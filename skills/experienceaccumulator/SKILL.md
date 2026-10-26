---
name: experience-accumulator
version: 1.0.0
description: "经验累积器 — 自动沉淀踩坑经验、错误日志、功能需求，识别重复模式，晋升全局规范，支持 SkillHub CLI 一键安装。内置容错保护、环境校验、安全写入。触发场景：需要记录学习经验、追踪错误日志、管理功能需求、沉淀团队规范。"
author: 团子 🦐
license: MIT
tags:
  - self-improvement
  - experience
  - logging
  - knowledge-management
  - skill-management
  - openclaw
  - claude
  - skillhub
compatibility: OpenClaw, Claude Code, Codex CLI, GitHub Copilot
---

# 📦 Experience Accumulator — 经验累积器

> **把每次犯错、每次学习、每次优化都攒起来。**
> 自动记录 → 识别模式 → 沉淀经验 → 晋升规范 → 提取技能

---

## ⚙️ 元数据

| 字段 | 值 |
|------|------|
| skill_name | 经验累积器 |
| skill_id | experience_accumulator_v1 |
| skill_type | 自我改进 / 经验沉淀 / 日志管理 |
| auto_trigger | true |
| trigger_keywords | 记录经验、沉淀知识、错误日志、功能需求、复盘、晋升规范 |
| skill_mode | 自动记录 + 定期复盘 |

---

## 🎯 功能边界定义

> **明确知道该干什么、不该干什么，避免功能模糊。**

### ✅ 该做（In Scope）

| 能力 | 说明 |
|------|------|
| 日志模板管理 | 创建/维护三套标准日志模板 |
| 日志写入 | 自动识别场景并写入对应日志文件 |
| 重复模式识别 | 基于 Pattern-Key 检索、计数、关联 |
| 经验晋升 | 将日志精简后写入全局配置文档 |
| 周期性复盘 | 统计、排序、标记状态 |
| 技能提取 | 将高频经验固化为独立 SKILL.md |
| CLI 安装管理 | SkillHub CLI 安装/更新/卸载 |

### ❌ 不该做（Out of Scope）

| 排除项 | 原因 |
|--------|------|
| 自动执行修复脚本 | 只提供 Suggested Fix，不自动执行 |
| 自动修改全局配置文档 | 晋升需用户确认后执行 |
| 自动创建钩子脚本 | 只提供配置示例，脚本需用户自行实现 |
| 自动推送通知 | 不提供钉钉/飞书/邮件推送 |
| 自动清理过期日志 | 仅提示，不自动删除 |
| 数据分析仪表盘 | 仅提供 grep 查询命令 |

---

## 🔒 核心原则

1. **问题发生立刻记录**：保留完整上下文，不拖延
2. **日志描述精准**：报错必须附带复现步骤
3. **通用经验尽早晋升**：不要堆积日志，及时写入全局配置
4. **定期复盘清理**：避免日志臃肿
5. **强制脱敏**：禁止记录密钥、Token、私钥、完整源码

---

## 📂 目录结构

### OpenClaw 工作区

```
~/.openclaw/workspace/
├── AGENTS.md           # 多代理、自动化工作流规范
├── SOUL.md             # AI行为准则、输出风格
├── TOOLS.md            # 工具使用踩坑、集成异常
├── MEMORY.md           # 全局长期记忆
├── memory/             # 按日期分片记忆文件
└── .learnings/         # 经验日志根目录
    ├── LEARNINGS.md    # 学习记录（修正/洞察/知识盲区/最佳实践）
    ├── ERRORS.md       # 错误日志（命令异常/接口故障/集成问题）
    └── FEATURE_REQUESTS.md  # 功能需求（用户新增能力诉求）
```

### 通用项目工作区

```
<project>/
├── .learnings/
│   ├── LEARNINGS.md
│   ├── ERRORS.md
│   └── FEATURE_REQUESTS.md
├── AGENTS.md / CLAUDE.md / .github/copilot-instructions.md  # 全局规范
└── .gitignore
```

---

## 🚀 首次初始化

进入任意工作区/项目，自动校验并生成日志目录文件（**禁止覆盖已有内容**）：

