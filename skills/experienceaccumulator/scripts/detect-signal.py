#!/usr/bin/env python3
# detect-signal.py — 失败信号检测（error-detector.sh 调用）
# 输入：stdin 收 hook 的 JSON；输出：bad / 空行
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
def find(k, o):
    if isinstance(o, dict):
        for kk, vv in o.items():
            if kk == k:
                yield vv
            yield from find(k, vv)
    elif isinstance(o, list):
        for vv in o:
            yield from find(k, vv)
bad = False
for c in find("exit_code", d):
    if isinstance(c, int) and c != 0:
        bad = True
for b in find("is_error", d):
    if b is True:
        bad = True
for e in find("stderr", d):
    if isinstance(e, str) and e.strip():
        bad = True
print("bad" if bad else "")
