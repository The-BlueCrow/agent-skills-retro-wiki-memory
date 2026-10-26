```yaml
title: "SkillHub CLI 安装技能在 Windows Git Bash 下 ~ 指向错误目录的排查"
date: 2026-07-03
category: 环境配置
tags: [SkillHub CLI, ZCode技能安装, Windows, Git Bash, 路径问题, 绝对路径, 波浪号解析错误, 技能加载目录]
tools: [SkillHub CLI, Git Bash, ZCode, playwright-scraper-skill, wechat-article-spider]
difficulty: 中级
reuse_level: 高
keywords: [Git Bash 波浪号指向 SPB_Data, SkillHub CLI 安装技能失败, ZCode 不识别新安装技能, Windows 技能安装目录错误, --dir 参数必须用绝对路径, ~/.agents/skills 路径错位]
```

# SkillHub CLI 安装技能：Windows Git Bash 下 `~` 路径错位排查

## TL;DR

> **Windows / Git Bash 下用 SkillHub CLI 安装技能，`--dir` 一律用 `C:/Users/<你>/.agents/skills` 绝对路径，禁用 `~`。**
> 否则 `~` 会被解析为 `C:/SPB_Data`，技能装到 `C:/SPB_Data/.agents/skills/`，而 ZCode 从 `C:/Users/100319/.agents/skills/` 加载——两个独立目录，技能不可见。

| 路径 | 实际指向 | 是否 ZCode 加载源 |
|------|----------|:-----------------:|
| `~/.agents/skills`（错误用法） | `C:/SPB_Data/.agents/skills/` | ❌ |
| `C:/Users/100319/.agents/skills`（正确用法） | `C:/Users/100319/.agents/skills/` | ✅ |

## 1. 背景与定位

本文是 SkillHub CLI 的**安装侧**经验，与 [2026-07-03-skill发布到skillhub全流程.md](./2026-07-03-skill发布到skillhub全流程.md)（发布侧）互补，共同覆盖「发布 + 安装」闭环。
任务：检查 CLI 是否已装 → 用 `python ~/.skillhub/skills_store_cli.py install` 安装两个技能。

## 2. SkillHub CLI 安装与校验

```bash
# 三路并行探测是否已装
which skillhub                       # 命令是否在 PATH
ls -la ~/.skillhub                   # 安装目录
find ~ -maxdepth 3 -iname "skills_store_cli.py"   # 按文件名兜底

# 确认版本/元数据
cat ~/.skillhub/version.json         # {"version":"2026.6.24"}
python ~/.skillhub/skills_store_cli.py --version  # skillhub 2026.6.24
```

确认已装（版本 2026.6.24），无需重装。本机 Windows 缺 `python3`，按 AGENTS.md 经验用 `python` 直跑 `skills_store_cli.py`。

## 3. 核心坑：`~` 在 Git Bash 下解析为 `C:/SPB_Data`

**现象**：`install` 报 `✓ Installed`，但 ZCode 技能列表里**找不到新技能**。

**根因**：

| 预期 | 实际 |
|------|------|
| `~` = `C:/Users/100319` | `~` = `C:/SPB_Data`（被 profile/环境变量改写） |

于是 `--dir ~/.agents/skills` 实际指向 `C:/SPB_Data/.agents/skills/`，与 ZCode 加载源 `C:/Users/100319/.agents/skills/`（73 个技能）是**两个独立目录**（`fsutil reparsepoint query` 证明非 junction/symlink）。一秒判定法：`ls` 两目录文件数，`2 vs 73` 即错位。

> **本质**：Git Bash 的 `~`/`$HOME` 可能被改写，绝不假定默认值。把 CLI 的 success 当终态是危险的——**以消费方（宿主）的读取路径为准**。

## 4. 修复：绝对路径重装 + 清理误装副本

```bash
# 正确安装：绝对路径，禁用 ~
python ~/.skillhub/skills_store_cli.py install playwright-scraper-skill \
  --dir "C:/Users/100319/.agents/skills"
python ~/.skillhub/skills_store_cli.py install wechat-article-spider \
  --dir "C:/Users/100319/.agents/skills"

# 清理误装副本（副本零容忍）
rm -rf "C:/SPB_Data/.agents/skills/playwright-scraper-skill" \
       "C:/SPB_Data/.agents/skills/wechat-article-spider"
```

装后验证闭环：

- [x] `find C:/Users/100319/.agents/skills/ -maxdepth 2 -name SKILL.md | grep <name>` 命中
- [x] `ls C:/SPB_Data/.agents/skills/` 为空（无误装残留）
- [x] ZCode 技能列表出现新技能

## 5. 一键避坑 Checklist

```bash
# 1. 先确认 ~ 实际指向（若非 C:/Users/<你> 即危险）
echo "HOME=$HOME"; echo "tilde=$(echo ~)"
# 2. 确认 ZCode 权威加载目录
ls "C:/Users/100319/.agents/skills/" | head
# 3. 安装：强制绝对路径
#    python ~/.skillhub/skills_store_cli.py install <slug> --dir "C:/Users/100319/.agents/skills"
# 4. 装后校验落盘 + 查残留副本
ls "C:/SPB_Data/.agents/skills/" 2>/dev/null && echo "⚠️发现误装副本需清理" || echo "✓无误装副本"
```

**早发现信号**：CLI 报 success 但 ZCode 列表找不到技能；`ls ~/.agents/skills` 内容与 ZCode 加载技能对不上；路径出现 `SPB_Data` 前缀——任一出现，立即查 `~` 解析值并改用绝对路径。

## 通用教训

任何在 Git Bash 下接受 `--dir`/输出路径的工具，**先 `echo ~` 验证家目录再用**。生产方（安装器）报 success 不代表消费方（加载器）可见——「装即验，验加载源」。

**关联文档**：[2026-07-03-skill发布到skillhub全流程.md](./2026-07-03-skill发布到skillhub全流程.md)（发布侧经验，含 Windows 用 python 直跑 CLI、token 前缀 skh_/sk_ 区分等坑）。
