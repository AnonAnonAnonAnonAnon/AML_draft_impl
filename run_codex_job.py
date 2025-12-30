#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_codex_job.py

Outer driver to launch Codex with a RUNID and capture *all* Codex output in a single log.
This version reuses your working UIUI Codex config directory via CODEX_HOME (= .codex_uiui).
"""

from __future__ import annotations

import os
import sys
import shlex
import subprocess
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIG (ALL tunables are here)
# ============================================================

# Repo root (assume this script sits in repo root)
REPO_ROOT = Path(__file__).resolve().parent

# Reuse your working UIUI codex config directory
CODEX_HOME = REPO_ROOT / ".codex_uiui"

# Codex command (choose ONE)
USE_NPX = True
CODEX_CMD = ["npx", "codex"] if USE_NPX else ["codex"]

# Auth
# Recommended: set UIUI_KEY="" and export UIUI_API_KEY in your shell
UIUI_KEY = "sk-c0sBK7t2p6LV84r5s7KUknm4BvzcEdiwjd3jRNE1IdV0Ero5"  # leave empty to use env only
UIUI_ENV_KEY_NAME = "UIUI_API_KEY"

# Execution policy (pick ONE)
BYPASS_SANDBOX_AND_APPROVALS = True  # uses "--dangerously-bypass-approvals-and-sandbox"
USE_FULL_AUTO = False                # if BYPASS is False, you can choose "--full-auto"
SANDBOX_MODE = "workspace-write"     # only used when BYPASS=False and USE_FULL_AUTO=False
APPROVAL_POLICY = "untrusted"        # only used when BYPASS=False and USE_FULL_AUTO=False

# Time / logs
TIMEZONE_UTC_OFFSET_HOURS = 8  # UTC+8
LOG_DIR = REPO_ROOT / "logs"
DOC_CACHE_DIR = REPO_ROOT / "docs" / "cache"
OUTER_LOG_PREFIX = "codex_outer"

# ------------------------------------------------------------
# Run-specific input (the concrete goal for this run)
# ------------------------------------------------------------
USER_REQUIREMENTS = r"""
制作一个策略，需要对光照变化有泛化能力：
- 默认 policy：ACT（除非用户另有要求）
- 默认任务：beat_block_hammer（除非用户另有要求）
- 关键要求：数据采集/任务配置中启用光照相关的域随机化（例如 domain_randomization.random_light=true）
- 其余配置保持默认（除非为满足该目标必须调整）

English summary:
Build a policy that generalizes to lighting changes.
Default policy: ACT. Default task: beat_block_hammer.
Key requirement: enable lighting domain randomization in data collection / task config
(e.g., domain_randomization.random_light=true).
Keep other settings default unless required.
"""

USER_TASK = rf"""
请运行 RoboTwin 2.0 全流程：采集 -> 处理 -> 训练 -> 评估。

【本次运行的具体用户需求 / 目标】
{USER_REQUIREMENTS}

严格遵守 AGENTS.md：
- 禁止 sudo
- 禁止危险/破坏性命令
- 不允许修改任何本次开始前就存在的文件（只能复制/新建带 RUNID 后缀的文件，然后在“新入口脚本/新配置”里改为引用这些新文件）
- 不得越界仓库根目录

请使用我提供的 RUNID 来命名你创建的所有新文件，并且必须创建：
- worklog_<RUNID>.md
- docs/cache/web_refs_<RUNID>.md（如内容较多允许拆分多个文件，例如 web_refs_<RUNID>_01.md, _02.md）

推荐自底向上调试：先做最小化 smoke test，再逐步扩大规模。
"""

# ============================================================
# Implementation (keep thin)
# ============================================================

def _ensure_dirs() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    DOC_CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _ensure_key(env: dict) -> None:
    if UIUI_KEY.strip():
        env[UIUI_ENV_KEY_NAME] = UIUI_KEY
        return
    if UIUI_ENV_KEY_NAME not in env or not env[UIUI_ENV_KEY_NAME].strip():
        raise SystemExit(
            f"Missing env {UIUI_ENV_KEY_NAME}. Either set UIUI_KEY in CONFIG, "
            f"or run: export {UIUI_ENV_KEY_NAME}=..."
        )

def _gen_runid() -> str:
    now = datetime.utcnow()
    ts = now.timestamp() + TIMEZONE_UTC_OFFSET_HOURS * 3600
    local = datetime.fromtimestamp(ts)
    return local.strftime("%Y%m%d_%H%M%S")

def _write_initial_worklog(runid: str) -> Path:
    path = REPO_ROOT / f"worklog_{runid}.md"
    if path.exists():
        return path
    path.write_text(
        f"""## Run {runid}
### 目标
- Task：RoboTwin 2.0 全流程（采集->处理->训练->评估）
- 指标：success rate、OOD success rate（如适用）
- 约束：禁 sudo；禁危险命令；不得修改旧文件；不得越界仓库根目录

### 本次用户需求 / 目标输入
{USER_REQUIREMENTS}

### 已执行命令
-（由 agent 填写）

### 本次新增文件/目录
-（由 agent 填写）

### 日志与 PID
- 外层 driver 日志：logs/{OUTER_LOG_PREFIX}_{runid}.log

### 产物定位（必须写清）
- Raw data：
- Processed data：
- Checkpoints：
- Eval outputs：

""",
        encoding="utf-8",
    )
    return path

def _build_codex_prompt(runid: str) -> str:
    return f"""RUNID={runid}

{USER_TASK}

请先阅读 AGENTS.md，然后在执行过程中持续创建/更新：worklog_{runid}.md。
"""

def main() -> int:
    _ensure_dirs()
    runid = _gen_runid()
    _write_initial_worklog(runid)

    outer_log = LOG_DIR / f"{OUTER_LOG_PREFIX}_{runid}.log"
    prompt = _build_codex_prompt(runid)

    env = os.environ.copy()
    env["CODEX_HOME"] = str(CODEX_HOME)
    _ensure_key(env)

    # Build command exactly like your working UIUI driver style:
    # npx codex exec --cd <repo> [flags] "<prompt>"
    cmd = CODEX_CMD + ["exec", "--cd", str(REPO_ROOT)]

    if BYPASS_SANDBOX_AND_APPROVALS:
        cmd += ["--dangerously-bypass-approvals-and-sandbox"]
    else:
        if USE_FULL_AUTO:
            cmd += ["--full-auto"]
        else:
            cmd += ["--sandbox", SANDBOX_MODE, "--ask-for-approval", APPROVAL_POLICY]

    cmd += [prompt]

    with outer_log.open("w", encoding="utf-8") as f:
        f.write(f"[RUNID] {runid}\n")
        f.write(f"[CWD] {REPO_ROOT}\n")
        f.write(f"[CODEX_HOME] {env.get('CODEX_HOME', '')}\n")
        f.write(f"[CMD] {' '.join(map(shlex.quote, cmd[:-1]))} <PROMPT_OMITTED>\n\n")
        f.flush()

        proc = subprocess.Popen(
            cmd,
            cwd=str(REPO_ROOT),
            env=env,
            stdout=f,
            stderr=subprocess.STDOUT,
            text=True,
        )
        f.write(f"\n[PID] {proc.pid}\n")
        f.flush()

        return proc.wait()

if __name__ == "__main__":
    sys.exit(main())
