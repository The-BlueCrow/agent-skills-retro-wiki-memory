#!/bin/bash
# reprompt.sh — 周期性复盘查询
# 用法：bash reprompt.sh [目录=.learnings]  [区域过滤,如 backend]
# 行为：只读统计，不改任何文件（复盘动作由人/Agent 按输出执行）
# 状态行兼容粗体模板（**Status**: pending）与普通写法两种格式


DIR="${1:-.learnings}"
AREA="${2:-}"

[ -d "$DIR" ] || { echo "❌ 目录不存在: $DIR"; exit 1; }

echo "== 待处理统计 =="
echo "pending 总数: $(grep -hE "Status.*: pending" "$DIR"/*.md 2>/dev/null | wc -l)"
echo "in_progress:  $(grep -hE "Status.*: in_progress" "$DIR"/*.md 2>/dev/null | wc -l)"
echo "resolved:     $(grep -hE "Status.*: resolved" "$DIR"/*.md 2>/dev/null | wc -l)"
echo "promoted:     $(grep -hE "Status.*: promoted$" "$DIR"/*.md 2>/dev/null | wc -l)"

echo
echo "== 高优先级待处理条目 =="
grep -B5 -E "Priority.*: high" "$DIR"/*.md 2>/dev/null | grep "^## \[" || echo "(无)"

if [ -n "$AREA" ]; then
    echo
    echo "== 区域 [$AREA] 日志文件 =="
    grep -lE "Area.*: $AREA" "$DIR"/*.md 2>/dev/null || echo "(无)"
fi

echo
echo "== 重复模式 Top（按 Recurrence-Count）=="
grep -h "Recurrence-Count:" "$DIR/LEARNINGS.md" 2>/dev/null | sort | uniq -c | sort -rn | head -10 || echo "(无)"
