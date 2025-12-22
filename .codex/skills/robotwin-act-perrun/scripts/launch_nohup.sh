#!/usr/bin/env bash
set -e

TASK_NAME="${1:?task_name required}"
BASE_CONFIG="${2:?base_config required}"
EXPERT_DATA_NUM="${3:?expert_data_num required}"
SEED="${4:?seed required}"
GPU_ID="${5:?gpu_id required}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../" && pwd)"
cd "${REPO_ROOT}"

mkdir -p full_pipeline/logs

# Create per-run files and capture outputs
OUT="$(
  bash .codex/skills/robotwin-act-perrun/scripts/create_run_scaffold.sh \
    "${TASK_NAME}" "${BASE_CONFIG}" "${EXPERT_DATA_NUM}" "${SEED}" "${GPU_ID}"
)"

RUN_ID="$(echo "${OUT}" | sed -n '1p')"
TASK_CONFIG="$(echo "${OUT}" | sed -n '2p')"
RUN_DIR="$(echo "${OUT}" | sed -n '3p')"
RUNNER_PY="$(echo "${OUT}" | sed -n '4p')"

LOG_FILE="full_pipeline/logs/act_${TASK_NAME}_${TASK_CONFIG}_n${EXPERT_DATA_NUM}_s${SEED}_g${GPU_ID}.log"

export PYTHONUNBUFFERED=1

nohup python -u "${RUNNER_PY}" \
  --task_name "${TASK_NAME}" \
  --task_config "${TASK_CONFIG}" \
  --expert_data_num "${EXPERT_DATA_NUM}" \
  --seed "${SEED}" \
  --gpu_id "${GPU_ID}" \
  --eval_test_num 100 \
  > "${LOG_FILE}" 2>&1 &

PID=$!

echo "[LAUNCHED]"
echo "  RUN_ID=${RUN_ID}"
echo "  TASK_CONFIG=${TASK_CONFIG}"
echo "  RUN_DIR=${RUN_DIR}"
echo "  PID=${PID}"
echo "  LOG=${LOG_FILE}"
echo "  MONITOR: tail -f ${LOG_FILE}"
