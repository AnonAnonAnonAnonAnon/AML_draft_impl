#!/usr/bin/env python3
# Thin Python wrapper around `codex exec` for programmatic use with common options.
import os
import subprocess
from pathlib import Path
from typing import Iterable, Sequence


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _append_repeat(args: list[str], flag: str, values: Iterable[str] | None) -> None:
    if not values:
        return
    for value in values:
        args.extend([flag, value])


def codex_exec(
    instruction: str,
    *,
    repo_root: Path | str | None = None,
    search: bool = True,
    sandbox: str | None = "danger-full-access",
    ask_for_approval: str | None = "never",
    dangerously_bypass: bool = True,
    model: str | None = None,
    profile: str | None = None,
    config: Sequence[str] | None = None,
    enable: Sequence[str] | None = None,
    disable: Sequence[str] | None = None,
    images: Sequence[Path | str] | None = None,
    oss: bool = False,
    local_provider: str | None = None,
    full_auto: bool = False,
    skip_git_repo_check: bool = False,
    add_dir: Sequence[Path | str] | None = None,
    output_schema: Path | str | None = None,
    output_last_message: Path | str | None = None,
    json_output: bool = False,
    color: str | None = None,
    extra_args: Sequence[str] | None = None,
    check: bool = True,
    capture_output: bool = False,
    text: bool = True,
    input_text: str | None = None,
    env: dict | None = None,
    show_cmd: bool = True,
) -> subprocess.CompletedProcess:
    """Run a single Codex instruction via `codex exec`.

    Defaults: web search enabled + bypass approvals/sandbox for full access.
    Set dangerously_bypass=False to honor sandbox/approvals.
    """
    if not instruction or not instruction.strip():
        raise ValueError("instruction must be a non-empty string")

    root = Path(repo_root) if repo_root else _default_repo_root()

    cmd: list[str] = ["codex"]
    if search:
        cmd.append("--search")
    if not dangerously_bypass and ask_for_approval:
        cmd.extend(["--ask-for-approval", ask_for_approval])

    _append_repeat(cmd, "--config", config)
    _append_repeat(cmd, "--enable", enable)
    _append_repeat(cmd, "--disable", disable)

    if model:
        cmd.extend(["--model", model])
    if profile:
        cmd.extend(["--profile", profile])
    if images:
        for image in images:
            cmd.extend(["--image", str(image)])
    if oss:
        cmd.append("--oss")
    if local_provider:
        cmd.extend(["--local-provider", local_provider])
    if full_auto:
        cmd.append("--full-auto")
    if dangerously_bypass:
        cmd.append("--dangerously-bypass-approvals-and-sandbox")

    cmd.append("exec")
    cmd.extend(["--cd", str(root)])

    if not dangerously_bypass and sandbox:
        cmd.extend(["--sandbox", sandbox])
    if skip_git_repo_check:
        cmd.append("--skip-git-repo-check")
    if add_dir:
        for directory in add_dir:
            cmd.extend(["--add-dir", str(directory)])
    if output_schema:
        cmd.extend(["--output-schema", str(output_schema)])
    if output_last_message:
        cmd.extend(["--output-last-message", str(output_last_message)])
    if json_output:
        cmd.append("--json")
    if color:
        cmd.extend(["--color", color])
    if extra_args:
        cmd.extend(extra_args)

    cmd.append(instruction)

    if show_cmd:
        print("+ " + " ".join(cmd))

    if env is None:
        env = os.environ.copy()

    run_kwargs = {
        "env": env,
        "check": check,
        "capture_output": capture_output,
        "text": text,
    }
    if input_text is not None:
        run_kwargs["input"] = input_text

    return subprocess.run(cmd, **run_kwargs)
