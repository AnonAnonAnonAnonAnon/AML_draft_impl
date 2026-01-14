#!/usr/bin/env python3
from codex_wrapper__r20260114_181903 import codex_exec


codex_exec(
    "rg --files | head -n 5",
    search=False,
    dangerously_bypass=False,
    sandbox="read-only",
)
