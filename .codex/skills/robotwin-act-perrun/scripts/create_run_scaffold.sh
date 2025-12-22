#!/usr/bin/env bash
set -e

TASK_NAME="${1:?task_name required}"
BASE_CONFIG="${2:?base_config required}"
EXPERT_DATA_NUM="${3:?expert_data_num required}"
SEED="${4:?seed required}"
GPU_ID="${5:?gpu_id required}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../" && pwd)"
cd "${REPO_ROOT}"

RUN_ID="$(TZ=Asia/Shanghai date +%Y%m%d_%H%M%S)"
RUN_DIR="full_pipeline/runs/act_${RUN_ID}"

mkdir -p "${RUN_DIR}"
mkdir -p full_pipeline/logs

TASK_CONFIG="act_full_${RUN_ID}"
TASK_CONFIG_FILE="task_config/${TASK_CONFIG}.yml"

EVAL_PY="script/eval_policy_act_${RUN_ID}.py"
PROCESS_SH="${RUN_DIR}/process_act_${RUN_ID}.sh"
TRAIN_SH="${RUN_DIR}/train_act_${RUN_ID}.sh"
EVAL_SH="${RUN_DIR}/eval_act_${RUN_ID}.sh"
RUNNER_PY="${RUN_DIR}/run_robotwin_act_${RUN_ID}.py"

# 1) task_config/act_full_${RUN_ID}.yml
if [ -e "${TASK_CONFIG_FILE}" ]; then
  echo "[ERROR] ${TASK_CONFIG_FILE} already exists. Refusing to overwrite."
  exit 1
fi
cp "task_config/${BASE_CONFIG}.yml" "${TASK_CONFIG_FILE}"

# 2) process_act_${RUN_ID}.sh (copy from policy/ACT/process_data.sh)
if [ -e "${PROCESS_SH}" ]; then
  echo "[ERROR] ${PROCESS_SH} already exists. Refusing to overwrite."
  exit 1
fi
cp "policy/ACT/process_data.sh" "${PROCESS_SH}"

# 3) train_act_${RUN_ID}.sh (copy from policy/ACT/train.sh)
if [ -e "${TRAIN_SH}" ]; then
  echo "[ERROR] ${TRAIN_SH} already exists. Refusing to overwrite."
  exit 1
fi
cp "policy/ACT/train.sh" "${TRAIN_SH}"

# 4) script/eval_policy_act_${RUN_ID}.py (copy from smoke, patch only this new file)
if [ -e "${EVAL_PY}" ]; then
  echo "[ERROR] ${EVAL_PY} already exists. Refusing to overwrite."
  exit 1
fi
cp "script/eval_policy_smoke.py" "${EVAL_PY}"

python - <<PY_PATCH
from pathlib import Path
p = Path("${EVAL_PY}")
txt = p.read_text(encoding="utf-8")

txt = txt.replace('test_num = int(usr_args.get("test_num", 2))',
                  'test_num = int(usr_args.get("test_num", 100))')

txt = txt.replace('strftime("%Y-%m-%d %H:%M:%S")',
                  'strftime("%Y%m%d_%H%M%S")')

p.write_text(txt, encoding="utf-8")
import sys
print("[PATCHED]", p, file=sys.stderr)
PY_PATCH

# 5) eval_act_${RUN_ID}.sh (new file, calls the per-run eval python)
if [ -e "${EVAL_SH}" ]; then
  echo "[ERROR] ${EVAL_SH} already exists. Refusing to overwrite."
  exit 1
fi

cat > "${EVAL_SH}" <<EOF_EVAL
#!/usr/bin/env bash
set -e

# Args:
#   1 task_name
#   2 task_config
#   3 ckpt_setting
#   4 expert_data_num
#   5 seed
#   6 gpu_id
#   7 test_num (optional, default 100)

policy_name=ACT
task_name=\${1}
task_config=\${2}
ckpt_setting=\${3}
expert_data_num=\${4}
seed=\${5}
gpu_id=\${6}
test_num=\${7:-100}

export CUDA_VISIBLE_DEVICES=\${gpu_id}
echo -e "\\033[33mgpu id (to use): \${gpu_id}\\033[0m"

cd "${REPO_ROOT}"

PYTHONWARNINGS=ignore::UserWarning \\
python "${EVAL_PY}" --config policy/\${policy_name}/deploy_policy.yml \\
  --overrides \\
  --task_name \${task_name} \\
  --task_config \${task_config} \\
  --ckpt_setting \${ckpt_setting} \\
  --ckpt_dir policy/ACT/act_ckpt/act-\${task_name}/\${ckpt_setting}-\${expert_data_num} \\
  --seed \${seed} \\
  --temporal_agg true \\
  --test_num \${test_num}
EOF_EVAL

# 6) run_robotwin_act_${RUN_ID}.py (new file; sets cwd internally, you don't need to know cwd)
if [ -e "${RUNNER_PY}" ]; then
  echo "[ERROR] ${RUNNER_PY} already exists. Refusing to overwrite."
  exit 1
fi

cat > "${RUNNER_PY}" <<PY_RUNNER
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import subprocess
from pathlib import Path

def run(cmd, cwd: Path):
    print(f"\\n[RUN] (cwd={cwd})\\n  " + " ".join(cmd), flush=True)
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
    run(["bash", str((repo_root / "${PROCESS_SH}").resolve()),
         args.task_name, args.task_config, str(args.expert_data_num)], cwd=act_dir)

    # 3) train (cwd=policy/ACT)
    run(["bash", str((repo_root / "${TRAIN_SH}").resolve()),
         args.task_name, args.task_config, str(args.expert_data_num), str(args.seed), args.gpu_id], cwd=act_dir)

    # 4) eval (ckpt_setting == task_config; cwd=policy/ACT)
    ckpt_setting = args.task_config
    run(["bash", str((repo_root / "${EVAL_SH}").resolve()),
         args.task_name, args.task_config, ckpt_setting,
         str(args.expert_data_num), str(args.seed), args.gpu_id, str(args.eval_test_num)], cwd=act_dir)

    print("\\n[DONE] per-run ACT pipeline finished.", flush=True)

if __name__ == "__main__":
    main()
PY_RUNNER

chmod +x "${PROCESS_SH}" "${TRAIN_SH}" "${EVAL_SH}" "${RUNNER_PY}"

# Return 4 lines for the launcher to parse
echo "${RUN_ID}"
echo "${TASK_CONFIG}"
echo "${RUN_DIR}"
echo "${RUNNER_PY}"