```bash
mkdir -p .learnings

# 生成学习记录
[ -f .learnings/LEARNINGS.md ] || printf "# Learnings\n\n修正、开发洞察、知识盲区沉淀\n分类：correction | insight | knowledge_gap | best_practice\n\n---\n" > .learnings/LEARNINGS.md

# 生成错误日志
[ -f .learnings/ERRORS.md ] || printf "# Errors\n\n命令异常、接口/第三方集成故障记录\n\n---\n" > .learnings/ERRORS.md

# 生成功能需求日志
[ -f .learnings/FEATURE_REQUESTS.md ] || printf "# Feature Requests\n\n用户提出的新增能力诉求\n\n---\n" > .learnings/FEATURE_REQUESTS.md
```

---

## 📝 日志编号规则

**格式：`类型-年月日-三位标识`**

| 类型 | 前缀 | 示例 |
|------|------|------|
| 学习记录 | LRN | `LRN-20260701-001` |
| 错误日志 | ERR | `ERR-20260701-A7B` |
| 功能需求 | FEAT | `FEAT-20260701-001` |

---

## 🔄 日志分流匹配规则

| 触发场景 | 写入文件 | 附加标记 |
|---------|---------|---------|
| Shell/工具/API 调用失败、超时、异常堆栈 | ERRORS.md | 补充集成环境信息 |
| 用户纠正回答、原有知识过时 | LEARNINGS.md | `category=correction` / `knowledge_gap` |
| 优化开发流程、通用优质规范 | LEARNINGS.md | `category=best_practice` |
| 用户提出新增功能、缺失能力 | FEATURE_REQUESTS.md | — |
| 重复高频代码/流程模式 | LEARNINGS.md | `Source:simplify-and-harden` + `Pattern-Key` |
| 存在历史同类日志 | 元数据添加 `See Also` | 重复问题提升优先级 |
| 跨项目通用经验 | 晋升至全局配置文档 | 修改日志状态为 `promoted` |

---

## 📋 日志标准模板

### 1. LEARNINGS.md — 学习条目

```markdown
## [LRN-YYYYMMDD-XXX] category
**Logged**: ISO-8601时间戳
**Priority**: low | medium | high | critical
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
一句话总结本次经验

### Details
完整上下文：问题、错误点、正确方案

### Suggested Action
可落地优化措施

### Metadata
- Source: conversation | error | user_feedback
- Related Files: 文件路径
- Tags: 标签1,标签2
- See Also: 关联日志ID
- Pattern-Key: 重复模式唯一标识(可选)
- Recurrence-Count: 重复次数(可选)
- First-Seen / Last-Seen: 首次/末次出现日期(可选)
---
```

### 2. ERRORS.md — 错误条目

```markdown
## [ERR-YYYYMMDD-XXX] 工具/命令名
**Logged**: ISO-8601时间戳
**Priority**: high
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
故障简短描述

### Error
原始报错信息

### Context
执行命令、入参、环境、脱敏输出摘要

### Suggested Fix
可行修复方案

### Metadata
- Reproducible: yes/no/unknown
- Related Files: 文件路径
- See Also: 同类错误日志ID
---
```

### 3. FEATURE_REQUESTS.md — 功能需求条目

```markdown
## [FEAT-YYYYMMDD-XXX] 能力名称
**Logged**: ISO-8601时间戳
**Priority**: medium
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Requested Capability
用户想要实现的功能

### User Context
业务场景、待解决痛点

### Complexity Estimate
simple | medium | complex

### Suggested Implementation
实现思路、扩展方向

### Metadata
- Frequency: first_time | recurring
- Related Features: 关联已有功能
---
```

---

## 📊 日志状态全集

| 状态 | 说明 |
|------|------|
| `pending` | 新建待处理（默认） |
| `in_progress` | 正在处理 |
| `resolved` | 已修复，补充 Resolution 块 |
| `wont_fix` | 不予处理，备注拒绝原因 |
| `promoted` | 晋升至全局规则文档 |
| `promoted_to_skill` | 提炼为独立可复用技能 |

### resolved 补充格式

```markdown
### Resolution
- Resolved: 完成时间戳
- Commit/PR: 提交编号
- Notes: 处理说明
```

