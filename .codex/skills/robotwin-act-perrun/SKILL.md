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

## Customization (MUST do before launch if user provides overrides)
If the user provides any parameter overrides, you MUST:
1) Run:
   bash .codex/skills/robotwin-act-perrun/scripts/create_run_scaffold.sh <task> <base_config> <n> <seed> <gpu>
   and capture outputs: RUN_ID, TASK_CONFIG, RUN_DIR, RUNNER_PY.
2) Apply overrides ONLY by editing files created in this run:
   - task_config/<TASK_CONFIG>.yml
   - full_pipeline/runs/act_<RUN_ID>/*.sh
   - script/eval_policy_act_<RUN_ID>.py
   - full_pipeline/runs/act_<RUN_ID>/run_robotwin_act_<RUN_ID>.py
   Never touch any pre-existing files.
3) After edits, launch:
   bash .codex/skills/robotwin-act-perrun/scripts/launch_nohup.sh <task> <base_config> <n> <seed> <gpu>

When editing, prefer minimal surgical changes:
- YAML: change only the specified keys.
- Shell/Python: change only explicitly requested parameters.
- Print final RUN_ID/TASK_CONFIG/RUN_DIR/PID/LOG/tail command.

