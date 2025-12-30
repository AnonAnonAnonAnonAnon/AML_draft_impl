#!/usr/bin/env bash
set -e

# Usage:
#   bash full_pipeline/runs/act_20251230_141520/launch_nohup_act_20251230_141520.sh \
#     <task_name> <task_config> <expert_data_num> <seed> <gpu_id> [eval_test_num]

TASK_NAME="${1:?task_name required}"
TASK_CONFIG="${2:?task_config required}"
EXPERT_DATA_NUM="${3:?expert_data_num required}"
SEED="${4:?seed required}"
GPU_ID="${5:?gpu_id required}"
EVAL_TEST_NUM="${6:-100}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "${REPO_ROOT}"

mkdir -p full_pipeline/logs

LOG_FILE="full_pipeline/logs/act_${TASK_NAME}_${TASK_CONFIG}_n${EXPERT_DATA_NUM}_s${SEED}_g${GPU_ID}__r20251230_141520.log"

export PYTHONUNBUFFERED=1

nohup python -u "full_pipeline/runs/act_20251230_141520/run_robotwin_act_20251230_141520.py" \
  --task_name "${TASK_NAME}" \
  --task_config "${TASK_CONFIG}" \
  --expert_data_num "${EXPERT_DATA_NUM}" \
  --seed "${SEED}" \
  --gpu_id "${GPU_ID}" \
  --eval_test_num "${EVAL_TEST_NUM}" \
  > "${LOG_FILE}" 2>&1 &

PID=$!

echo "[LAUNCHED]"
echo "  RUN_ID=20251230_141520"
echo "  RUN_DIR=full_pipeline/runs/act_20251230_141520"
echo "  PID=${PID}"
echo "  LOG=${LOG_FILE}"
echo "  MONITOR: tail -f ${LOG_FILE}"

