#!/bin/bash
# Smoke version of train.sh: minimal epochs / frequent checkpointing

task_name=${1}
task_config=${2}
expert_data_num=${3}
seed=${4}
gpu_id=${5}

export CUDA_VISIBLE_DEVICES=${gpu_id}

python3 imitate_episodes.py \
    --task_name sim-${task_name}-${task_config}-${expert_data_num} \
    --ckpt_dir ./act_ckpt/act-${task_name}/${task_config}-${expert_data_num} \
    --policy_class ACT \
    --kl_weight 10 \
    --chunk_size 50 \
    --hidden_dim 512 \
    --batch_size 2 \
    --dim_feedforward 3200 \
    --num_epochs 2 \
    --lr 1e-5 \
    --save_freq 1 \
    --state_dim 14 \
    --seed ${seed}
