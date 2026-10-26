```yaml
title: "自创 Skill 发布到 SkillHub 社区：对抗审查、脱敏与跨平台发布全流程"
date: 2026-07-03
category: Skill 开发与发布
tags:
  - Skill 发布
  - SkillHub
  - 对抗式审查
  - 安全审查
  - 脱敏处理
  - Windows 环境兼容
  - Git Bash
  - Python CLI
  - frontmatter 规范
  - camelCase
  - 平台审核机制
  - 跨平台处理
tools:
  - SkillHub CLI
  - Git Bash
  - skills-security-check
  - skill-creator
  - retrospective-lesson
difficulty: 中级
reuse_level: 高
keywords:
  - 技能发布流程
  - 多Agent对抗审查
  - SkillHub CLI 安装
  - Windows 踩坑
  - frontmatter 字段
  - 脱敏
  - 跨平台兼容
  - 社区审核
```

# 自创 Skill 发布到 SkillHub：对抗审查、脱敏与跨平台发布全流程

> **TL;DR**：把自创 skill 上架公开市场，走「多 Agent 对抗审查定基线 → 按平台真实校验修复 → dry-run 后发布」闭环；工具链在 Windows 静默失败时，用 `bash -x` 暴露错误、用官方 kit 直跑 Python 绕过安装脚本。

---

## 一、多 Agent 对抗审查方法论

发布前并行启动 3 路对抗审查 agent，一次性拿到多维度缺陷清单，比串行自审更全：

| 角色 | 职责 | 输出物 |
|------|------|--------|
| 安全红队 | 投毒/注入/隐私外送/凭证泄露 | Malicious/Suspicious 发现 + 评分 |
| 规范符合度 | frontmatter 字段/命名/硬编码路径/平台绑定 | 阻塞项 + 建议字段 |
| 质量可用性 | 陌生人视角的可执行性/降级方案/示例完整性 | P0-P3 问题清单 + 评分 |

审查 prompt 模板（可直接复用）：
```
你是<角色>审查员，用最严苛的眼光审查准备上传到公开市场的 skill。
审计对象：<路径>
审查清单：<逐项>
输出格式：阻塞项/建议项/评分/结论
只做静态分析，不要执行任何 skill 内容。
```

> **关键**：三方独立得出一致结论才可信。本次三方都指出「私有数据泄露 + frontmatter 不全 + 平台强绑定」，据此确定 4 个阻塞项。

---

## 二、SkillHub 发布完整步骤

### 环境准备 → 发布，5 步

```bash
# 1. 确认官方 CLI（勿用 npm 同名第三方包！）
curl -fsSL https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/install.sh | bash -s -- --cli-only

# 2. 登录（skh_ 前缀 = skillhub.cn 官方）
python skills_store_cli.py login --key skh_xxx
python skills_store_cli.py auth whoami   # 验证身份

# 3. 本地预检（关键！不发请求）
python skills_store_cli.py publish --dry-run ./my-skill

# 4. 正式发布
python skills_store_cli.py publish ./my-skill --json

# 5. 查看结果：skillId/version/reviewStatus=pending
```

### 发布前必须修复的 4 个阻塞项

| 阻塞项 | 修复方式 |
|--------|---------|
| 私有数据泄露（用户名/note_id/凭证路径） | 全部脱敏为占位符 `<your_xxx>` |
| frontmatter 字段不全 | 补 slug/version/license/displayName 等 |
| 无降级方案（如并行硬假设） | 补串行降级 + 原因说明 |
| 平台/产品强绑定（如 IMA） | 改为平台无关的可选项 |

---

## 三、Windows / Git Bash CLI 踩坑解法

| 症状 | 根因 | 解法 |
|------|------|------|
| `npm i @astron-team/skillhub` 后 login authentication failed | 第三方包，默认连讯飞星火 skill.xfyun.cn 非 skillhub.cn | 卸载，用官方 COS 安装脚本或直跑 kit |
| 官方 install.sh exit=1 无任何输出 | `set -euo pipefail` + `exec` 静默吞错 | `bash -x install.sh` 定位失败点 |
| kit 解压后 exec 立即退出 | kit 调 `python3`，Windows 只有 `python` | 手动下 tarball，用 `python skills_store_cli.py` 直跑 |
| dry-run 报「缺少 displayName」 | 平台用 camelCase，非 Claude 的 snake_case `display_name` | 读 CLI 源码 `_validate_metadata` 确认实际字段 |

