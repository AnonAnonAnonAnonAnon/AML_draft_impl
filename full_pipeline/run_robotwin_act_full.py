#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import subprocess

TASK_NAME = "beat_block_hammer"
TASK_CONFIG = "act_full_12211636"   # 你手动改：对应 task_config/*.yml
GPU_ID = "6"

RUN_COLLECT = True
RUN_ACT_PROCESS = True
RUN_ACT_TRAIN = True
RUN_ACT_EVAL = True

EXPERT_DATA_NUM = 50
SEED = 0

PROCESS_SCRIPT = "process_full.sh"
TRAIN_SCRIPT = "train_full.sh"
EVAL_SCRIPT  = "eval_full.sh"
CKPT_SETTING = TASK_CONFIG
EVAL_TEST_NUM = 100

# REPO_ROOT = Path(__file__).resolve().parent
# ACT_DIR = REPO_ROOT / "policy" / "ACT"

SCRIPT_DIR = Path(__file__).resolve().parent          # .../full_pipeline
REPO_ROOT  = SCRIPT_DIR.parent                        # .../AML_draft_impl
ACT_DIR    = REPO_ROOT / "policy" / "ACT"

LOG_DIR = SCRIPT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def run(cmd, cwd):
    print(f"\n[RUN] (cwd={cwd})\n  " + " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd), check=True)

def main():
    if RUN_COLLECT:
        run(["bash", "collect_data.sh", TASK_NAME, TASK_CONFIG, GPU_ID], cwd=REPO_ROOT)

    if RUN_ACT_PROCESS:
        run(["bash", PROCESS_SCRIPT, TASK_NAME, TASK_CONFIG, str(EXPERT_DATA_NUM)], cwd=ACT_DIR)

    if RUN_ACT_TRAIN:
        run(["bash", TRAIN_SCRIPT, TASK_NAME, TASK_CONFIG, str(EXPERT_DATA_NUM), str(SEED), GPU_ID], cwd=ACT_DIR)

    if RUN_ACT_EVAL:
        run(["bash", EVAL_SCRIPT, TASK_NAME, TASK_CONFIG, CKPT_SETTING, str(EXPERT_DATA_NUM), str(SEED), GPU_ID, str(EVAL_TEST_NUM)], cwd=ACT_DIR)

    print("\n[DONE] full ACT pipeline finished.")

if __name__ == "__main__":
    main()
