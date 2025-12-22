#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import subprocess
from pathlib import Path

def run(cmd, cwd: Path):
    print(f"\n[RUN] (cwd={cwd})\n  " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=str(cwd), check=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task_name", required=True)
    p.add_argument("--task_config", required=True)
    p.add_argument("--expert_data_num", type=int, required=True)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--gpu_id", required=True)
    p.add_argument("--eval_test_num", type=int, default=100)
    args = p.parse_args()

    runner_file = Path(__file__).resolve()
    run_dir = runner_file.parent
    repo_root = run_dir.parent.parent.parent  # .../AML_draft_impl

    # 1) collect (repo root)
    run(["bash", "collect_data.sh", args.task_name, args.task_config, args.gpu_id], cwd=repo_root)

    # 2) process (execute script from run_dir, but cwd=policy/ACT)
    act_dir = repo_root / "policy" / "ACT"
    run(["bash", str((repo_root / "full_pipeline/runs/act_20251222_140535/process_act_20251222_140535.sh").resolve()),
         args.task_name, args.task_config, str(args.expert_data_num)], cwd=act_dir)

    # 3) train (cwd=policy/ACT)
    run(["bash", str((repo_root / "full_pipeline/runs/act_20251222_140535/train_act_20251222_140535.sh").resolve()),
         args.task_name, args.task_config, str(args.expert_data_num), str(args.seed), args.gpu_id], cwd=act_dir)

    # 4) eval (ckpt_setting == task_config; cwd=policy/ACT)
    ckpt_setting = args.task_config
    run(["bash", str((repo_root / "full_pipeline/runs/act_20251222_140535/eval_act_20251222_140535.sh").resolve()),
         args.task_name, args.task_config, ckpt_setting,
         str(args.expert_data_num), str(args.seed), args.gpu_id, str(args.eval_test_num)], cwd=act_dir)

    print("\n[DONE] per-run ACT pipeline finished.", flush=True)

if __name__ == "__main__":
    main()
