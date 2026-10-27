---
name: retrospective-lesson
author: The-BlueCrow
slug: retrospective-lesson
version: 1.5.0
license: MIT
visibility: public
displayName: "回顾性总结/retrospective-lesson"
display_name: "回顾性总结/retrospective-lesson"
display_name_en: "Retrospective & Lesson Capture"
summary: "把一次有价值的技术对话，跑一遍 6 路并行分析 → 整合文档 → 写入持久记忆 → 归档分发的流水线，让经验从'存在于这次对话'变成'可被未来检索和继承'。"
description: |
  当用户想"复盘"——把刚解决的问题/对话变成可复用经验时触发。三个触发分支：
  ① 用户明说复盘/沉淀/总结/SOP/更新记忆；② 刚完成踩坑、架构决策等非平凡任务；③ 没明说但意图是把过程变成可复用的东西。
  Triggers: retrospective, lessons learned, post-mortem, update memory, form an SOP.
description_zh: "当用户想把刚解决的问题/对话变成可复用经验时触发：明说复盘/沉淀/总结/SOP，或刚完成踩坑、决策等非平凡任务。"
description_en: "Triggers when the user wants to turn a just-finished task or conversation into reusable knowledge: says retrospective/post-mortem/SOP, or just finished a non-trivial task worth keeping."
keywords:
  - 复盘
  - 经验沉淀
  - 知识管理
  - retrospective
  - lessons-learned
  - post-mortem
  - knowledge-capture
tags:
  - 知识管理
  - 工作流
  - agent-memory
metadata:
  author: user_ac889ddb
  modes:
    - interactive
---

# Retrospective Lesson（对话复盘与经验沉淀）

**复盘**——把刚完成的技术对话跑一遍"6 路分析 → 整合文档 → 写入记忆 → 归档分发"流水线，
让经验从"存在于这次对话"变成"可被未来检索和继承"的资产。全文围绕「复盘」展开：
判断是否值得**复盘** → 跑**复盘**流水线 → 检验**复盘**质量。

## 触发

`复盘` 或 `/retrospective-lesson`（自然语言如「沉淀/总结/记下来/SOP/更新记忆」也触发）。

**值得复盘的信号**（满足任一）：踩坑找到根因 / 做了非显然的决策 / 产出可复用命令脚本 / 发现工具非常规用法。
全不满足 → 问用户「这次要复盘吗」，别硬凑。

> 适用边界（图片对话/多人协作/超短对话等）和故障排查见包内文件 `references/troubleshooting.md`（同目录下的 references 文件夹，不是网页链接，请到 skill 目录中查看）。

---

## 复盘流程（4 阶段）

### 阶段 0.5：提炼复盘素材
主 agent 把对话压缩成 5 段（每段 ≤200 字）：需求 / 环境约束 / 执行步骤 / 坑（现象-因-解）/ 产出物。
> 不要把整段对话原文丢给后续 agent。

### 阶段一：复盘分析（按对话复杂度选档）

**先判断用哪一档**（根据对话轮数/踩坑数/产出量）：

| 档位 | 适用场景 | 怎么做 | 耗时 |
|------|---------|--------|------|
| **快档（轻量复盘）** | 对话 <8 轮、或只有 1-2 个点值得记 | 主 agent 自己跑 3 个核心维度：①理解问题 ②抽取解法 ④防复发；跳过文档互链/排版；不写记忆文件，只落盘一篇简短文档 | 快 |
| **全档（完整复盘）** | 对话较长、踩坑多、有架构决策、产出丰富 | 并行启动 6 个 subagent（见下表），不支持并行则串行，质量不变只是更慢 | 慢但全 |

> 拿不准选哪档？看踩坑数：≤2 个坑用快档，≥3 个坑或涉及架构决策用全档。用户明说「简单记一下」强制快档；明说「完整复盘」强制全档。

**全档 6 路分析表**：

