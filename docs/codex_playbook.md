# docs/codex_playbook.md

This is a playbook for running and iterating the RoboTwin 2.0 pipeline.

---

## A. Core Constraints (Summary)
- No sudo.
- No destructive commands.
- Do not modify pre-existing files; use **copy → modify new file → redirect call**.
- Stay inside repo root.
- Use RUNID everywhere; keep `worklog_<RUNID>.md` updated.

How to change behavior without editing existing files:
Do not edit any pre-existing file. If you need to change a called script/config, first copy it to a new RUNID-suffixed file and modify the copy; then copy the upstream entry/caller and update it to reference the new file.
Example: if the original flow is c.sh -> a.py, create b.py (copied from a.py and modified), then create d.sh (copied from c.sh and updated to call b.py). This satisfies “no changes to old files; only add new files.”

---

## B. RUNID & Record Templates (Recommended Practice)

### B1) Worklog template (copy into `worklog_<RUNID>.md`)
## Run <RUNID>
### Objective
- Task:
- Metrics:
- Constraints:
  (If not, fill in null)

### Environment
- Host:
- GPU:
- Conda env:
- Key paths:

### New files/dirs created
- (path) — purpose

### Commands executed
- (command)
- (command)

### Logs & PIDs
- (log path) — (pid) — what it is

### Artifacts (Recommended Practice)
- Raw data:
- Processed data:
- Checkpoints:
- Eval outputs:

### Notes / Issues (Recommended Practice, Brief description)
- Error:
- Fix:
- Reference (see docs/cache/...):

---

### B2) Web refs template (copy into `docs/cache/web_refs_<RUNID>_NN.md`) (Recommended Practice, Brief description)
## Web refs <RUNID>_<NN>
### Topic / error
- What I was solving:

### Links
- (link) — why it matters
- (link) — why it matters

### Key takeaways
- Bullet points

---

## C. Change Strategy: “Copy in-place” (Recommended Practice)
Because pre-existing files cannot be edited, follow this pattern:

1) Identify a config/script you want to change:
- e.g., `task_config/<base>.yml`, `train.sh`, `eval_policy.py`

2) Copy it **in the same directory** and add RUNID suffix:
- `cp task_config/<base>.yml task_config/<base>__r<RUNID>.yml`

3) Modify only the new file:
- change episode_num / domain_randomization / seed / ckpt_dir, etc.

4) Do the same for the superior file (the file that calls this file); at this point, the call in the superior file should point to the new file

How to change behavior without editing existing files:
Do not edit any pre-existing file. If you need to change a called script/config, first copy it to a new RUNID-suffixed file and modify the copy; then copy the upstream entry/caller and update it to reference the new file.
Example: if the original flow is c.sh -> a.py, create b.py (copied from a.py and modified), then create d.sh (copied from c.sh and updated to call b.py). This satisfies “no changes to old files; only add new files.”

---

## E. nohup Patterns (Examples) (Recommended Practice)
### E1) nohup for training
nohup bash train__r<RUNID>.sh > logs/train__r<RUNID>.log 2>&1 & echo $! > logs/train__r<RUNID>.pid

### E2) monitor
tail -f logs/train__r<RUNID>.log
cat logs/train__r<RUNID>.pid
ps -fp $(cat logs/train__r<RUNID>.pid)

Record the command/log/pid in `worklog_<RUNID>.md`.

---

## F. Recommended Git Self-Checks (Non-blocking) (Recommended Practice)
- `git status --porcelain`
- `git diff --name-only`

If you accidentally modified an existing file:
- revert it, then re-apply changes via Copy in-place.
