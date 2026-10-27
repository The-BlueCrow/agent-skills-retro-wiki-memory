---
name: skill-library-ops
description: "Manage the three-library skill setup (runtime/source/底稿)."
version: 0.1.0
author: The-BlueCrow
license: MIT
platforms: [linux, macos]
tags: [skills, library, install, backup, sync]
---

# Skill Library Operations (Three-Library Workflow)

The user maintains **three skill libraries** with distinct roles; only the runtime one is scanned by the host. Every install, removal, or audit must touch all three correctly.

## The Three Libraries

| Layer | Path | Registered? | Role |
|---|---|---|---|
| **Runtime** | `<SKILLS_DIR>/<name>/` | YES (scanned at session start) | What this session actually loads |
| **Source (源库)** | `<SOURCE_DIR>/<bot>/`（每个工作位一格） | NO | Per-workspace low-frequency skills; copy back when needed |
| **底稿 (backup)** | `<BACKUP_DIR>/<name>/` | NO | Shared full mirror, "只进不出" — every skill ever seen, no reverse sync |

Source of truth for the rules: your source-library README (`<SOURCE_DIR>/README.md`). Treat that file as the contract; if it disagrees with this skill, the README wins and this skill needs patching.

## When to Use

- User says "装/删除/上架/下架/补一个技能", "查技能库", "核一下", "同步底稿库"
- Installing a skill from GitHub
- Reconciling README count vs actual filesystem count
- Auditing which skills are in which library

## Install Procedure (from GitHub)

1. **Locate the source repo**: Web search or `curl https://api.github.com/repos/<owner>/<repo>/git/trees/<branch>?recursive=1` to confirm the skill path actually exists upstream and list its files.
2. **Download via codeload** (on restrictive networks raw.githubusercontent.com often fails for large pulls; codeload tarballs and small api JSON usually work):
   ```bash
   curl -sL -o /tmp/<repo>.tar.gz 'https://codeload.github.com/<owner>/<repo>/tar.gz/refs/heads/<branch>'
   tar tzf /tmp/<repo>.tar.gz  # confirm the path is in the tarball
   ```
3. **DIFF before overwriting** the local SKILL.md (pitfall below). If local is a customized newer version, keep it; only copy missing `references/` and `scripts/`.
4. **Validate frontmatter format** before declaring install complete. The skill loader requires `name` and `description`; legacy Claude command-format fields (`argument-hint`, `user-invocable`) signal the file was authored for a different agent and needs rewriting, not just copying.
5. **Copy** to runtime: `cp -a <extracted>/<skill>/<missing-pieces> <SKILLS_DIR>/<skill>/`
6. **Sync to 底稿**: `rm -rf <BACKUP_DIR>/<skill> && cp -a <SKILLS_DIR>/<skill> <BACKUP_DIR>/<skill>` (rm-first because `cp -a` to an existing dir nests under it).
7. **List which bot libraries get this skill** before syncing — see Multi-Bot Sync below. Never assume the current bot's runtime is the only destination.
8. **Update README** if the install is a notable event (new entry, count change). README is the audit log; do not skip this.
9. **Test the skill works** if it has scripts (e.g. `--help`, a smoke test). Document the result.
10. **Tell the user** to open a new session — runtime registry is cached at session start, the new skill is invisible until then.

## Multi-Bot Sync

A host may run more than one workspace profile; "installed in the current workspace" is not the same as "installed everywhere". Default sync targets for a new skill:

| Layer | Where it lives | Sync rule |
|---|---|---|
| Runtime | `<other-workspace-skills>/<bot>/` | Only if the user asks for this bot to use it, OR the skill is bot-agnostic and the user wants it active now |
| Source (源库) | `<SOURCE_DIR>/<bot>/<skill>/` | Always sync, so every bot has the same starting point in its low-frequency shelf |
| 底稿 (backup) | `<BACKUP_DIR>/<skill>/` | Always sync, single canonical copy |

Decision rule when unsure: default to **runtime of the workspace asking + 源库 for every workspace that has one + 底稿**. Never put a skill in a 源库格 just to mirror a runtime that already has it — 源库 is for skills *not* in that bot's runtime (per the README's only-in rule). If unsure which workspaces exist: `ls <workspace-roots>`.

