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
task_name=${1}
task_config=${2}
ckpt_setting=${3}
expert_data_num=${4}
seed=${5}
gpu_id=${6}
test_num=${7:-100}

export CUDA_VISIBLE_DEVICES=${gpu_id}
echo -e "\033[33mgpu id (to use): ${gpu_id}\033[0m"

cd "/home/liwenbo/projects/AML/AML_draft_impl"

PYTHONWARNINGS=ignore::UserWarning \
python "script/eval_policy_act_20251222_144116.py" --config policy/${policy_name}/deploy_policy.yml \
  --overrides \
  --task_name ${task_name} \
  --task_config ${task_config} \
  --ckpt_setting ${ckpt_setting} \
  --ckpt_dir policy/ACT/act_ckpt/act-${task_name}/${ckpt_setting}-${expert_data_num} \
  --seed ${seed} \
  --temporal_agg true \
  --test_num ${test_num}
