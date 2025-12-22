#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
from pathlib import Path

# ============================================================
# CONFIG (ALL tunables are here)
# ============================================================

# Repo / Codex
REPO_ROOT = Path(__file__).resolve().parents[1]   # .../AML_draft_impl
CODEX_HOME = REPO_ROOT / ".codex_uiui"            # reuse your working UIUI codex config dir
CODEX_BIN = "codex"                               # or "npx", if you prefer

# Codex binary command (choose ONE)
USE_NPX = True
CODEX_CMD = ["npx", "codex"] if USE_NPX else ["codex"]


# Auth (choose ONE)
# Option A (fastest): hardcode key here (NOT recommended for repo hygiene)
UIUI_KEY = "sk-SpkJBkL1Ti1X7RKwQbBotgmTUDA4xzJFJM9VQmIqyYQwVJYf"  # e.g. "sk-xxxx"  (leave empty to use env var UIUI_API_KEY)

# Option B (recommended): export UIUI_API_KEY in shell before running this script
UIUI_ENV_KEY_NAME = "UIUI_API_KEY"

# Skill + ACT run args
SKILL_NAME = "robotwin-act-perrun"
TASK_NAME = "beat_block_hammer"
BASE_CONFIG = "demo_clean"
EXPERT_DATA_NUM = 50
SEED = 0
GPU_ID = 7

# Codex execution policy
SANDBOX_MODE = "workspace-write"      # must be workspace-write (skill creates files)
APPROVAL_POLICY = "untrusted"         # safer; change to "on-request"/"never" if you want less prompts
USE_FULL_AUTO = True                 # True -> add "--full-auto" instead of sandbox+approval flags

BYPASS_SANDBOX_AND_APPROVALS = True   # True -> use --dangerously-bypass-approvals-and-sandbox


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
from pathlib import Path

# ============================================================
# CONFIG (ALL tunables are here)
# ============================================================

REPO_ROOT = Path(__file__).resolve().parents[1]
CODEX_HOME = REPO_ROOT / ".codex_uiui"

# Codex command (choose ONE)
USE_NPX = True
CODEX_CMD = ["npx", "codex"] if USE_NPX else ["codex"]

UIUI_KEY = "sk-SpkJBkL1Ti1X7RKwQbBotgmTUDA4xzJFJM9VQmIqyYQwVJYf"  # leave "" to use env var
UIUI_ENV_KEY_NAME = "UIUI_API_KEY"

SKILL_NAME = "robotwin-act-perrun"
TASK_NAME = "beat_block_hammer"
BASE_CONFIG = "demo_clean"
EXPERT_DATA_NUM = 50
SEED = 0
GPU_ID = 7

SANDBOX_MODE = "workspace-write"
APPROVAL_POLICY = "untrusted"
USE_FULL_AUTO = True

BYPASS_SANDBOX_AND_APPROVALS = True

# ============================================================
# Implementation (keep thin)
# ============================================================

def main():
    env = os.environ.copy()
    env["CODEX_HOME"] = str(CODEX_HOME)

    if UIUI_KEY.strip():
        env[UIUI_ENV_KEY_NAME] = UIUI_KEY
    else:
        if UIUI_ENV_KEY_NAME not in env or not env[UIUI_ENV_KEY_NAME].strip():
            raise SystemExit(f"Missing env {UIUI_ENV_KEY_NAME}. export {UIUI_ENV_KEY_NAME}=...")

    prompt = (
        f"Use ${SKILL_NAME}.\n"
        "Follow the skill safety rules strictly: no sudo/su/apt; do not modify/delete any pre-existing files; "
        "only create new per-run files using RUN_ID.\n"
        "Now launch one ACT full run:\n"
        f"  bash .codex/skills/{SKILL_NAME}/scripts/launch_nohup.sh "
        f"{TASK_NAME} {BASE_CONFIG} {EXPERT_DATA_NUM} {SEED} {GPU_ID}\n"
        "After launching, print RUN_ID, TASK_CONFIG, RUN_DIR, PID, LOG, and the exact tail -f command.\n"
    )

    cmd = CODEX_CMD + ["exec", "--cd", str(REPO_ROOT)]

    if BYPASS_SANDBOX_AND_APPROVALS:
        cmd += ["--dangerously-bypass-approvals-and-sandbox"]
    else:
        if USE_FULL_AUTO:
            cmd += ["--full-auto"]
        else:
            cmd += ["--sandbox", SANDBOX_MODE, "--ask-for-approval", APPROVAL_POLICY]

    cmd += [prompt]

    print("[CMD]", " ".join(map(str, cmd)), flush=True)
    print("[CODEX_HOME]", env.get("CODEX_HOME", ""), flush=True)

    subprocess.run(cmd, env=env, check=True)

if __name__ == "__main__":
    main()