---

## ⬆️ 经验晋升（Promote）规范

### 晋升触发条件

满足以下任一条件即可晋升：

1. 经验适用于多模块、全项目通用
2. 所有开发者/AI 必须掌握
3. 能够规避重复踩坑
4. 属于项目统一标准规范

### 晋升对应目标文档

| 经验类型 | 写入文件 |
|---------|---------|
| 代理自动化、多任务流程 | AGENTS.md |
| AI输出行为、对话风格 | SOUL.md |
| 工具使用踩坑、集成异常 | TOOLS.md |
| 项目通用规范、业务常识 | CLAUDE.md / copilot-instructions.md |

### 晋升操作流程

1. 将冗长日志精简为简短可执行规则，删除冗余上下文
2. 写入对应全局文档（文件不存在自动创建）
3. 修改原日志 `Status=promoted`，新增 `Promoted: 文档名`

---

## 🔍 重复模式自动识别

### 识别逻辑

```
1. 新增日志前执行检索匹配同类条目
   grep -n "Pattern-Key: 目标key" .learnings/LEARNINGS.md

2. 匹配到：
   - 自增 Recurrence-Count
   - 更新 Last-Seen
   - 添加 See Also 关联

3. 无匹配：
   - 新建 LRN 记录
   - 标记 Source:simplify-and-harden
```

### 自动晋升判定（全部满足则强制晋升）

| 条件 | 阈值 |
|------|------|
| Recurrence-Count | ≥ 3 |
| 不同任务出现次数 | ≥ 2 |
| 30 天内触发次数 | ≥ 2 |

**晋升内容只写前置预防简短规则，不粘贴完整事故记录。**

---

## 🔄 周期性复盘

### 复盘触发时机

- 新项目启动
- 功能迭代完成
- 处理同类业务
- 每周固定复盘

### 快速查询脚本

```bash
# 统计全部待处理日志
grep -h "Status: pending" .learnings/*.md | wc -l

# 列出高优先级待处理条目
grep -B5 "Priority: high" .learnings/*.md | grep "^## \["

# 筛选指定领域日志（示例：backend）
grep -l "Area: backend" .learnings/*.md

# 统计重复模式
grep -h "Recurrence-Count:" .learnings/LEARNINGS.md | sort | uniq -c | sort -rn
```

### 复盘执行动作

1. 标记已解决日志为 `resolved`
2. 通用经验执行晋升
3. 同类日志互相添加关联 `See Also`
4. 高频重复问题升级技术债务或自动化脚本

---

## 🚨 优先级分级标准

| 级别 | 说明 |
|------|------|
| **critical** | 阻断核心业务、存在数据丢失、安全漏洞 |
| **high** | 高频流程严重受阻、持续重复复现 |
| **medium** | 存在临时替代方案，影响程度一般 |
| **low** | 边缘场景轻微体验瑕疵、优化类需求 |

---

## 📦 Gitignore 三种管理方案

### 方案1：本地私有（推荐）

```gitignore
.learnings/
```

### 方案2：团队共享沉淀

删除 `.gitignore` 内 `.learnings` 配置，全团队共用日志

### 方案3：混合模式（仅保留模板，忽略日志条目）

```gitignore
.learnings/*.md
!.learnings/.gitkeep
```

---

## ⚡ SkillHub CLI 安装流程

### 前置校验（自动容错）

在安装技能前，自动执行以下校验，确保环境就绪：

