#!/bin/bash
# safe-write.sh — 安全日志写入（原子操作+权限检查）
# 用法：bash safe-write.sh [日志文件名=LEARNINGS.md] "条目内容"

LOG_FILE=".learnings/${1:-LEARNINGS.md}"
ENTRY="$2"

# 1. 确保目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 2. 写入前检查文件权限
if [ ! -w "$LOG_FILE" ] && [ -e "$LOG_FILE" ]; then
    echo "❌ 无法写入 $LOG_FILE，请检查文件权限"
    exit 1
fi

# 3. 原子写入（先写临时文件再追加）
TEMP_FILE=$(mktemp "${LOG_FILE}.tmp.XXXXXX")
echo "$ENTRY" > "$TEMP_FILE"
cat "$TEMP_FILE" >> "$LOG_FILE" || { rm -f "$TEMP_FILE"; exit 1; }
rm -f "$TEMP_FILE"

echo "✅ 日志已写入: $LOG_FILE"
