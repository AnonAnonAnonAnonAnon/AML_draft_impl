#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path


def run(cmd, env):
    print("+ " + " ".join(cmd))
    subprocess.run(cmd, env=env, check=True)


def main():
    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()

    base = ["codex", "exec", "--cd", str(repo_root), "--sandbox", "read-only"]

    default_cmds = [
        ["codex", "--help"],
        base + ["pwd"],
        base + ["rg --files | head -n 20"],
        base + ["rg -n 'robotwin|RoboTwin' -S README.md docs -g'*.md'"],
        base + ["git status --porcelain"],
    ]

    for cmd in default_cmds:
        run(cmd, env)

    if len(sys.argv) > 1:
        extra = " ".join(sys.argv[1:]).strip()
        if extra:
            run(base + [extra], env)


if __name__ == "__main__":
    main()