| # | 维度 | 产出 | 字数 |
|---|------|------|------|
| 1 | 理解问题 | 核心诉求/显性隐性需求/约束/成功标准/归类 | ≤400 |
| 2 | 抽取解法 | 方法论/管用TOP5/陷阱TOP5/资产清单/一句话精髓 | ≤500 |
| 3 | 文档互链 | 引用关系/入口层级/skill关联/缺失文档/互链建议 | ≤400 |
| 4 | 防复发 | 逐坑检查项/通用原则/自动检查清单/早发现信号 | ≤500 |
| 5 | 分类标签 | YAML frontmatter（title/date/category/tags/...） | 仅YAML |
| 6 | 排版大纲 | 章节/呈现形式/开头结尾/字数建议 | ≤400 |

> **6 个 agent 的完整可复用 prompt 见包内文件 `references/prompts.md`（同目录下的 references 文件夹，直接复制填素材即可；不是网页链接，请到 skill 目录中查看）。**

**全档调用失败的自动保护**（解决 AI 服务不稳定）：

| 失败情形 | 自动处理 |
|---------|---------|
| 某 subagent 超时/限流/报错 | 重试 1 次；仍失败 → 主 agent 自己补跑该维度（用 prompts.md 对应模板，不再起 subagent） |
| 并行调用整体被拒/不可用 | 降级为串行（按表 1→6 逐个调） |
| 串行也频繁失败 | 降级为快档（主 agent 自己跑 ①②④ 三核心维度，其余跳过） |
| 重试都失败且用户在线 | 告知用户「N 路成功/M 路失败，是否用已有产出继续？」让用户定夺，不静默丢维度 |

> 核心原则：**任何单点失败都不应中断整个复盘**。已成功的维度产出要保留，失败的维度按上面顺序降级，最坏情况下主 agent 自己接手。

### 阶段二：整合复盘文档
头部贴 agent 5 的 frontmatter，正文按 agent 6 结构填 agent 1-4 内容。
形式原则：速查用表格、复用用代码块、验证用 checkbox、避免长段落。
落盘（三选一，不要同时写多处）：项目经验→`<project>/docs/lessons-learned/`；通用方法论→本 skill 的 `lessons-learned/`；简短规则→记忆文件。

### 阶段三：写入持久记忆
写入当前框架的记忆文件（Claude Code→`~/.claude/CLAUDE.md`；Cursor→`.cursorrules`；ZCode/其他→询问用户或用项目级 `AGENTS.md`）。
**写入前先把内容给用户确认**。只写可迁移规则（4 行模板）：

```
### <模式名>
- 触发场景：<什么情况适用>
- 核心做法：<一句话>
- 关键检查：<2-3 个必做动作>
- 详细文档：<链接>
```

**验证"学到了"**：下次用户提同类问题，记忆规则能让 agent 直接走对路吗？能→通过。

### 阶段四：归档分发（可选）
用户要求时，上传到外部知识库（IMA/Notion/Obsidian 等），调用对应 skill，按门类归类。

---

## 复盘质量检查清单

**内容完整性**（exhaustive 标准：每个 X 都要核对，不是"大致覆盖"）
- [ ] 档位选对：快档≥3核心维度 / 全档6维度都有产出
- [ ] 每个坑都有配对预防：逐条扫文档，每个「坑/陷阱」条目下方必有「解法/预防/检查项」（缺一即不通过）
- [ ] 一句话精髓能独立成立：遮住正文，仅凭这1句能否让没看过对话的人抓住核心（抓不住=不通过）

**文档规范**
- [ ] YAML frontmatter 含 title/date/category/tags 至少4项
- [ ] 形式合规：速查用表格、可复用用代码块、验证用 checkbox（全段落=不通过）
- [ ] 无残留 markdown 相对链接：`grep -nE '\]\(' SKILL.md` 对包内文件无命中

**记忆与归档**
- [ ] 记忆规则写入前已给用户看过并确认（未确认=不通过）
- [ ] 记忆规则通过"验证学到了"：下次同类问题，这条规则能否让 agent 走对路（不能=补充或改写）
- [ ] 只落盘了一处（项目docs / skill的lessons-learned / 记忆文件，三选一）
