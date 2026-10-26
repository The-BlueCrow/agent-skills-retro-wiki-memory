#!/bin/bash
# 行为：向 stderr 打一行轻提醒（hook 通道），永不阻断、永不改文件、永不 exit 非 0
# 挂载：宿主的会话提示钩子（UserPromptSubmit 类）指向本脚本

echo "[experience-accumulator] 本轮若有踩坑/纠错，记得记入 .learnings/（LRN/ERR/FEAT）" >&2
exit 0
