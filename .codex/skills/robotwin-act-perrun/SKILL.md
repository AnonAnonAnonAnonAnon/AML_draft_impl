---
name: robotwin-act-perrun
description: Per run, create RUN_ID (Asia/Shanghai), generate 6 per-run ACT interface files (runner + 3 sh + task_config + eval python), then launch ACT pipeline via nohup with logs under full_pipeline/logs.
---

robotwin-act-perrun

Safety rules (MUST follow)
1) NEVER run sudo/su/apt or modify system settings.
2) NEVER modify or delete any file that existed before this run. Only create new files/directories.
3) NEVER overwrite existing artifacts. Always use a new RUN_ID and unique filenames.

Per-run files created
- full_pipeline/runs/act_${RUN_ID}/run_robotwin_act_${RUN_ID}.py
- full_pipeline/runs/act_${RUN_ID}/process_act_${RUN_ID}.sh
- full_pipeline/runs/act_${RUN_ID}/train_act_${RUN_ID}.sh
- full_pipeline/runs/act_${RUN_ID}/eval_act_${RUN_ID}.sh
- task_config/act_full_${RUN_ID}.yml
- script/eval_policy_act_${RUN_ID}.py

Launch command (manual)
bash .codex/skills/robotwin-act-perrun/scripts/launch_nohup.sh beat_block_hammer demo_clean 50 0 7

Args
1) task_name
2) base_config (task_config/<base_config>.yml)
3) expert_data_num
4) seed
5) gpu_id

Monitor
tail -f full_pipeline/logs/<logfile>.log
