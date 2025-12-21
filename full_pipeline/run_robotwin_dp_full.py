#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import subprocess

# =========================
# CONFIG：你只改这里
# =========================
TASK_NAME = "beat_block_hammer"
TASK_CONFIG = "dp_full_12212127"   # 对应 task_config/dp_full_12212230.yml
GPU_ID = "6"

RUN_COLLECT = True
RUN_DP_PROCESS = True
RUN_DP_TRAIN = True
RUN_DP_EVAL = True

EXPERT_DATA_NUM = 50
SEED = 0
ACTION_DIM = 14   # 你 primitive DP 已跑通用的就是 14

PROCESS_SCRIPT = "process_full.sh"  # policy/DP/
TRAIN_SCRIPT   = "train_full.sh"    # policy/DP/
EVAL_SCRIPT    = "eval_full.sh"     # policy/DP/
CKPT_SETTING   = TASK_CONFIG        # DP 的 ckpt_setting 通常就用 task_config
CHECKPOINT_NUM = 600                # 默认 600；若训练没跑完可改 300

# =========================
# Thin implementation
# =========================
SCRIPT_DIR = Path(__file__).resolve().parent          # .../full_pipeline
REPO_ROOT  = SCRIPT_DIR.parent                        # .../AML_draft_impl
DP_DIR     = REPO_ROOT / "policy" / "DP"

def run(cmd, cwd):
    print(f"\n[RUN] (cwd={cwd})\n  " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=str(cwd), check=True)

def main():
    # 最小存在性检查（避免路径错跑半天）
    assert (REPO_ROOT / "collect_data.sh").exists(), "REPO_ROOT 不对：找不到 collect_data.sh"
    assert (REPO_ROOT / "task_config" / f"{TASK_CONFIG}.yml").exists(), f"缺少 task_config/{TASK_CONFIG}.yml"
    assert (DP_DIR / PROCESS_SCRIPT).exists(), f"缺少 policy/DP/{PROCESS_SCRIPT}"
    assert (DP_DIR / TRAIN_SCRIPT).exists(), f"缺少 policy/DP/{TRAIN_SCRIPT}"
    assert (DP_DIR / EVAL_SCRIPT).exists(), f"缺少 policy/DP/{EVAL_SCRIPT}"

    if RUN_COLLECT:
        run(["bash", "collect_data.sh", TASK_NAME, TASK_CONFIG, GPU_ID], cwd=REPO_ROOT)

    if RUN_DP_PROCESS:
        run(["bash", PROCESS_SCRIPT, TASK_NAME, TASK_CONFIG, str(EXPERT_DATA_NUM)], cwd=DP_DIR)

    if RUN_DP_TRAIN:
        run(["bash", TRAIN_SCRIPT, TASK_NAME, TASK_CONFIG, str(EXPERT_DATA_NUM), str(SEED), str(ACTION_DIM), GPU_ID], cwd=DP_DIR)

    if RUN_DP_EVAL:
        # 如果你的 eval_full.sh 支持 checkpoint_num，就加上；否则去掉最后一个参数
        run(["bash", EVAL_SCRIPT, TASK_NAME, TASK_CONFIG, CKPT_SETTING, str(EXPERT_DATA_NUM), str(SEED), GPU_ID, str(CHECKPOINT_NUM)], cwd=DP_DIR)

    print("\n[DONE] full DP pipeline finished.", flush=True)

if __name__ == "__main__":
    main()
