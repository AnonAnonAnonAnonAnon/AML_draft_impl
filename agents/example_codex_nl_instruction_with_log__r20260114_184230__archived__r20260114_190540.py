#!/usr/bin/env python3
from codex_wrapper_with_log__r20260114_184230__archived__r20260114_190540 import (
    codex_exec_to_log,
)


instruction = "List the first 5 entries in the repo root"
log_path = codex_exec_to_log(instruction)
print(log_path)

# 归档说明（中文详注）：
# 1) 这是最简“自然语言指令”的调用示例，instruction 可以写成中文/英文的自然语言描述。
# 2) codex_exec_to_log 会执行 Codex，并把 stdout/stderr 等完整输出写入日志文件，
#    返回值是日志路径；这里直接打印该路径，便于后续打开查看。
# 3) 默认参数 search=True、dangerously_bypass=True（完全权限）。如果希望更安全的运行方式，
#    可以显式传入 search=False、dangerously_bypass=False、sandbox="read-only" 等参数。
# 4) 日志中包含命令信息、stdout/stderr、returncode 以及可能的 token 统计行，
#    便于后续排查与复盘。
