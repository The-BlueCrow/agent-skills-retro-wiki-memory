# scripts 用法说明

## 脚本清单

| 脚本 | 用途 | 用法 / 接口 |
|---|---|---|
| `preflight-check.sh` | SkillHub CLI 前置校验 | `bash preflight-check.sh`；缺依赖时报错退出并给安装指引 |
| `safe-write.sh` | 追加式安全写入（原子落盘+自动分节） | `bash safe-write.sh [日志文件名=LEARNINGS.md] "条目内容"`；在调用目录下写 `.learnings/` |
| `reprompt.sh` | 周期性复盘只读统计 | `bash reprompt.sh [目录=.learnings] [区域过滤]`；统计 pending 条目数，不改文件 |
| `activator.sh` | 会话结束时提醒梳理经验 | 挂到宿主的会话提示钩子（UserPromptSubmit 类）；向 stderr 打一行提醒，永不阻断 |
| `error-detector.sh` | 命令执行后自动捕获异常 | 挂到宿主的工具后置钩子（PostToolUse 类）；stdin 收 hook JSON，命中失败信号才追加 ERR 条目 |
| `detect-signal.py` | 失败信号检测（error-detector.sh 调用） | stdin 收 hook JSON；命中输出 `bad`，格式不符或成功则无输出、退出码 0 |
| `extract-skill.sh` | 经验晋升为独立技能 | `bash extract-skill.sh <条目ID> <技能名(小写横杠)> [技能目录=skills]`；生成 SKILL.md 骨架并回标原条目 Status |

## 约定

- 钩子 JSON 的字段名各宿主略有差异，error-detector.sh 识别 exit code / is_error / stderr 三类失败信号；对不上就静默跳过。
- 全部脚本纯 bash + python3 标准库，无第三方依赖；`bash -n` / `py_compile` 均可自检。
- 写入类脚本原子落盘、保留原内容；提醒类脚本永不阻断主流程。