## Audit / Reconcile Procedure

When the user says "核一下" or you suspect a count mismatch (README says N, but you counted M):

- **Count by `*/SKILL.md` recursively**, not by top-level directory. Umbrella directories (e.g. `music/`) hold nested skills in subdirs; `@user`-prefixed subdirs hold one skill each. The README is the *correct* number, not your gut.
- Three numbers to compare: README claim, top-level dir count, recursive `*/SKILL.md` count. They should all match. If not, find the class of exception (umbrella, prefix, missing entry) and report.

```bash
# recursive count
find <lib>/<skill-name> -name 'SKILL.md' | wc -l
# top-level (if each dir IS a skill)
ls -1 <lib>/ | grep -v '^\.' | wc -l
```

## Removal Procedure

1. `rm -rf <SKILLS_DIR>/<skill>` (runtime)
2. **底稿保留** (only-in no-out). Do NOT remove from `<BACKUP_DIR>/`.
3. If the skill was in source library, also `rm -rf <SOURCE_DIR>/<bot>/<skill>`.
4. Update README count + the source library's archived-skills index pointer (e.g. `ARCHIVED.md`) if relevant.
5. Verify no cronjob / config still references the removed skill: `global content search / `grep -rn '<skill>' <host-config-tree>``.

## Pitfalls

1. **DIFF the local SKILL.md before overwriting from upstream.** The user's copy is often a *newer customized version* than the upstream repo (e.g. local had a routing table the upstream lacked). Blind `cp -a` will regress it. Always `diff` first; if local is richer, keep local and only copy the missing `references/` + `scripts/`.
2. **Never claim a skill is "无模型绑定" without reading the SKILL.md body and grepping for the model name.** Metadata/description is not enough. Skills named "prompt-engineering" can be Claude-specific; skills named "general-llm" can be GPT-specific. The body and references are the truth.
3. **"Not registered" does not mean "broken" or "absent".** Source and 底稿 libraries are deliberately unregistered to save tokens. They work fine; you just have to `cp` them back into runtime before opening a new session. Don't waste a turn re-explaining this to the user — and don't tell the user "the skill is missing" when it's sitting in 底稿.
4. **Count skills the way the README counts them.** Recursive `*/SKILL.md` is the safe metric; top-level `ls | wc -l` is wrong when umbrella dirs and `@user`-prefixed subdirs are in play. When the two numbers disagree, find the class of exception; don't patch one toward the other.

   Diagnostic commands when README ≠ reality:
   ```bash
   # 1. recursive SKILL.md (truth, when each leaf IS a skill)
   find <lib> -mindepth 2 -name SKILL.md | wc -l
   # 2. top-level entries (truth, when each top dir IS a skill)
   ls -1 <lib>/ | grep -v '^\.' | wc -l
   # 3. diff: which top-level dirs have NO SKILL.md? (umbrellas)
   comm -23 <(ls -1 <lib>/ | grep -v '^\.' | sort) \
            <(find <lib> -mindepth 2 -name SKILL.md -exec dirname {} \; | xargs -n1 basename | sort)
   # 4. diff: which top-level dirs are MISSING? (gaps)
   comm -13 <(ls -1 <lib>/ | grep -v '^\.' | sort) <(list-from-README)
   ```
   The README's number is the contract; if reality doesn't match, update either reality or the README — but never silently change the comparison method to hide the gap.
5. **`cp -a src/. dst/` (with `/.`) copies contents, but `cp -a src dst/` (no slash) creates `dst/src/`.** The user's standard pattern is `rm -rf dst && cp -a src dst` (rm-first to guarantee a clean mirror). Don't get clever with trailing slashes.
5a. **下架/取回一个技能后，核对"是否真离开运行时"必须查宿主的技能清单视图，不只是 find 顶层目录**（2026-10-09 实踩）：`find -name SKILL.md` 只看文件，**技能清单还会把嵌套子目录（如样例生成类技能的 `<generator>/examples/<name>/`）里的副本当独立技能挂出**（顶层目录已删、子目录副本还在 = 仍被触发）。子副本留存的常见来源是样例生成类技能的子目录（`<generator>/examples/`）、旧版本沉留（`...bak*/...`）、agent 自己的子目录。私下架必查清单：
   ```bash
   # 1. 顶层目录全无？
   ls -1 <lib> | grep -c '^<name>$'
   # 2. 任意深度 SKILL.md 副本全无？（包括 nuwa-skill/examples、autonomous-ai-agents/* 这种嵌套）
   find <lib> -name SKILL.md -path '*<name>*' | wc -l
   # 3. 技能清单里是否还挂这个名字？（递归深、含嵌套）
   # 技能清单工具返回的 count 也要对——能查到名字就还会被触发
   ```
   三者**全 0** 才算真正下架；只删顶层目录但 `nuwa-skill/examples/` 留副本 = 表面上"已下架"实际还在跑。同步 ARCHIVED.md 的 `技能列表 N → M` 时 N/M 都要现查技能清单，不凭对话印象写。
