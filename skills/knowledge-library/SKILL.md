---
name: knowledge-library
description: "Use when checking or filling the local knowledge library."
version: 1.1.0
author: The-BlueCrow
license: MIT
tags: [knowledge, skills-library, experience, memory, audit]
    related_skills: [skill-library-ops, skill-finder]
---

# 本机知识库：盘点与回流

## When to Use

- 「知识库现在什么情况」「技能库/经验库有多少」「主库和镜像同步吗」
- 「要不要回流」「装完技能之后该做什么」
- 「这个仓库/资料能装吗，装进知识库」（外部资料装库，流程见下）
- 要判断某条经验/教训该落到哪一处时（分工表见下）

本机有多处知识存放，各有分工；只读盘点直接跑，输出一张带数字的清单。
总入口和写入规范是记忆库入口 README（`<MEMORY_DIR>/README.md`，内含 Append SOP，先读它，别凭记忆复述分工表）。

**子文件指引**：`references/lessons-merge-sop.md` — 教训库合并规则（何时合/不该合、合并 5 步流程、3 项验收断言、副本验证、有据事故实录、与 Append SOP 分工）。

| 存放 | 内容 | 谁写 |
|---|---|---|
| `<SKILLS_DIR>/` | 运行时技能库（真正被加载的） | 技能安装/创建 |
| `<SOURCE_DIR>/<bot>/` | 源库：各工作位低频技能，其 README 是三层规矩**唯一事实源** | 下架/取回 |
| `~/skills-library/` | 底稿库：全服共同备份，**只进不出** + README | 装完/下架后 `cp -a` 回流 |
| `~/experience/` | 经验条目（按主题分文件）+ README | 经验沉淀 |
| `<MEMORY_DIR>/` | 深层记忆（教训/服务器笔记/排障）+ NOTICE | 长期记忆清理 |
| `<CRON_DIR>`（定时任务目录，如有） | 定时任务与产出 | cron |

## 盘点（只读，直接跑）

```bash
# 镜像规模：目录数 / SKILL.md 数 / 体积
ls -d ~/skills-library/*/ | wc -l; find ~/skills-library -name SKILL.md | wc -l; du -sh ~/skills-library
# 各运行时树对底稿库的缺口（按技能名 basename 比对，0 = 对齐；无 rsync 时用 python）
python3 - <<'PY'
import os, glob
names=lambda r:{os.path.basename(d) for d,_,f in os.walk(r) if 'SKILL.md' in f}
lib=names(os.path.expanduser(os.environ.get('BACKUP_DIR','~/skills-library')))
runtimes=[os.path.expanduser(os.environ.get('SKILLS_DIR','~/.agents/skills'))]
runtimes+=glob.glob(os.path.expanduser(os.environ.get('SOURCE_DIR','~/.agents-source'))+'/*/skills')
for p in runtimes:
    x=names(p); print(p, len(x), '缺:', sorted(x-lib) or '0')
PY
# 各库说明文件是否在
ls -la <MEMORY_DIR>/README.md ~/experience/README.md ~/skills-library/README.md
# 各库条目量（行数即内容量）
wc -l <MEMORY_DIR>/*.md ~/experience/*.md
# 泄密检查：镜像里不该有 .env / 密钥
find ~/skills-library -name '.env*' -o -name '*.key'
```

交付：数量 + 同步差异 + 有无泄密文件，逐项打勾；不要只报一个总数。
再把本次数字与上次会话/记录里的数字对比——差值为 0 说明没人动过，差值正好等于新装技能数则直接证明回流生效，这句结论比单次快照有用。

## 回流（写操作 → 先列清单获批）

装完/改完技能后把主库镜像进底稿（无 rsync 用 cp）：
`cp -a <SKILLS_DIR>/. ~/skills-library/`
只补缺口时逐个 `cp -a <SKILLS_DIR>/<技能名> ~/skills-library/`（分类技能连分类目录一起复制）。
回流后：1) 重跑上面的缺口检查全为 0；2) 更新 `~/skills-library/README.md` 顶部统计行
（顶层目录数 / SKILL.md 数 / 体积，新装的资料也写进去）——统计行过期会让下次盘点拿错基线。

## 下架归档（运行时 → 底稿库；写操作 → 先列清单获批）

用户说「这个不要了 / 丢到底库去 / 搬去底库」时走这条，**顺序不能乱**：

1. **先定位源**：`find <宿主根目录> -name SKILL.md -path '*<名字>*'` 确认它在哪棵树。
   源可能在**其他工作位的技能目录**（`<其他工作位技能根>/<技能>/`，如宿主支持多工作位/多账号），
   不一定在当前运行时——找不到就先全盘搜，别只查自己的主库。
2. **列清单获批**：报源路径、目标路径、将删什么、索引留哪。底稿库是「只进不出」的共同备份，
   搬进去不动其他树，属写操作，必须批。
3. **复制**：`cp -a <源技能目录> ~/skills-library/<技能名>/` —— 整夹搬，references/scripts 一起带。
4. **核对零差异才准删**：`diff -rq <源> ~/skills-library/<技能名>` 必须无输出，`md5sum` 两边一致、
   文件数一致；再跑泄密检查（`find <目标> -name '.env*' -o -name '*.key'`）。