```bash
#!/bin/bash
# preflight-check.sh — 安装前环境校验

set -e

# 1. 检查 CLI 是否安装
if ! command -v skillhub &> /dev/null; then
    echo "❌ skillhub CLI 未安装，请先执行安装脚本"
    echo "   curl -fsSL https://skillhub.cn/install/install.sh | bash -s -- --cli-only"
    exit 1
fi

# 2. 检查目标目录是否存在
TARGET_DIR="${1:-$HOME/.openclaw/skills}"
if [ ! -d "$TARGET_DIR" ]; then
    echo "⚠️  目标目录不存在，自动创建: $TARGET_DIR"
    mkdir -p "$TARGET_DIR"
fi

# 3. 检查磁盘空间（至少 10MB）
AVAILABLE_SPACE=$(df -m "$TARGET_DIR" | awk 'NR==2{print $4}')
if [ "$AVAILABLE_SPACE" -lt 10 ]; then
    echo "❌ 磁盘空间不足（${AVAILABLE_SPACE}MB），至少需要 10MB"
    exit 1
fi

# 4. 检查网络连接
if ! curl -s --connect-timeout 5 https://skillhub.cn > /dev/null 2>&1; then
    echo "⚠️  无法连接到 skillhub.cn，请检查网络或切换国内源"
    echo "   export SKILLHUB_REGISTRY=https://skillhub.cn"
fi

echo "✅ 环境校验通过"
```

**使用方式：**
```bash
# 安装前校验
bash ./skills/experience-accumulator/scripts/preflight-check.sh ~/.openclaw/skills/

# 校验通过后安装
skillhub install experience-accumulator --dir ~/.openclaw/skills/
```

---

### 运行时容错保护

日志写入时自动处理并发和权限问题：

```bash
#!/bin/bash
# safe-write.sh — 安全的日志写入脚本

LOG_FILE=".learnings/${1:-LEARNINGS.md}"
ENTRY="$2"

# 1. 确保目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 2. 写入前检查文件权限
if [ ! -w "$LOG_FILE" ]; then
    echo "❌ 无法写入 $LOG_FILE，请检查文件权限"
    exit 1
fi

# 3. 原子写入（先写临时文件再 mv）
TEMP_FILE=$(mktemp "${LOG_FILE}.tmp.XXXXXX")
echo "$ENTRY" > "$TEMP_FILE"
cat >> "$LOG_FILE" || { rm -f "$TEMP_FILE"; exit 1; }
rm -f "$TEMP_FILE"

echo "✅ 日志已写入: $LOG_FILE"
```

---

### 1. 一键安装 CLI（无内置技能）

```bash
curl -fsSL https://skillhub.cn/install/install.sh | bash -s -- --cli-only
```

### 2. 安装校验

```bash
skillhub --version
skillhub --help
```

> 报错 `command not found`：手动将 CLI 路径写入 `~/.zshrc` / `~/.bashrc`

### 3. 软件源配置

```bash
# 设置国内商店源
skillhub config set registry https://skillhub.cn
# 查看当前源
skillhub config list
```

### 4. 安装本技能

安装必须携带 `--dir` 参数指定 AI 技能目录：

```bash
# OpenClaw
skillhub install experience-accumulator --dir ~/.openclaw/skills/
# Claude Code
skillhub install experience-accumulator --dir ~/.claude/skills/
# Codex CLI
skillhub install experience-accumulator --dir ~/.codex/skills/
# GitHub Copilot
skillhub install experience-accumulator --dir ~/.github/skills/
```

### 5. 配套 CLI 管理命令

```bash
# 查看已安装技能
skillhub list --dir 目标路径
# 更新技能
skillhub update experience-accumulator --dir 目标路径
# 卸载技能
skillhub uninstall experience-accumulator --dir 目标路径
# 模糊检索技能
skillhub search self-improvement
```

### 6. 重载生效

- **OpenClaw**：`openclaw reload`
- **Claude/Codex**：`/reload-plugins`

---

## 📁 内置脚本说明

本技能提供以下配套脚本（用户可自行实现或使用示例）：

| 脚本 | 路径 | 功能 | 状态 |
|------|------|------|------|
| `preflight-check.sh` | `scripts/preflight-check.sh` | 安装前环境校验 | ✅ 完整 |
| `safe-write.sh` | `scripts/safe-write.sh` | 安全日志写入（原子操作+权限检查） | ✅ 完整 |
| `activator.sh` | `scripts/activator.sh` | 对话结束提醒梳理经验日志 | 📝 示例 |
| `error-detector.sh` | `scripts/error-detector.sh` | Bash 命令执行后自动捕获异常 | 📝 示例 |
| `extract-skill.sh` | `scripts/extract-skill.sh` | 从日志中提取经验为独立技能 | 📝 示例 |
| `reprompt.sh` | `scripts/reprompt.sh` | 周期性复盘查询脚本 | ✅ 完整 |

