---
name: llm-wiki-slim
description: "Karpathy LLM Wiki：投喂、查询、体检持久化 markdown 知识库。"
---

# LLM Wiki（瘦身定制版）

官方 bundled v2.1.0 精简，只留操作规则；Obsidian 桌面集成、无头同步整节、相关工具介绍已删。零依赖：不要账号、npm 包、API key。wiki 路径取 `WIKI_PATH`，缺省 `~/wiki`（下文 `WIKI` 即它）——一个 markdown 目录就是全部，没有数据库、没有服务。

## Always-on rules

- 新会话任何 wiki 操作前，先读 `SCHEMA.md` + `index.md` + `log.md` 末 30 条。跳过就动手 = 造重复页、漏互链、违背已有约定；页数 >100 再加一次全局文件搜索查重。
- 知识库 / 记忆类问题优先从 wiki 里答：先读 `index.md` 定位，再读页——它已把这个领域编译过一遍。
- 建页门槛：2+ 来源提到，或单来源的核心对象。顺带一提、细节、领域外一律不建页。
- 每次 ingest 三连：建 / 改页面 → 更新 `index.md`（条目 + Total pages + 日期）→ 追加 `log.md`（列出每个改动文件）。这两个是导航骨架，跳过 wiki 就退化。
- `raw/` 只读不可变：纠正写进 wiki 页面，永不改原文。
- frontmatter 必填（title / created / updated / type / tags / sources）；标签只用 SCHEMA taxonomy 里已登记的。
- 每页 ≥2 条出链；单页 >200 行拆页；`log.md` 超 500 条轮转成 `log-YYYY.md`。
- 新旧信息冲突：看日期（新的通常胜）；真冲突两条并列 + 标 `contradictions: [slug]`，交 lint 报给用户，不许静默覆盖。
- 一次改动会波及 10+ 已有页时，先跟用户确认范围。

## 目录结构（三层）

```
wiki/
├── SCHEMA.md  index.md  log.md    # 约定 / 目录 / 流水
├── raw/       # 原文只读：articles/ papers/ transcripts/ assets/
├── entities/  concepts/  comparisons/  queries/
```

- Layer 1 `raw/` 只读；Layer 2 页面由 agent 建、改、互链；Layer 3 `SCHEMA.md` 是所有约定的唯一出处。

## 初始化（新库）

1. 定 `WIKI` 路径 → 建上表目录
2. 问用户领域范围，要具体
3. 写 `SCHEMA.md`：Domain、Conventions（文件名英文小写连字符、frontmatter、互链 `[[slug|显示名]]` ≥2、更新 bump updated、入 index、写 log、出处标记）、Frontmatter 字段、raw 的 sha256 规则、Tag Taxonomy（10-20 个）、Page Thresholds、Update Policy
4. 写 `index.md`（按类型分区 + Total pages / Last updated）和 `log.md`（create 条目）

示例：`examples/demo-wiki/` 是一份 4 页最小可用库（含 SCHEMA / index / log 与 4 个示例页，过 lint），整目录拷成你的 wiki，改 Domain 与 Tag Taxonomy 即用。

完成判据：三文件齐、目录齐、已告知用户可开始投喂。

## Ingest workflow

1. 原文进 `raw/`：URL / PDF 用网页抓取工具转 markdown，粘贴文本直接写；文件名描述性（`karpathy-llm-wiki-2026.md`），加 raw frontmatter（source_url / ingested / sha256）。重投同一 URL：sha256 相同 → 跳过，不同 → 标漂移并更新。
2. 全文搜索 + 读 index 查重，先看已有哪些相关页。
3. 建 / 改页面：过阈值、互链 ≥2、标签入 taxonomy、合成 3+ 来源的段落标 `^[raw/articles/xx.md]`、单来源或观点性内容设 confidence。
4. 更新 index（计数、日期、新页入分区）；log 追加一条，列出全部改动文件。同一文件要改多处时逐处串行 patch、每步核对 diff，防互相覆盖。
   - **插新分区段的锚点必须落在段落边界**：用「上一段最后一条」做锚（其后插完整新段）或「下一节表头」做锚（其前插），绝不用段中间的条目当锚——patch 不懂段落归属，会把上一段的条目切进新段（10-12 实踩：business 2 条被切进 career 段）。插完回读整个邻域 `sed -n '/上一节/,/下一节/p'`，不能只看 patch 返回 success。
   - **页数对账口径 = lint 口径**：`find domains -name '*.md' ! -name GUIDE.md` 会漏顶层四目录（`comparisons/` 等）的页；index Total 必须与 `wiki-lint.py` 输出对齐（10-12 实踩：find 69 vs lint 70）。
   - **patch 改 log.md 锚点前先 `tail -1` 复核原文**，不要信终端截断显示（10-14 实踩：截断把 log 锚点「坑 35 扩『两侧同改』」显示成「坑 39（跑批后台化）」，按错版 patch 把「坑 35 扩」整段删了；并发复查只能解决「别人的写」不能解决「自己的视」——必须直接读原文）。
   - log 追加用 heredoc 时**终止定界符独占一行**，后续命令另起一行（10-12 实踩：`EOF && echo` 残留垃圾行）。
5. 跑 lint（本技能 `scripts/wiki-lint.py`）→ 修 → 复检；把改动文件清单报给用户。

完成判据：每个改动文件都能在 log 条目里找到，index 计数与实际页数一致，lint PASS。单份资料动 5-15 页属正常。

