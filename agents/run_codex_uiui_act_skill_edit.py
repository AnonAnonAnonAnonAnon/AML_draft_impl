#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
from pathlib import Path

# ============================================================
# CONFIG (ALL tunables are here)
# ============================================================

# Repo / Codex
REPO_ROOT = Path(__file__).resolve().parents[1]           # .../AML_draft_impl
CODEX_HOME = REPO_ROOT / ".codex_uiui"                    # reuse your working UIUI codex config dir

# Codex command (choose ONE)
USE_NPX = True
CODEX_CMD = ["npx", "codex"] if USE_NPX else ["codex"]

# Auth
# - Recommended: leave UIUI_KEY="" and export UIUI_API_KEY in shell
# - Fastest: hardcode here (NOT recommended for repo hygiene)
UIUI_KEY = "sk-SpkJBkL1Ti1X7RKwQbBotgmTUDA4xzJFJM9VQmIqyYQwVJYf"  # set "" to use env only
UIUI_ENV_KEY_NAME = "UIUI_API_KEY"

# Skill + run args
SKILL_NAME = "robotwin-act-perrun"
TASK_NAME = "beat_block_hammer"
BASE_CONFIG = "demo_clean"
EXPERT_DATA_NUM = 50
SEED = 0
GPU_ID = 7

# Execution policy (pick ONE mode)
# Mode A: safest sandboxed automation
USE_FULL_AUTO = True                 # uses "--full-auto" (still sandboxed)
SANDBOX_MODE = "workspace-write"     # only used when USE_FULL_AUTO=False
APPROVAL_POLICY = "untrusted"        # only used when USE_FULL_AUTO=False

# Mode B: no sandbox (what you used to succeed). Highest risk.
BYPASS_SANDBOX_AND_APPROVALS = True  # uses "--dangerously-bypass-approvals-and-sandbox"

# ====== OVERRIDES (this is the key part for Plan A) ======
# If empty -> Codex will just run the existing launch_nohup.sh (simple mode).
# If non-empty -> Codex will:
#   1) create_run_scaffold.sh (capture RUN_ID/TASK_CONFIG/RUN_DIR/RUNNER_PY)
#   2) patch ONLY newly created files according to these instructions
#   3) nohup python -u RUNNER_PY ... (do NOT call launch_nohup.sh again)
OVERRIDE_INSTRUCTIONS = [
    "In task_config YAML: set domain_randomization.random_light=true",
]


# Optional: ask Codex to verify changes before launch (recommended)
VERIFY_BEFORE_LAUNCH = True

# ============================================================
# Implementation (keep thin)
# ============================================================

def _ensure_key(env: dict) -> None:
    if UIUI_KEY.strip():
        env[UIUI_ENV_KEY_NAME] = UIUI_KEY
        return
    if UIUI_ENV_KEY_NAME not in env or not env[UIUI_ENV_KEY_NAME].strip():
        raise SystemExit(
            f"Missing env {UIUI_ENV_KEY_NAME}. Either set UIUI_KEY in CONFIG, "
            f"or run: export {UIUI_ENV_KEY_NAME}=..."
        )

def _build_prompt() -> str:
    safety = (
        "Follow the skill safety rules strictly: "
        "no sudo/su/apt; do not modify/delete any pre-existing files; "
        "only create/modify per-run files using RUN_ID; never overwrite artifacts.\n"
    )

    # Simple mode: call launch_nohup.sh directly
    if not OVERRIDE_INSTRUCTIONS:
        return (
            f"Use ${SKILL_NAME}.\n"
            f"{safety}"
            "Now launch one ACT full run:\n"
            f"  bash .codex/skills/{SKILL_NAME}/scripts/launch_nohup.sh "
            f"{TASK_NAME} {BASE_CONFIG} {EXPERT_DATA_NUM} {SEED} {GPU_ID}\n"
            "After launching, print RUN_ID, TASK_CONFIG, RUN_DIR, PID, LOG, and the exact tail -f command.\n"
        )

    # Override mode (Plan A): scaffold -> patch -> nohup runner
    overrides_text = "\n".join([f"- {x}" for x in OVERRIDE_INSTRUCTIONS])

    verify_text = ""
    if VERIFY_BEFORE_LAUNCH:
        verify_text = (
            "Before launch, verify the overrides took effect by printing the relevant lines "
            "from the newly created files (grep/cat), ONLY for this run's files.\n"
        )

    return (
        f"Use ${SKILL_NAME}.\n"
        f"{safety}"
        "User overrides for this run (apply before launch, edit ONLY newly created per-run files):\n"
        f"{overrides_text}\n"
        "\n"
        "Procedure (MUST follow exactly; DO NOT generate a second RUN_ID):\n"
        "1) Run create_run_scaffold.sh to generate per-run files and capture outputs.\n"
        "   Command:\n"
        f"     bash .codex/skills/{SKILL_NAME}/scripts/create_run_scaffold.sh "
        f"{TASK_NAME} {BASE_CONFIG} {EXPERT_DATA_NUM} {SEED} {GPU_ID}\n"
        "   Note: the script prints an extra '[PATCHED] ...' line. Use the LAST 4 lines as:\n"
        "     RUN_ID, TASK_CONFIG, RUN_DIR, RUNNER_PY.\n"
        "2) Apply overrides by editing ONLY the newly created files for this RUN_ID.\n"
        f"{verify_text}"
        "3) Launch by running the RUNNER_PY directly with nohup (do NOT call launch_nohup.sh again).\n"
        "   - Use: nohup python -u <RUNNER_PY> ... > full_pipeline/logs/<log>.log 2>&1 &\n"
        "   - Pass eval_test_num via CLI if requested (avoid editing runner when possible).\n"
        "4) Print final: RUN_ID, TASK_CONFIG, RUN_DIR, PID, LOG, and exact tail -f command.\n"
    )

def main():
    env = os.environ.copy()
    env["CODEX_HOME"] = str(CODEX_HOME)
    _ensure_key(env)

    prompt = _build_prompt()

    cmd = CODEX_CMD + ["exec", "--cd", str(REPO_ROOT)]

    if BYPASS_SANDBOX_AND_APPROVALS:
        cmd += ["--dangerously-bypass-approvals-and-sandbox"]
    else:
        if USE_FULL_AUTO:
            # still sandboxed; fewer prompts
            cmd += ["--full-auto"]
        else:
            cmd += ["--sandbox", SANDBOX_MODE, "--ask-for-approval", APPROVAL_POLICY]

    cmd += [prompt]

    print("[CMD]", " ".join(map(str, cmd)), flush=True)
    print("[CODEX_HOME]", env.get("CODEX_HOME", ""), flush=True)
    subprocess.run(cmd, env=env, check=True)

if __name__ == "__main__":
    main()