5. **下架**：`rm -rf <源目录>`，随后 `ls` 父目录确认只剩同类技能。
6. **原处留索引**：在该技能所在的**分类目录**下写 `ARCHIVED.md`（不是 SKILL.md —— 用 SKILL.md 当索引
   仍会被加载，白占常驻 token），一行一条：技能名 / 下架日期 / 底稿位置 / 一句话理由 / **取回命令写全路径**。
   同级已有 ARCHIVED.md 就追加，不新建第二份。
7. **更新 `~/skills-library/README.md`**：顶部追加一行日期条目（来源路径、md5、核对结论、留了什么索引、
   更新后的统计数），统计三项**实测**：`ls -d ~/skills-library/*/ | wc -l`、`find ~/skills-library -name SKILL.md | wc -l`、`du -sh ~/skills-library`。

**同族技能（原版 vs 精简版）共存**：定下哪一版当日常规矩后，另一版整夹下架归档——两版都留在运行时，
没人读的那版就是纯常驻 token 开销。区分方式看是否只是删节：精简版是独立技能名（如 `X-slim`）时，两者各留一份即可，
搬的是被弃用的那个。

## 长期记忆清理（写操作 → 先获批；用户说「清理记忆 / 有用的放深层记忆」即批准了搬运）

1. **先搬后删**：挑出占字数但低频的长条目（网关/端口/网络通道类环境细节最典型），浓缩追加进
   `<MEMORY_DIR>/server-notes.md` 对应小节（没有就新建小节，一事一条、带日期）。
2. 记忆里原条目**整条**替换成一行指针（「细节已迁 server-notes.md + 关键词」），绝不留半截。
3. 分类：环境/操作事实进 memory，用户长期规矩进 user 画像（新规矩当场入库，不必再问）。
4. 收尾报 usage 前后百分比、搬了几条、指针去向。
5. 记忆库只新增小节/文件才改 README 索引行，改已有内容不用。

## 外部资料装库（GitHub 仓库 / 网页 → 本机知识库）

1. **核实（只读，先做）**：`curl -s https://api.github.com/repos/<owner>/<repo>` 取
   size(KB)/default_branch/license/pushed_at；README 用网页抓取工具读。
   `git ls-remote` 直连 github.com:443 在部分网络环境下会超时——那是网络，不是仓库不存在，别据此下结论。
2. **取包**：`curl -L -o x.tar.gz https://codeload.github.com/<owner>/<repo>/tar.gz/refs/heads/<branch>`
   （受限网络下 api.github.com / codeload.github.com 通常可达；github.com 与 raw.githubusercontent.com 常超时）。
3. **体检**：解压到 scratch，`du -sh`、`find -name '*.md' | wc -l`、按扩展名统计，判断它是
   技能（有符合标准的 SKILL.md：name/description 齐全、步骤可执行）还是课程/文档资料（只有说明性文档、无可执行流程的也算资料）。
4. **列方案获批**：整包落盘 / 精简（去网页工程 site+api+assets）/ 只在 README 记链接索引，
   编号成清单让用户选，批准后才写正式目录。资料类落 `~/skills-library/<repo>/`，
   **不要**塞进 `<SKILLS_DIR>/`（不是技能，白占常驻 token）。
5. **核验**：`diff -rq <scratch源> <落盘目标>` 必须零输出（文件数也要一致），再跑上面的泄密检查；
   资料类只进底稿库，不涉及主库回流。数字（体积/文件数）以核验后的实测为准报，不用预估值。

## Pitfalls

- **别只数一个来源**：主库和镜像是两棵树，只报一边的数字会让用户以为不同步；技能数用 `find -name SKILL.md` 而不是目录数（一个目录可能没有或多份 SKILL.md）。
- **本技能只管本机文件系统上的知识存放**，外部在线知识库是另一套系统，别混为一谈。
- **回流 / 改文件 / 删条目是写操作**，先列清单获批；盘点是只读，直接跑。
- **记忆写入若整批 all-or-nothing，超限则整批拒**：先 `len()` 算净增删、或同批附带压缩操作腾位再提交，否则会连续空跑。
- **凭据不入库**：发现 `.env` / key 混进镜像属异常，先报告再等指示，不要自行删除。
- **缺口按技能名（basename）比对，不按 relpath**：底稿库含分类子目录（如 `devops/x`），路径对不上会误报缺口；
  且要查**全部**运行时树——只查自己的主库会漏掉其他 profile 的新技能，它就永远不会回流。
- **统计数一律实测，别沿用旧基线**：README 统计行的目录数 / 技能数 / 体积每次都要跑命令取数（下架、新增都会变），
  报「本次 vs 上次」的差值比单次快照有用；用预估值或上一条日期里的数字会让下次盘点拿错基线。
- **未登记的 profile 别擅自补格子**：三层结构只登记已注册的运行时；源技能若来自第三方 profile 目录，
  按用户当次指示落底稿库即可，**不要**自行往 `<SOURCE_DIR>/<bot>/` 加格、也不要改三层规矩 README——那是用户的规矩，改动要单独获批。
- **下架前查引用与进程**：`ps -eo pid,cmd | grep -i <宿主进程名>` 看该工作位有没有独立会话在跑，
  另查 cron / 其他技能有没有引用这个技能；活跃 bot 正在用的技能不能静默下架。
