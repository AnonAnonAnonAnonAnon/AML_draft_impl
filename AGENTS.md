# AGENTS.md

Please note that this agent.md describes guidelines for performing automated manipulation learning tasks, which is also the task of this project; when assisting users with other routine development tasks, the content here may not be very helpful. You should follow the user's instructions and learn to distinguish between these two types of calls.

## 0. Mission
You are the executor for this repository. Your goal is to run the full RoboTwin 2.0 pipeline end-to-end:
**Data Collection → Data Processing → Training → Evaluation**, iterating until it works.

Default to using ACT for the policy choice, unless there are other relevant requirements.

This repo is research/engineering code. The instructions and examples may be incomplete or wrong.
When you hit errors, **explore and debug autonomously**. Prefer an incremental approach:
start from minimal smoke tests, then scale up.

---

### 0.1 Documentation Entry Points (Read first / consult as needed)
To keep this file short, extended guidance and navigation are split into `docs/`:

- **Execution Playbook**: `docs/codex_playbook.md`  
  Includes: RUNID/record templates, nohup guidance, debugging order, and common self-check commands.

- **Pipeline Map**: `docs/robowin_pipeline_map.md`  
  Includes: entry-point hints for each pipeline stage (collect/process/train/eval), pointers to key configs, artifact location guidelines, and a quick repo-search checklist (`rg/find`) to discover entry points.

## 1. Non-negotiable Safety Rules (Hard Constraints)
1) **No sudo**. Do not run `sudo` or any command requiring elevated privileges.

2) **No destructive commands** (including equivalents). Examples (non-exhaustive):
- `rm -rf` on broad paths (repo root, parent dirs, `~`, `/`, glob-heavy deletes)
- `mkfs`, `dd`, `chmod -R`, `chown -R`, disk/partition tools
- Overwriting unknown files with `> somefile` unless the file is newly created by you in this run

3) **Do NOT modify any pre-existing file** (anything that existed before this run began).
- Allowed: create new files/dirs; copy an existing file to a new file; edit the new file.
- If you need to “change a call-site”, do it via a **new wrapper script/config** and use that wrapper for execution.

How to change behavior without editing existing files:
Do not edit any pre-existing file. If you need to change a called script/config, first copy it to a new RUNID-suffixed file and modify the copy; then copy the upstream entry/caller and update it to reference the new file.
Example: if the original flow is c.sh -> a.py, create b.py (copied from a.py and modified), then create d.sh (copied from c.sh and updated to call b.py). This satisfies “no changes to old files; only add new files.”

4) **Stay inside repo root**.
- Do not read/write outside this repository (no `/etc`, `~/.ssh`, system dirs, other repos).
- Use web search only via your built-in search tool, and cache key findings to docs (see below).

---

## 2. RUN Protocol (Recommended Approach)
At the start of each run, generate a RUNID:
- Format: `YYYYMMDD_HHMMSS` (UTC+8)
- Use RUNID in names of all new files you create, e.g. `*_RUNID.*` or `*__rRUNID.*`

You must produce two kinds of records:

### 2.1 Worklog (required)
Create `worklog_<RUNID>.md` in repo root, and keep it updated.
It must include:
- Objective & constraints (task, metrics, resources)
- Commands executed (copy/paste exact commands)
- Newly created files/dirs list (paths + purpose)
- Logs & PIDs (if nohup)
- Artifacts locations: dataset/processed_data/ckpt/eval outputs

### 2.2 Web search cache (Recommended Practice)
Create at least one cache file under `docs/cache/`, for example:
- `docs/cache/web_refs_<RUNID>.md`

If the content is large, you may create multiple files, e.g.:
- `docs/cache/web_refs_<RUNID>_01.md`
- `docs/cache/web_refs_<RUNID>_02.md`

Each cache file should include:
- Links + short notes
- What problem it solved / which error message it relates to
- Any concrete command/config snippet you applied

### 2.3 About Environment and Download

Please note that the environment has already been largely set up and can run the full RoboTwin 2.0 end-to-end pipeline for both ACT and DP.

Therefore, in most cases, you likely do not need to re-download all environments and assets exactly as described in the RoboTwin 2.0 documentation.

You can try running with my existing environment first.

The current environment is the conda environment `aml`.

To activate it:

```bash
conda activate aml
```

Generally speaking, before asking you to work, I will activate the environment first. You can proceed directly.



---

## 3. Execution for Long Runs (Recommended Practice)
This pipeline can take hours. Prefer robust execution:
- Use `nohup` for long training/eval jobs.
- Record the exact nohup command, log path, and PID to `worklog_<RUNID>.md`.
- Periodically check progress via `tail -f <log>` or targeted `grep`.

---

## 4. Recommended Self-Checks (Recommended Practice)
You should *often* sanity-check that you did not modify pre-existing files.
Recommended commands:
- `git status --porcelain`
- `git diff --name-only`
- `git diff` (ensure no edits to existing files)
- `git ls-files --others --exclude-standard` (list newly added files)

If any existing file was modified, stop and fix by reverting, then proceed using new copies/wrappers.


