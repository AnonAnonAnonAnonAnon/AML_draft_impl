#!/usr/bin/env python3
import sys

from codex_wrapper__r20260114_181903 import codex_exec


def main() -> int:
    instruction = " ".join(sys.argv[1:]).strip() or "pwd"
    codex_exec(instruction)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
