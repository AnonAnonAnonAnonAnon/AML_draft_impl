#!/usr/bin/env python3
from codex_wrapper__r20260114_181903 import codex_exec


instruction = "List the first 5 entries in the repo root"
result = codex_exec(instruction, capture_output=True)
print(result.stdout)
