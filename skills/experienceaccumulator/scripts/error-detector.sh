#!/bin/bash
# 输入：stdin 收 hook 的 JSON（含 exit code / is_error / stderr 类字段，字段名随宿主而异）
# 行为：检测到失败信号才追加一条 ERR 条目；宿主格式不符时静默退出，永不阻断

set -u
INPUT=$(cat 2>/dev/null || true)
[ -n "$INPUT" ] || exit 0

# 提取疑似失败信号：exit_code 非 0 / is_error 为 true / stderr 非空
# 检测逻辑在同目录 detect-signal.py（stdin 收 hook JSON，输出 bad/空）。
SIGNAL=$(printf '%s' "$INPUT" | python3 "$(dirname "$0")/detect-signal.py" 2>/dev/null || true)
[ "$SIGNAL" = "bad" ] || exit 0

TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
DAY=$(date +%Y%m%d)
ERR_DIR=".learnings"
mkdir -p "$ERR_DIR"
FILE="$ERR_DIR/ERRORS.md"
[ -f "$FILE" ] || printf "# Errors\n\n命令异常、接口/第三方集成故障记录\n\n---\n" > "$FILE"

# 取报错片段做脱敏摘要（禁止记录密钥/Token —— 强制脱敏原则）
SUMMARY=$(printf '%s' "$INPUT" | python3 -c '
import json,sys,re
try: d=json.load(sys.stdin)
except Exception: sys.exit(0)
se=[]
def f(o):
    if isinstance(o,dict):
        for v in o.values(): f(v)
    elif isinstance(o,list):
        for v in o: f(v)
    elif isinstance(o,str) and o.strip() and ("error" in o.lower() or "Traceback" in o or "denied" in o.lower()):
        se.append(o)
f(d)
txt="\n".join(se)[:1200]
txt=re.sub(r"(sk-[A-Za-z0-9]{8,}|Bearer\s+\S+|api[_-]?key[\"'\'':=\s]+\S+)", "[REDACTED]", txt, flags=re.I)
print(txt)' 2>/dev/null || echo "(见 hook 输入)")

N=$(grep -c "^\## \[ERR-$DAY" "$FILE" 2>/dev/null || true)
N=${N:-0}
cat >> "$FILE" <<ENTRY
## [ERR-$DAY-$(printf '%03d' $((N + 1)))] bash-hook
**Logged**: $TS
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
PostToolUse hook 捕获到命令失败信号（自动记录）

### Error
\`\`\`
$SUMMARY
\`\`\`

### Context
来源：error-detector.sh（PostToolUse hook，自动）；原始输入已脱敏截断

### Suggested Fix
人工补：复现步骤 + 修复方案后改 Status

### Metadata
- Reproducible: unknown
- Source: hook
---
ENTRY

echo "已捕获异常并写入 $FILE" >&2
exit 0
