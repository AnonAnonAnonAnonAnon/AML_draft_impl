#!/usr/bin/env python3
# Wrapper for `codex exec` that writes full output to a log file and returns the log path.
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_log_dir(repo_root: Path) -> Path:
    return repo_root / "docs" / "codex_logs"


def _append_repeat(args: list[str], flag: str, values: Iterable[str] | None) -> None:
    if not values:
        return
    for value in values:
        args.extend([flag, value])


def _find_token_lines(text: str) -> list[str]:
    token_lines: list[str] = []
    for line in text.splitlines():
        if "token" in line.lower():
            token_lines.append(line.strip())
    return token_lines


def codex_exec_to_log(
    instruction: str,
    *,
    repo_root: Path | str | None = None,
    log_dir: Path | str | None = None,
    run_id: str | None = None,
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
    text: bool = True,
    input_text: str | None = None,
    env: dict | None = None,
    show_cmd: bool = True,
) -> str:
    """Run a single Codex instruction and log all output to a file."""
    if not instruction or not instruction.strip():
        raise ValueError("instruction must be a non-empty string")

    root = Path(repo_root) if repo_root else _default_repo_root()
    log_root = Path(log_dir) if log_dir else _default_log_dir(root)
    log_root.mkdir(parents=True, exist_ok=True)

    if run_id is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    log_path = log_root / f"codex_exec__r{run_id}.log"

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
        "check": False,
        "capture_output": True,
        "text": text,
    }
    if input_text is not None:
        run_kwargs["input"] = input_text

    result = subprocess.run(cmd, **run_kwargs)

    output_text = (result.stdout or "") + (result.stderr or "")
    token_lines = _find_token_lines(output_text)

    header = [
        "codex_exec log",
        f"timestamp: {datetime.now().isoformat(timespec='seconds')}",
        f"repo_root: {root}",
        f"model: {model or '(default)'}",
        f"instruction: {instruction}",
        f"command: {' '.join(cmd)}",
        f"search: {search}",
        f"dangerously_bypass: {dangerously_bypass}",
        "---- stdout ----",
        result.stdout or "",
        "---- stderr ----",
        result.stderr or "",
        "---- footer ----",
        f"returncode: {result.returncode}",
    ]

    if token_lines:
        header.append("token_usage_lines:")
        header.extend(token_lines)
    else:
        header.append("token_usage: not reported in output")

    log_path.write_text("\n".join(header), encoding="utf-8")

    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, cmd, output=result.stdout, stderr=result.stderr
        )

    return str(log_path)


# Parameter reference (defaults are shown as in the function signature):
# - instruction: required natural-language or shell instruction string.
# - repo_root=None: repo root for --cd (defaults to repo of this file).
# - log_dir=None: directory for logs (defaults to docs/codex_logs).
# - run_id=None: string for log filename (defaults to YYYYMMDD_HHMMSS).
# - search=True: add `--search`.
# - sandbox="danger-full-access": used only when dangerously_bypass=False.
# - ask_for_approval="never": used only when dangerously_bypass=False.
# - dangerously_bypass=True: add --dangerously-bypass-approvals-and-sandbox.
# - model=None: add `--model` if set.
# - profile=None: add `--profile` if set.
# - config=None: repeatable `--config key=value` values.
# - enable=None: repeatable `--enable FEATURE` values.
# - disable=None: repeatable `--disable FEATURE` values.
# - images=None: repeatable `--image PATH` values.
# - oss=False: add `--oss` if True.
# - local_provider=None: add `--local-provider` if set.
# - full_auto=False: add `--full-auto` if True.
# - skip_git_repo_check=False: add `--skip-git-repo-check` if True.
# - add_dir=None: repeatable `--add-dir PATH` values.
# - output_schema=None: add `--output-schema PATH` if set.
# - output_last_message=None: add `--output-last-message PATH` if set.
# - json_output=False: add `--json` if True.
# - color=None: add `--color` if set.
# - extra_args=None: appended as-is to the codex command.
# - check=True: raise on non-zero exit after logging.
# - text=True: run subprocess in text mode.
# - input_text=None: send this string to stdin.
# - env=None: defaults to os.environ copy.
# - show_cmd=True: print the command before running.
