```yaml
title: "基于平台评审反馈迭代 retrospective-lesson skill 的全流程经验"
date: 2026-07-03
category: Skill开发
tags: [skill迭代, 反馈闭环, SKILL.md结构设计, references按需加载, markdown相对路径, 网页404修复, 平台渲染差异, SemVer版本管理, 触发方式, 适用边界]
tools: [SKILL.md, references, markdown, SemVer]
difficulty: 中级
reuse_level: 高
keywords: [skill持续迭代工作流, SKILL.md瘦身重构, references拆分按需加载, markdown相对链接网页平台404, 包内文件链接渲染坑, skill平台评审反馈处理, 加内容与拆结构取舍, SemVer语义化版本管理实践]
```

# 基于平台评审反馈迭代 retrospective-lesson skill 的全流程经验

> **TL;DR**：应对内容反馈的正解是"主文件瘦身 + references 按需加载"而非"堆砌膨胀"；包内文件跳转永远用纯文字，不用 markdown 相对链接（网页会 404）；每次改动 dry-run + publish --changelog，用 SemVer 控节奏。

---

## 一、反馈闭环工作流

把平台评审反馈当 backlog 逐版本消化，每条反馈匹配一个版本：

```
平台反馈 → 判定类型(信息缺失 or 过载) → 选修复策略(补内容 or 拆结构)
  → dry-run 预检 → publish --changelog → 等下一轮反馈
```

| 版本 | 触发反馈 | 修复动作 |
|------|---------|---------|
| v1.2.0 | 适用性 4.3（触发方式/边界不清） | 加触发方式表 + 适用边界表 |
| v1.3.0 | 文档偏长 + prompt 示例少 | 结构重构：108 行 + references 拆分 |
| v1.3.1 | references 链接 404 | 去链接语法，改纯文字描述 |

---

## 二、加内容 vs 拆结构（核心方法论）⭐

**这是本次最值钱的经验**：收到"文档偏长新手难上手"反馈时，前几版（1.1/1.2）的本能反应是往 SKILL.md 里加内容（快速开始/FAQ/触发方式），结果从 113 行膨胀到 250 行，**反而加重了"文档偏长"问题**。

| 决策矩阵 | 判定条件 | 正确动作 | 风险 |
|---------|---------|---------|------|
| 信息缺失 | 用户/评审说"没有 X""不清楚 X" | **补内容**到 SKILL.md | — |
| 信息过载 | 用户/评审说"太长""找不到重点""新手吃力" | **拆结构**：主文件瘦身 + references 按需加载 | 误判为缺失而继续加 → 膨胀 |

**关键反直觉点**：当反馈是"prompt 示例太少"时，不要把示例塞进主文件——移入 `references/prompts.md` 按需加载。这样既补了示例，又不增加主文件长度。

**主文件只保留**：触发条件 + 4 阶段骨架 + 质量清单。重型细节（完整 prompt、FAQ、边界表）全部下沉到 references/。参考已发布优质 skill（如 skillhub-daily）的 references 模式。

---

## 三、网页平台 Markdown 链接渲染坑 ⭐

### 现象
SKILL.md 里写 `[文本](references/prompts.md)`，在 skillhub.cn 网页上点击跳转到 `https://skillhub.cn/skills/references/prompts.md`，404 打不开。

### 根因
包内文件在平台**没有对应的公网 URL**。markdown 相对路径在本地/agent 加载时正确，但在浏览器渲染时被解析成了**绝对 URL**，指向一个平台并不存在的路径。

### 修复前后对比

```markdown
# ❌ 修复前（网页 404）
> 详见 [references/prompts.md](references/prompts.md)。

# ✅ 修复后（纯文字，不渲染成链接）
> 详见包内文件 `references/prompts.md`（同目录下的 references 文件夹，不是网页链接，请到 skill 目录中查看）。
```

### 自动检测
```bash
# 检测 SKILL.md 中残留的指向包内文件的 markdown 链接
grep -nE '\]\(' SKILL.md   # 有输出则需检查
```

---

## 四、references 按需加载模式

```
retrospective-lesson/
├── SKILL.md              # ~108行：骨架入口
├── references/
│   ├── prompts.md        # 6个完整prompt（用到才读）
│   └── troubleshooting.md # 边界表+FAQ（用到才读）
└── lessons-learned/      # 示例与归档
```

**原则**：SKILL.md 是 agent 启动时必读的入口，越短越好；references 是 agent 遇到具体场景时才加载的细节。

---

## 五、SemVer 版本管理实践

| 变更类型 | 版本号动作 | 示例 |
|---------|-----------|------|
| 结构性大改（重构/拆分） | bump minor | 1.2.0 → 1.3.0 |
| 小修补（单点 bug） | bump patch | 1.3.0 → 1.3.1 |

**硬规则**：每次 publish 必带 `--changelog`，写清"针对什么反馈做了什么"。

---

## 六、skill 迭代可迁移检查清单

```bash
# 1. 行数监控：超 150 行须审视是否该拆入 references
wc -l SKILL.md

# 2. 残留 markdown 链接检测（网页会 404）
grep -nE '\]\(' SKILL.md references/*.md

# 3. 版本号一致性：SKILL.md 声明 vs 即将 publish 的版本
grep -E 'version:' SKILL.md | head -1

# 4. references 完整性
ls references/ 2>/dev/null || echo "无 references 目录"
```

- [ ] SKILL.md ≤ 150 行
- [ ] 无指向包内文件的 markdown 链接（改纯文字）
- [ ] changelog 写清对应反馈与修复
- [ ] dry-run 通过后再 publish
- [ ] 结构大改 bump minor，小修 bump patch

---

## 适用场景

任何已上架公开市场的 skill，面对平台评审反馈做持续迭代时。尤其适用于：①收到"文档长"反馈时的决策；②包内文件在网页平台的链接处理；③references 拆分模式设计。
