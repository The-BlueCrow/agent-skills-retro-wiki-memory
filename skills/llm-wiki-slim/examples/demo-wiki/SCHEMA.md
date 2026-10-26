---
title: 示例库约定 SCHEMA
---

# SCHEMA —— 示例 wiki 的全部约定

## Domain
演示 llm-wiki-slim 工作流的最小知识库：主题是「AI 协作的工程实践」。换成你自己的领域时，只改本文件的 Domain 与 Tag Taxonomy。

## Conventions
- 文件名英文小写连字符；每页 frontmatter 必填 title / created / updated / type / tags / sources。
- 互链用 `[[slug|显示名]]`，每页 ≥2 条出链；每次改动 bump `updated`、更新 index、追加 log。
- `raw/` 只读不可变：纠正写进页面，永不改原文。
- 合成 3+ 来源的段落标来源；单来源或观点性结论设 confidence。

## Tag Taxonomy
`memory` `skills` `git` `workflow` `tooling`

## Page Thresholds
- 建页门槛：2+ 来源提到，或单来源的核心对象。
- 单页 >200 行拆页；log 超 500 条轮转。

## Update Policy
新旧冲突看日期；真冲突并列保留并标 `contradictions:`，交 lint 报给用户，不静默覆盖。
