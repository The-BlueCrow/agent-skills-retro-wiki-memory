# 复盘 · Wiki · 经验 · 记忆 —— 通用智能体技能合集

一套跑在长期记忆上的知识管理流水线：**踩坑 → 复盘四连 → 教训/经验/wiki 分流入库 → 记忆瘦身**。

本合集不绑定任何框架：技能采用 Agent Skills 开放标准（目录内一个 `SKILL.md` + YAML frontmatter，必填 `name` 与 `description`），任何支持该标准、能读 markdown、能执行 bash/python 的智能体都能直接用。脚本全部纯标准库，零账号、零 API 依赖。

## 一分钟上手

1. 把 `skills/` 里想要的技能**整个目录**拷进你所在运行时的技能根目录（各运行时惯例不同，形如 `~/<宿主>/skills/`、`.agents/skills/` 等，按所用运行时的文档放置即可；技能名无需改动，均为合法 kebab-case）。
2. 对智能体说「复盘一下」——retrospective-ops 会自动加载，按四连 + 八校对收尾。
3. 首次使用 wiki 类技能前，按技能内说明初始化一个 wiki 目录（`WIKI_PATH`，默认 `~/wiki`）。
4. 脚本直接 `bash` / `python3` 可跑，无需安装任何依赖。

## 通用约定（先读这段）

- **占位符**：技能正文里的路径一律为占位符，按你的环境取值——
  `<SKILLS_DIR>` = 技能根目录；`<MEMORY_DIR>` = 长期记忆/深层经验目录；`<SOURCE_DIR>` = 低频技能源库（可选）；`<BACKUP_DIR>` = 技能底稿备份库（可选）；`WIKI_PATH` = wiki 目录。
- **能力名**：正文用能力而非某家工具名——「全文文件搜索」「网页抓取」「联网搜索」「记忆文件」等，对应你宿主自己的工具，按等效能力替换即可。

## 为什么需要这套东西

见 [优势说明.md](./优势说明.md)：同一个模型，装与不装的逐条对照。

## 技能一览（11 个）

| 技能 | 干什么 | 依赖 |
|---|---|---|
| **retrospective-ops** | 复盘主流程：四连（lessons/技能/wiki/commit）+ 八校对 + 硬门槛 | references/ 准则全文（已附） |
| **llm-wiki-slim** | LLM Wiki：投喂、查询、体检 | scripts/wiki-lint.py、wiki_search.py（已附，纯 stdlib） |
| **knowledge-library** | 知识库存量盘点、回流、下架归档 | 无（约定目录） |
| **agent-memory-opt** | 长期记忆审计与瘦身（四步法） | 无 |
| **minnow-token-efficiency** | 省 token：小读、批调用、防上下文膨胀 | 无 |
| **skill-library-ops** | 技能库三库分层（运行时/源库/底稿）安装运维 | 无 |
| **experienceaccumulator** | 经验累积器：安全写入 + 队列校验 + 报错捕获 + 晋升技能 | scripts/ 六件套（已附） |
| **experience-triage** | 一次纠错向哪分流：规则/经验/教训/wiki/技能 | 无 |
| **retrospective-lesson** | 教训（lessons）的写作格式与查重 | 无 |
| **ai-retrospective-skill** | 独立的四阶段复盘流程（另一套方法论，可作对照） | 无 |
| **llm-wiki** | LLM Wiki 原版（llm-wiki-slim 的源头，可对照精简版） | 无 |

## 推荐流水线

```
踩坑/纠错发生
  → retrospective-ops（复盘六步）
      ① 教训   → <MEMORY_DIR>/lessons-learned.md   （格式见 retrospective-lesson）
      ② 技能   → 对应 SKILL.md 补规则
      ③ wiki   → llm-wiki-slim（ingest 三连 + lint）
      ④ commit → 本地知识仓一笔提交
  → experience-triage（分流拿不准时的路由器）
  → 经验沉淀   → experienceaccumulator（队列+激活）
  → 记忆臃肿   → agent-memory-opt（瘦身）
  → 上下文浪费 → minnow-token-efficiency（省 token）
```

## 目录结构

```
README.md      ← 本文件（全局教程）
依赖说明.md     ← 逐技能依赖与部署提示
优势说明.md     ← 有这套 vs 没这套的逐条对照
skills/
  <技能名>/     ← 每个技能独立目录，自带 references/ 与 scripts/
```

## 凭据与安全

本合集不含任何账号、密钥、token。部署到你自己的环境后，写入你的记忆库/经验库前照常做凭据扫描。