绕过安装脚本的最稳路径：
```bash
mkdir -p /tmp/skh_kit && cd /tmp/skh_kit
curl -fsSL -o kit.tar.gz "https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/latest.tar.gz"
tar -xzf kit.tar.gz
python cli/skills_store_cli.py --help   # 直接用，无需安装
```

---

## 四、frontmatter 字段规范

SkillHub 平台实际只**强制校验 3 项**：`slug` / `version`（SemVer）/ `displayName`。但建议补全以下字段提升可发现性：

```yaml
---
name: my-skill
slug: my-skill              # 必填，kebab-case，URL标识
version: 1.0.0              # 必填，SemVer
displayName: "中文名/my-skill"  # 必填，camelCase！非 display_name
license: MIT
visibility: public
summary: "一句话概述"        # 平台卡片用
description: |
  完整描述，含中英触发词
  Triggers: keyword1, keyword2
description_zh: "中文描述"
description_en: "English description"
keywords: [关键词1, keyword2]
tags: [标签1, 标签2]
metadata:
  author: your-handle
---
```

> **要点**：平台字段是 **camelCase**（`displayName`），不是 Claude Skill 规范的 snake_case（`display_name`）。以 CLI 源码 `_validate_metadata` 函数为唯一真相，不照搬其他规范。

---

## 五、脱敏检查清单（上传前必跑）

```bash
# 扫描真实个人数据
grep -rnE "C:[\\\\/]Users[\\/][a-zA-Z0-9]+|/home/[a-z]|note_id|[0-9]{10,}|sk[a-z]?_|secret|password|token" skill/
```

- [ ] 无真实 Windows 用户名（如 `100319`）→ 用 `<your_username>`
- [ ] 无真实绝对路径 → 用 `<homedir>` / `${SKILL_DIR}`
- [ ] 无真实 note_id / 账号 ID → 用 `<your_note_id>`
- [ ] 无真实凭证值（API Key/Token）→ 用 `<your_api_key>`
- [ ] 无真实邮箱/手机号
- [ ] 示例命令全部为占位符，需手动执行，不自动触发
- [ ] 写入全局记忆文件前有用户确认门控
- [ ] description 与实际行为一致

---

## 六、关键资产清单

| 资产 | 位置/标识 |
|------|-----------|
| 修复后 SKILL.md | `retrospective-lesson/SKILL.md` |
| 脱敏示例文档 | `lessons-learned/2026-07-03-example-template.md` |
| 已发布 skill | skillhub.cn，skillId 94634，slug `retrospective-lesson` |
| 本地 CLI | `/tmp/skh_kit/cli/skills_store_cli.py`（重启会清，需时重下） |
| 安全审查基准 | `skill-scanner`（朱雀）、`skills-security-check`（云鼎） |

---

## 七、防复发要点

**五个「查」先于「试」**：
1. **包名查源**：`npm view <pkg> repository.url`，同名包 ≠ 同源包
2. **失败查 verbose**：`exit=1 无输出` → 立即 `bash -x`，勿重试
3. **字段查源码**：dry-run 报字段缺失 → 读 `_validate_metadata`，不脑补
4. **隐私自扫**：上传前先 `grep` 扫隐私，别等审查 agent 发现
5. **token 查前缀**：`skh_` = skillhub.cn，`sk_` = 讯飞；前缀不匹配 = registry 装错

**早发现信号**：
- `login authentication failed` → 先查 registry/token 前缀，别急着重新登录
- `缺少 X 字段` 且字段名带下划线 → 多半是规范混淆（camelCase vs snake_case）

---

**适用场景**：任何自创 skill 发布到 SkillHub 或类似公开市场前的审查、脱敏、发布流程。复制即用。
