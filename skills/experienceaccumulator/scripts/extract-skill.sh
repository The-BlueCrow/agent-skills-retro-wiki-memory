#!/bin/bash
# 用法：bash extract-skill.sh <LRN条目ID,如 LRN-20260701-001> <技能名(小写横杠)> [技能目录=skills]
# 行为：抽出该条目的 Summary/Details/Suggested Action 生成 SKILL.md 骨架；
#       原条目 Status 改 promoted_to_skill + 补 Skill-Path

set -eu
ID="${1:?用法: extract-skill.sh <LRN-ID> <技能名> [技能目录]}"
NAME="${2:?缺技能名（小写+横杠分隔）}"
SKILLS_DIR="${3:-skills}"

echo "$NAME" | grep -qE '^[a-z0-9]+(-[a-z0-9]+)*$' || { echo "❌ 技能名须小写+横杠: $NAME"; exit 1; }

SRC=""
for f in .learnings/*.md; do
  grep -q "\[$ID\]" "$f" && SRC="$f" && break
done
[ -n "$SRC" ] || { echo "❌ 未找到条目 $ID"; exit 1; }

mkdir -p "$SKILLS_DIR/$NAME"
python3 - "$ID" "$SRC" "$SKILLS_DIR/$NAME/SKILL.md" <<'PY'
import sys, re, datetime
id_, src, dst = sys.argv[1:4]
t = open(src, encoding='utf-8').read()
m = re.search(rf'## \[{re.escape(id_)}\][\s\S]*?(?=\n## \[|\Z)', t)
if not m: sys.exit('❌ 条目块解析失败')
blk = m.group(0)
def sec(title):
    mm = re.search(rf'### {title}\n([\s\S]*?)(?=\n### |\n## |\Z)', blk)
    return mm.group(1).strip() if mm else '（见原日志 ' + id_ + '）'
name = id_.lower().replace('lrn-', 'lesson-')
lines = [
    '---',
    f'name: {name}',
    f'description: "由 {id_} 提炼（extract-skill.sh 生成骨架，待人工完善 description 触发语）"',
    'version: 0.1.0',
    'license: MIT',
    '---',
    '',
    '# ' + sec('Summary'),
    '',
    '## 问题与上下文',
    '',
    sec('Details'),
    '',
    '## 解法',
    '',
    sec('Suggested Action'),
    '',
    '## 来源',
    '',
    f'- 原始日志：{src} [{id_}]',
    f'- 提取日期：{datetime.date.today().isoformat()}',
    '',
]
open(dst, 'w', encoding='utf-8').write('\n'.join(lines))
print(f'✅ 骨架已生成: {dst}')
PY

# 原条目标记 promoted_to_skill + 补 Skill-Path（文档「技能自动提取 → 手动创建规范」）
python3 - "$ID" "$SRC" "$SKILLS_DIR/$NAME" <<'PY'
import sys, re
id_, src, path = sys.argv[1:4]
t = open(src, encoding='utf-8').read()
t = re.sub(rf'(\[{re.escape(id_)}\][\s\S]*?\*\*Status\*\*: )pending', r'\1promoted_to_skill', t, count=1)
t = re.sub(rf'(\[{re.escape(id_)}\][\s\S]*?- Source:)', rf'- Skill-Path: {path}\n\1', t, count=1)
open(src, 'w', encoding='utf-8').write(t)
print(f'✅ 原条目 {id_} 已标 promoted_to_skill + Skill-Path')
PY