> **说明**：带 ✅ 的脚本可直接使用；带 📝 的需要用户根据自身环境实现。钩子配置中引用的脚本路径为示例，实际使用时请根据安装位置调整。

---

## 🎣 钩子自动化配置

### Claude 基础版（对话提交提醒记录日志）

`.claude/settings.json`：

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "./skills/experience-accumulator/scripts/activator.sh"
      }]
    }]
  }
}
```

### Claude 进阶版（增加 Bash 命令自动捕获报错）

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "./skills/experience-accumulator/scripts/activator.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "./skills/experience-accumulator/scripts/error-detector.sh"
      }]
    }]
  }
}
```

- `activator.sh`：对话结束提醒梳理经验日志
- `error-detector.sh`：执行 Shell 后自动捕获异常写入 ERRORS.md

---

## 🧩 技能自动提取

### 提取判定条件（满足任意一条即可）

1. 关联 ≥ 2 条同类历史日志
2. 问题已修复验证可用
3. 解决逻辑复杂、无法一眼想到
4. 跨项目通用，无项目绑定逻辑
5. 用户明确要求保存为独立技能

### 手动创建规范

1. 路径：`skills/技能名/SKILL.md`
2. 头部必须包含 YAML 配置，文件夹名与技能名完全一致
3. 禁止在技能文件夹内放置 README.md
4. 完善 SKILL.md 后，原日志标记 `Status: promoted_to_skill`，补充 Skill-Path 路径

### 技能质量校验标准

1. 方案可独立运行，不依赖原会话上下文
2. 无项目硬编码路径、变量
3. 代码示例完整可复现
4. 命名小写+横杠分隔

---

## ✅ 最佳实践约束

1. **立刻记录**：问题发生时立即写入日志，不拖延
2. **描述精准**：报错必须附带复现步骤和完整上下文
3. **方案明确**：填写关联文件路径、给出明确修复方案，不写模糊"排查"
4. **统一标签**：使用分类/领域标签，方便检索过滤
5. **尽早晋升**：通用经验及时写入全局文档，不要堆积日志
6. **定期清理**：复盘时标记 resolved/promoted，避免日志臃肿

---

## 🔧 常见故障排错

| 问题 | 解决方案 |
|------|---------|
| `skillhub: command not found` | 新开终端；将 CLI 路径写入 `~/.zshrc` / `~/.bashrc` |
| 技能安装完成不生效 | 核对 `--dir` 目录、执行重载指令、确认客户端支持自定义技能 |
| 下载安装超时 | 切换国内 registry 源、放开存储域名白名单 |
| 钩子脚本无执行提醒 | 检查 hooks 配置文件路径、权限、脚本可执行权限 `chmod +x *.sh` |
| `grep` 检索不到历史重复日志 | 核对 `Pattern-Key` 拼写、日志文件写入权限 |
| 日志写入权限不足 | 使用 `safe-write.sh` 脚本，自动检查并创建目录 |
| 磁盘空间不足 | 运行 `preflight-check.sh` 预检，清理过期日志 |

| 问题 | 解决方案 |
|------|---------|
| `skillhub: command not found` | 新开终端；写入环境变量配置文件 |
| 技能安装完成不生效 | 核对 `--dir` 目录、执行重载指令、确认客户端支持自定义技能 |
| 下载安装超时 | 切换国内 registry 源、放开存储域名白名单 |
| 钩子脚本无执行提醒 | 检查 hooks 配置文件路径、权限、脚本可执行权限 `chmod +x *.sh` |
| `grep` 检索不到历史重复日志 | 核对 `Pattern-Key` 拼写、日志文件写入权限 |

---

## 📋 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0.0 | 2026-07-01 | 首次发布：经验累积器，三套日志模板、重复模式识别、经验晋升、SkillHub CLI 安装 |
| 1.1.0 | 2026-07-01 | 补充功能边界定义、自动化容错保护、内置脚本说明、去重优化 |

---

_experience Accumulator V1.0 | 2026-07-01 | 把每次犯错、每次学习、每次优化都攒起来 📦_
