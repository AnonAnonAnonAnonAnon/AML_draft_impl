#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def codex_exec(
    instruction: str,
    *,
    repo_root: Path | str | None = None,
    sandbox: str = "read-only",
    env: dict | None = None,
    check: bool = True,
    show_cmd: bool = True,
) -> subprocess.CompletedProcess:
    """Run a single Codex instruction via `codex exec`."""
    if not instruction or not instruction.strip():
        raise ValueError("instruction must be a non-empty string")

    root = Path(repo_root) if repo_root else _default_repo_root()
    cmd = ["codex", "exec", "--cd", str(root), "--sandbox", sandbox, instruction]

    if show_cmd:
        print("+ " + " ".join(cmd))

    if env is None:
        env = os.environ.copy()

    return subprocess.run(cmd, env=env, check=check)