## Query workflow

1. 读 `index.md` 定位 → 关键词/原文检索先用 `wiki_search.py`（`python3 scripts/wiki_search.py <词> [--raw] [--regex] [--context N] [--glob "*.txt"] [--wiki 路径]`，wiki 根默认取 `WIKI_PATH` 环境变量、再默认脚本所在目录；建议部署时把脚本复制/软链进 wiki 根，或调用时带 `--wiki`/`WIKI_PATH`）；`--raw` 连 raw/ 的 OCR 全文本一起搜，多词=AND、`词1|词2`=OR，实测 0.5-0.7s，远快于逐页读）→ 页数 >100 补一次全局文件搜索 → 读页。
2. 综合作答，引用 `[[slug]]` 标明来源页。
3. 只把「重新推导一遍很痛」的答案写进 `queries/` 或 `comparisons/` 并入 index；琐碎查询不入库。
4. `log.md` 记一条，注明是否入库。

完成判据：答案带来源页引用；入库的已同步 index + log。

## Lint

- 查：断链、裸互链（`[[slug]]` 缺 `|显示名`）、孤儿页（无入链）、index 缺页、frontmatter 缺字段、标签越界、过期（`updated` 落后同主题最新来源 >90 天）、矛盾（`contested` / `contradictions`）、单来源未标 confidence、`raw/` sha256 漂移、>200 行页、log 超 500。
- 现成脚本 `scripts/wiki-lint.py`（纯 stdlib）：`python3 <技能目录>/scripts/wiki-lint.py [WIKI]`，terminal 或 execute_code 都能跑；报告按严重度排序，每条带文件路径和建议动作。单来源 confidence、sha256 漂移两项脚本不查，靠人。
- **勿跑库内旧版 `lint.py`**：若 wiki 目录里存有迁移前旧布局的 lint 脚本（只扫根级 `concepts/`、不认 `domains/`），对现行库会报一整墙「断条目/Total 不符」假错（2026-10-15 实踩：假报 124 条目 vs 真实 75 页）；唯一有效的是本技能 `scripts/wiki-lint.py`
- 脚本三个坑（2026-10-04 实测踩过）：① 切 SCHEMA 段落用标题锚定 `## Tag Taxonomy`，裸词会被正文半句截胡取到空段→合法标签全被误判越界；② 跨行计数正则必须带 `re.M`，否则 `^` 锚失效返回 -1→假不一致；③ 断链正则要兼容裸 `[[slug]]`，只认带 `|` 的会把裸链报成“出链 0 条”误导排查。
- 修完复检，向用户报 PASS / FAIL + 数量，log 追加 `## [日期] lint | N issues`；告警先分真/假——脚本 bug 不是内容问题，报给用户的计数以复核后为准。

## 视频内容入 wiki

视频类原文（抖音等）靠 `douyin-video-extraction` 技能拿**原声转录**，别拿平台章节要点当原文——那是二次改写，入 `raw/` 就等于把有损版本存成事实源。

- 转录文本进 `raw/transcripts/<描述名>.md`，frontmatter 记 `source_url` / `ingested` / `sha256` / 时长；`raw/` 只读不可变，**原始转录不动**。
- ASR 专名错字（Karpathy 被听成「卡巴西」这类）的校正与存疑标痕写在 **wiki 页面正文**，不改 raw——和引语 OCR 复原同一处理原则。
- 页面引用视频内容时标一段实际原话 + 一行核验判断，观点性结论设 confidence。

## 批量与归档

- 批量投喂：全部读完 → 一次查重 → 一次写 → 最后统一更新 index 和 log，别每份各来一轮。
- 归档：建 `_archive/` → 按原路径移入 → 从 index 删条目 → 反链改成「(archived)」纯文本 → 写 log。
- 搜索：全局文件搜索查内容/文件名，标签 `tags:.*xxx`；近期动作看 `log.md` 末尾。

## 版本管理（本地单仓建议）

知识层文件（wiki / 记忆库 / 技能库）共用一个**本地** git 仓是好习惯：可回滚、可对账、永不推远端。`.gitignore` 若用「全排除 + 逐个放行」的三层结构，注意：

1. **注释必须独立成行**——gitignore 没有行尾 `#` 语法，`pattern # 注释` 整行都是 pattern，规则会静默失效。
2. **递归放行收口要写三层**——`/*` 排除后根级用 `!/<dir>/` 逐个放行；下级再用 `/<dir>/*` 收口 + `!/<dir>/<sub>/`；第三层同理。漏任何一层 = 整棵子树不在库且 git 不吭声。放行后 `git ls-files <dir> | wc -l` 自证真进库。
3. **`.gitignore` 被自己排除时** `git add` 报 nothing added → `git add -f .gitignore` 再提交，入库后 `git ls-files --error-unmatch .gitignore` 自证。
4. **运行时被改写的文件出库**——缓存、锁文件、用量统计等会被运行时反复改写的文件若入库，status 永远脏、易混进误提交；`git rm --cached <f>` + 补 ignore 行。收尾判据 = `git status` 干净。
5. **大件 1M+ 单独排除**——推广物料、缓存索引等大件列名排除，清单写在 `.gitignore` 注释里（独立成行），`git ls-files` 复查别让几十 M 误入。

## 边界

- wiki 目录自包含：删掉它不影响其它东西，页面 / 索引 / 流水全在里面。
- 不用于：一次性问答、生成代码文档站。
