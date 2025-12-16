#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import subprocess

# ============================================================
# CONFIG：你只改这里
# ============================================================

TASK_NAME = "beat_block_hammer"

# 常改：1
# 选择你要用的配置：
# - "smoke_seed"：最快，只验证 collect 能跑通，不生成 hdf5（不能跑 ACT）
# - "smoke_act" ：会生成 hdf5，可继续跑 ACT process/train
TASK_CONFIG = "smoke_act"

GPU_ID = "0"

# 常改：2
# 分阶段开关
RUN_COLLECT = True
RUN_ACT_PROCESS = True
RUN_ACT_TRAIN = True
RUN_ACT_EVAL = True

# ACT 相关（只有在 TASK_CONFIG="smoke_act" 且 collect_data=true 且 episode_num>=expert 才能跑）
EXPERT_DATA_NUM = 2
SEED = 0
TRAIN_SCRIPT = "train_smoke.sh"  # 位于 policy/ACT/
EVAL_SCRIPT  = "eval_smoke.sh"   # 位于 policy/ACT/
CKPT_SETTING = TASK_CONFIG       # 建议就用同名，方便对齐 ckpt_dir 规则

# ============================================================
# 实现：尽量薄
# ============================================================

REPO_ROOT = Path(__file__).resolve().parent
ACT_DIR = REPO_ROOT / "policy" / "ACT"

def run(cmd, cwd):
    print(f"\n[RUN] (cwd={cwd})\n  " + " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd), check=True)

def main():
    # 轻量存在性检查（避免跑半天才报路径错）
    assert (REPO_ROOT / "collect_data.sh").exists(), "请把 run_robotwin_smoke.py 放到 RoboTwin 仓库根目录（与 collect_data.sh 同级）"
    assert (REPO_ROOT / "task_config" / f"{TASK_CONFIG}.yml").exists(), f"缺少 task_config/{TASK_CONFIG}.yml"
    if RUN_ACT_TRAIN:
        assert (ACT_DIR / TRAIN_SCRIPT).exists(), f"缺少 policy/ACT/{TRAIN_SCRIPT}"
    if RUN_ACT_EVAL:
        assert (ACT_DIR / EVAL_SCRIPT).exists(), f"缺少 policy/ACT/{EVAL_SCRIPT}"

    if RUN_COLLECT:
        run(["bash", "collect_data.sh", TASK_NAME, TASK_CONFIG, GPU_ID], cwd=REPO_ROOT)

    if RUN_ACT_PROCESS:
        run(["bash", "process_data.sh", TASK_NAME, TASK_CONFIG, str(EXPERT_DATA_NUM)], cwd=ACT_DIR)

    if RUN_ACT_TRAIN:
        run(["bash", TRAIN_SCRIPT, TASK_NAME, TASK_CONFIG, str(EXPERT_DATA_NUM), str(SEED), GPU_ID], cwd=ACT_DIR)

    if RUN_ACT_EVAL:
        run(["bash", EVAL_SCRIPT, TASK_NAME, TASK_CONFIG, CKPT_SETTING, str(EXPERT_DATA_NUM), str(SEED), GPU_ID], cwd=ACT_DIR)

    print("\n[DONE] smoke pipeline finished.")

if __name__ == "__main__":
    main()
