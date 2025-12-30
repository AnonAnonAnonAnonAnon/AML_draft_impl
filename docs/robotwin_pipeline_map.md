# docs/robowin_pipeline_map.md

This is a map of the RoboTwin 2.0 pipeline inside this repo.

It briefly describes the core information of RoboTwin 2.0, including each pipeline stage and the basic call structure.

You are encouraged to further explore the repository on your own, or search online for the RoboTwin 2.0 documentation to learn more.

For example:

* [https://robotwin-platform.github.io/doc/index.html](https://robotwin-platform.github.io/doc/index.html)
* [https://robotwin-platform.github.io/doc/usage/collect-data.html](https://robotwin-platform.github.io/doc/usage/collect-data.html)
* [https://robotwin-platform.github.io/doc/usage/ACT.html](https://robotwin-platform.github.io/doc/usage/ACT.html)
* [https://robotwin-platform.github.io/doc/usage/configurations.html#24-data-collection-settings](https://robotwin-platform.github.io/doc/usage/configurations.html#24-data-collection-settings)


---

## 1) Pipeline Stages
### Stage 1: Data Collection 
Goal: Collect a specified amount of expert data

Example:

```bash
bash collect_data.sh ${task_name} ${task_config} ${gpu_id}
```

Clean data example:

```bash
bash collect_data.sh beat_block_hammer demo_clean 0
```

If you modify this script, you must copy it to a new file and run **your newly created script** instead of the original one.

`task_name` defaults to `beat_block_hammer`, but it should be selected based on user requirements when provided.

`task_config` defaults to `demo_clean`, but in practice it usually carries a RUNID suffix; use the exact name of the `task_config` file you created (typically matching the config name).

`gpu_id` defaults to `6`, but before each run it is recommended to check available GPUs with `nvidia-smi` to avoid CUDA out-of-memory errors.

ref: https://robotwin-platform.github.io/doc/usage/collect-data.html

---

### Stage 2: Data Processing (Convert to policy format, e.g., ACT/DP)

Goal: convert the collected data into a format that can be used to train a specific model.

This depends on the policy you plan to use, e.g., **ACT**.

By default, use **ACT** unless the user specifies otherwise.

If you decide to use this policy, first switch to the policy directory, for example:

```bash
cd policy/ACT
```

Then process the data.

Example:

```bash
bash process_data.sh ${task_name} ${task_config} ${expert_data_num}
```

```bash
bash process_data.sh beat_block_hammer demo_clean 50
```

If you modify this script, you must copy it to a new file and run **your newly created script** instead of the original one (though this is rarely needed).

`task_name` defaults to `beat_block_hammer`, but it should be selected based on user requirements when provided.

`task_config` defaults to `demo_clean`, but in practice it usually carries a RUNID suffix; use the exact name of the `task_config` file you created (typically matching the config name).

Ref: [https://robotwin-platform.github.io/doc/usage/ACT.html](https://robotwin-platform.github.io/doc/usage/ACT.html)

---

### Stage 3: Training

Goal: start the training process.

This is the next step after data processing and should follow the decisions and settings made in the previous stages.

Example:

```bash
bash train.sh ${task_name} ${task_config} ${expert_data_num} ${seed} ${gpu_id}
```

```bash
bash train.sh beat_block_hammer demo_clean 50 0 0
```

* `task_config` defaults to `demo_clean`, but in practice it usually carries a RUNID suffix; use the exact name of the `task_config` file you created (typically matching the config name).
* `expert_data_num` defaults to `50`, unless the user requests otherwise and you have already adjusted the relevant configs earlier.
* `seed` defaults to `0`.
* `gpu_id` defaults to `6`, but before each run it is recommended to check available GPUs with `nvidia-smi` to avoid CUDA out-of-memory errors.

Ref: [https://robotwin-platform.github.io/doc/usage/ACT.html](https://robotwin-platform.github.io/doc/usage/ACT.html)

---

### Stage 4: Evaluation / Inference

Goal: evaluate the model trained in the previous steps.

Example:

```bash
bash eval.sh ${task_name} ${task_config} ${ckpt_setting} ${expert_data_num} ${seed} ${gpu_id}
```

```bash
# bash eval.sh beat_block_hammer demo_clean demo_clean 50 0 0
# This command trains the policy using the `demo_clean` setting ($ckpt_setting)
# and evaluates it using the same `demo_clean` setting ($task_config).
```

Make sure that `task_config`, `ckpt_setting`, and other related settings stay consistent with the earlier stages of the pipeline.

* `task_config` defaults to `demo_clean`, but in practice it usually carries a RUNID suffix; use the exact name of the `task_config` file you created (typically matching the config name).

* `gpu_id` defaults to `6`, but before each run it is recommended to check available GPUs with `nvidia-smi` to avoid CUDA out-of-memory errors.

Ref: [https://robotwin-platform.github.io/doc/usage/ACT.html](https://robotwin-platform.github.io/doc/usage/ACT.html)


---

## 2) Task Config (Common Starting Point)

Before running the four stages above, you first need to modify some configuration files or code according to user requirements. The modifications are implemented by copying new files, as mentioned earlier.

Modifications usually start with the task_config file.

Example: you can read it yourself:

* `task_config/demo_clean.yml`

The task config controls basic task settings such as `domain_randomization`. You can open and inspect it.

In practice, you typically copy an existing task config (e.g., `task_config/demo_clean.yml`), then modify the copy according to the needs of the current run. The filename often includes an identifier; I recommend adding a RUNID suffix.

---

## 3) Modify Other Files as Needed

There may be other files that need to be adjusted based on user requirements.

As mentioned earlier, any modification must be done by **copying to a new file** and editing the copy.

For example:

- Training configuration: `policy/ACT/train.sh`
- Evaluation configuration: `policy/ACT/eval.sh`
- Evaluation script: `script/eval_policy.py`

These are possible candidates, but not necessarily limited to them.

You are encouraged to explore the project and the documentation, and decide what to change based on runtime feedback and errors.

---

## 4) Artifact “Pointers” (What you must record)
For each successful run, ensure the worklog includes:
- raw data directory
- processed dataset directory
- checkpoint directory
- evaluation output (metrics log, csv, videos)