5b. **三方盘点时双向差集都要查**（2026-10-09 校对发现）：README/索引数字与实测不符时，两个方向都要查——「README 说有但磁盘无」（漏建、漏同步、错迁）和「磁盘有但 README 没说」（漏记、新装、嵌套副本）。单看「差几个」会漏方向；统一先 `comm -12` 找交集、`comm -13`/`comm -23` 找两个方向的差集各列一份。诊断命令块加这两条：
   ```bash
   # A. 索引声明 ∩ 磁盘实际（交集 = 一致）
   comm -12 <(索引里逐个抽名字 | sort) <(find <lib> -name SKILL.md ... | sort)
   # B. 索引里说但磁盘里没有（声明多余）
   comm -13 <(索引里逐个抽名字 | sort) <(find <lib> ... | sort)
   # C. 磁盘里有但索引没说（漏记）
   comm -23 <(索引里逐个抽名字 | sort) <(find <lib> ... | sort)
   ```
5c. **多工作位盘点「每个工作位的运行时 vs 自己的源库格」必须各自做交集**（2026-10-09 校对发现）：某 bot archived-skills 索引 32 行 32 目录对得上，但「下架条目」里 10 个同时还在那个工作位的运行时（4 个只存 DESCRIPTION.md 目录、6 个 md5 与源库一致的完整副本）——**索引表 32 行 = 索引行数对，但"下架意图"和"运行时实际"是两件事**。每个 bot 都要单独跑：
   ```bash
   for bot in <bots>; do
     idx="<bot> archived-skills/SKILL.md 里的各表行"
     rt="$(bot 运行时 skills/ 顶层)"
     comm -12 <(echo "$idx" | sort -u) <(echo "$rt" | sort -u)
   done
   ```
   「已下架」`仅在源库 ≠ 真已下架`；只有 `运行时 ∩ 源库 = ∅` 才算下架意图真正落地。
6. **The session's skill registry is cached at startup.** After `cp -a` to runtime, the new skill is invisible until a fresh session starts. This is the expected behavior, not a bug. Tell the user to open a new session to use the newly installed skills — don't try to "reload" it.
7. **Use codeload, not raw.githubusercontent.com** for tarball downloads on restrictive networks (api is fine for small JSON like tree listings; tarball pulls via raw often fail).
8. **A third-party skill finder's local index may describe skills in a foreign language** (e.g. Japanese). Chinese keyword searches miss; use English words or `#tag` filters. The GitHub fallback search is the safety net.
9. **A skill whose frontmatter uses slash-command fields (`argument-hint`, `user-invocable`, `$ARGUMENTS`) is not standard format** — it was authored for a chat UI's command interface. The loader will register it but the descriptions and triggers are misleading. Detect by greping the SKILL.md body for those fields, then rewrite to standard format (`name`, `description`, `version`, `author`, `license`, `tags`) before declaring install complete. Don't ship it under a "looks like a skill" assumption.
10. **Don't assume a skill only needs syncing to the current workspace.** Multi-workspace hosts (any host with other-workspace skill roots) have separate runtimes and 源库格; a "completed install" report that omits the other workspaces' state is incomplete. List every workspace's runtime + 源库格 before reporting done.

## Verification

- [ ] Diff done before any SKILL.md overwrite
- [ ] Runtime, 源库, 底稿 all updated per their rules
- [ ] README reflects the change
- [ ] No cronjob / config still references removed skills
- [ ] User told to open a new session to use newly installed skills
