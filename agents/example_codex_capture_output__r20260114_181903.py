#!/usr/bin/env python3
from codex_wrapper__r20260114_181903 import codex_exec


result = codex_exec("查看下当前的仓库里面都有哪些文件", capture_output=True)
print(result.stdout.strip())
