#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wiki-lint —— llm-wiki-slim 配套体检脚本（纯 stdlib，零依赖）
用法: python3 wiki-lint.py [WIKI_PATH]   # 缺省 $WIKI_PATH 或 ~/wiki
检查: 断链/裸互链/孤儿/出链<2/frontmatter/标签越界/index 计数与缺页/行数/log 条数/updated 过期
退出码: 0 = PASS, 1 = 有 issue
实现要点：段落切分标题锚定、跨行计数用 re.M、断链正则兼容裸链。
"""
import os, re, sys, glob, datetime

W = sys.argv[1] if len(sys.argv) > 1 else (os.environ.get('WIKI_PATH') or os.path.expanduser('~/wiki'))
if not os.path.isdir(W):
    print('FAIL: wiki 路径不存在: %s' % W)
    sys.exit(1)

SEV_ORDER = {'high': 0, 'medium': 1, 'low': 2}
issues = []


def add(sev, path, msg):
    issues.append((SEV_ORDER[sev], sev, path, msg))


def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


# ---- 页面收集：domains/<域>/*.md（排除 GUIDE），兼容顶层四目录 ----
pages = {}
for f in glob.glob(os.path.join(W, 'domains', '*', '*.md')):
    if not f.endswith('GUIDE.md'):
        pages[os.path.splitext(os.path.basename(f))[0]] = f
for d in ('entities', 'concepts', 'comparisons', 'queries'):
    for f in glob.glob(os.path.join(W, d, '*.md')):
        pages[os.path.splitext(os.path.basename(f))[0]] = f

schema_p = os.path.join(W, 'SCHEMA.md')
if not os.path.exists(schema_p):
    print('FAIL: 缺 SCHEMA.md，这不像个 wiki')
    sys.exit(1)
schema = read(schema_p)

# 坑①：段落切分用标题锚定（裸词会被正文半句截胡 → 标签集取空 → 合法标签全误判越界）
tm = re.search(r'##\s*Tag Taxonomy.*?(?=\n## |\Z)', schema, re.S)
tax = set(re.findall(r'`([^`]+)`', tm.group(0))) if tm else set()
if not tax:
    add('high', 'SCHEMA.md', 'Tag Taxonomy 段解析为空，无法校验标签')

LINK = re.compile(r'\[\[([a-zA-Z0-9_-]+)(\|[^\]]*)?\]\]')
incoming = {s: 0 for s in pages}

for slug, path in sorted(pages.items()):
    rel = os.path.relpath(path, W)
    text = read(path)
    lines = text.splitlines()

    # frontmatter
    fm = {}
    if lines and lines[0] == '---':
        end = next((i for i in range(1, len(lines)) if lines[i] == '---'), None)
        if end is None:
            add('high', rel, 'frontmatter 未闭合')
        else:
            for l in lines[1:end]:
                m = re.match(r'(\w+):\s*(.*)', l)
                if m:
                    fm[m.group(1)] = m.group(2)
            for k in ('title', 'created', 'updated', 'type', 'tags', 'sources'):
                if k not in fm:
                    add('medium', rel, 'frontmatter 缺字段: %s' % k)
    else:
        add('high', rel, '缺 frontmatter（首行应为 ---）')

    # 标签越界
    tm2 = re.search(r'\[([^\]]+)\]', fm.get('tags', ''))
    if tm2 and tax:
        for t in [x.strip() for x in tm2.group(1).split(',')]:
            if t and t not in tax:
                add('medium', rel, '标签越界（不在 SCHEMA taxonomy）: %s' % t)

    # 互链：坑③——断链正则必须兼容裸 [[slug]]，只认带 | 的会把裸链报成“出链 0 条”
    outs, bare = set(), []
    for m in LINK.finditer(text):
        s, disp = m.group(1), m.group(2)
        if s == slug:
            continue
        if disp is None:
            bare.append(s)
        outs.add(s)
    for s in sorted(outs):
        if s not in pages:
            add('high', rel, '断链: [[%s]] 目标页不存在' % s)
    if bare:
        add('medium', rel, '裸互链缺 |显示名: %s' % ', '.join(sorted(set(bare))))
    if len({s for s in outs if s in pages}) < 2:
        add('medium', rel, '出链 <2（SCHEMA 规定每页 ≥2 条）')
    for s in outs:
        if s in incoming:
            incoming[s] += 1

    if len(lines) > 200:
        add('low', rel, '超过 200 行，建议拆页（%d 行）' % len(lines))

    um = re.search(r'updated:\s*(\d{4}-\d{2}-\d{2})', text)
    if um:
        try:
            age = (datetime.date.today() - datetime.date.fromisoformat(um.group(1))).days
            if age > 90:
                add('low', rel, 'updated 落后 %d 天，考虑复检' % age)
        except ValueError:
            add('medium', rel, 'updated 格式不是 YYYY-MM-DD')

    if re.search(r'contested:|contradictions:', text):
        add('low', rel, '标了 contested/contradictions，需人工裁决')

# 孤儿页
for slug, n in sorted(incoming.items()):
    if n == 0:
        add('medium', os.path.relpath(pages[slug], W), '孤儿页：没有其它页链入')

# ---- index 校验 ----
idx_p = os.path.join(W, 'index.md')
if not os.path.exists(idx_p):
    add('high', 'index.md', 'index.md 不存在')
    idx = ''
else:
    idx = read(idx_p)

m = re.search(r'Total pages\*\*：(\d+)', idx)
if not m:
    add('high', 'index.md', '找不到 Total pages')
elif int(m.group(1)) != len(pages):
    add('high', 'index.md', 'Total pages=%s 与实际页数 %d 不符' % (m.group(1), len(pages)))

# 坑②：跨行计数必须 re.M，否则 ^ 锚失效返回 -1 → 假不一致
for hm in re.finditer(r'^(#{2,3}) .*?（(\d+)）', idx, re.M):
    level, hdr_n = len(hm.group(1)), int(hm.group(2))
    rest = idx[hm.end():]
    nm = re.search(r'\n#{1,%d} ' % level, rest)
    body = rest[:nm.start()] if nm else rest
    listed = len(re.findall(r'^- \[\[', body, re.M))
    if listed != hdr_n:
        add('high', 'index.md', '分区表头 %s 与列出条数 %d 不符' % (hm.group(0).strip(), listed))

for slug in sorted(pages):
    if ('[[%s|' % slug) not in idx and ('[[%s]]' % slug) not in idx:
        add('medium', 'index.md', 'index 缺页: %s' % slug)

# ---- log ----
log_p = os.path.join(W, 'log.md')
if not os.path.exists(log_p):
    add('high', 'log.md', 'log.md 不存在')
else:
    n_log = len(re.findall(r'^## ', read(log_p), re.M))
    if n_log > 500:
        add('medium', 'log.md', 'log 已有 %d 条，超 500 应轮转 log-YYYY.md' % n_log)

# ---- 报告 ----
issues.sort(key=lambda x: (x[0], x[2]))
if not issues:
    print('PASS: %d 页，0 issues' % len(pages))
    sys.exit(0)
counts = {}
for _, sev, _, _ in issues:
    counts[sev] = counts.get(sev, 0) + 1
print('FAIL: %d 页，%d issues（high=%d medium=%d low=%d）' % (
    len(pages), len(issues), counts.get('high', 0), counts.get('medium', 0), counts.get('low', 0)))
for _, sev, path, msg in issues:
    print('  [%s] %s — %s' % (sev, path, msg))
sys.exit(1)
