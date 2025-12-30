# docs/robowin_pipeline_map.zh.md

这是 RoboTwin 2.0 流水线在本仓库里的导航图

简要的描述了RoboTwin 2.0 的各个阶段、调用结构等基本信息

推荐你自行的探索仓库，或者自行的上网搜索RoboTwin 2.0的文档以进一步的学习

例如：

https://robotwin-platform.github.io/doc/index.html

https://robotwin-platform.github.io/doc/usage/collect-data.html

https://robotwin-platform.github.io/doc/usage/ACT.html

https://robotwin-platform.github.io/doc/usage/configurations.html#24-data-collection-settings

---

## 1) 流水线阶段概览

### 阶段 1：数据采集
目标：采集指定数量的专家数据

例子：

bash collect_data.sh ${task_name} ${task_config} ${gpu_id}
Clean Data Example: bash collect_data.sh beat_block_hammer demo_clean 0

如果你调整了该脚本并复制，则改为运行你自己新建的脚本

task_name 默认为 beat_block_hammer，但一般会有用户需求，根据用户需求选择

task_config 默认为 demo_clean，但一般会有runid后缀，具体根据你创建的task_config决定，是同名的

gpu_id默认为6，但在每次运行前，推荐运行nvidia-smi以查看服务器当前空闲的gpu，避免cuda out of memory错误

ref: https://robotwin-platform.github.io/doc/usage/collect-data.html

---

### 阶段 2：数据处理

目标：把收集的数据转成具体模型训练可用的格式

根据具体要使用的 policy 决定，例如 ACT

默认使用的 policy 为 ACT，除非用户提出其他要求

如果决定使用该 policy ，首先要进入该 policy 的目录，例如：

cd policy/ACT

然后收集数据

例子：

bash process_data.sh ${task_name} ${task_config} ${expert_data_num}

bash process_data.sh beat_block_hammer demo_clean 50

如果你调整了该脚本并复制，则改为运行你自己新建的脚本，但一般很少这样

task_name 默认为 beat_block_hammer，但一般会有用户需求，根据用户需求选择

task_config 默认为 demo_clean，但一般会有runid后缀，具体根据你创建的task_config决定，是同名的

ref：https://robotwin-platform.github.io/doc/usage/ACT.html

---

### 阶段 3：训练
目标：启动训练过程

是数据处理的后续步骤，延续各种决定

例子：

bash train.sh ${task_name} ${task_config} ${expert_data_num} ${seed} ${gpu_id}

# bash train.sh beat_block_hammer demo_clean 50 0 0

task_config 默认为 demo_clean，但一般会有runid后缀，具体根据你创建的task_config决定，是同名的

expert_data_num默认为50，除非有用户要求，你在前面的各种配置文件已经做了调整

seed默认为0

gpu_id默认为6，但在每次运行前，推荐运行nvidia-smi以查看服务器当前空闲的gpu，避免cuda out of memory错误

ref：https://robotwin-platform.github.io/doc/usage/ACT.html 

---

### 阶段 4：评估 / 推理
目标：评估前面所训练的模型

例子：

bash eval.sh ${task_name} ${task_config} ${ckpt_setting} ${expert_data_num} ${seed} ${gpu_id}
# bash eval.sh beat_block_hammer demo_clean demo_clean 50 0 0
# This command trains the policy using the `demo_clean` setting ($ckpt_setting)
# and evaluates it using the same `demo_clean` setting ($task_config).

task_config和ckpt_setting等等配置注意都和前面的过程保持一致

gpu_id默认为6，但在每次运行前，推荐运行nvidia-smi以查看服务器当前空闲的gpu，避免cuda out of memory错误

ref：https://robotwin-platform.github.io/doc/usage/ACT.html 

---

## 2) Task Config（常见起点）

在运行上面的4个阶段之前，你首先要根据用户需求修改一些配置文件或代码，修改通过复制新文件实现，前面已经提及

修改通常从task_config文件开始

例子：你可以自行阅读

task_config/demo_clean.yml

Task config 控制 domain_randomization 等 基本任务设置，你可以阅读看看

通常，会从现有的Task Config，例如task_config/demo_clean.yml，复制出一份，再根据本次运行的需求改动，命名可能会有标识，例如我推荐你的runid后缀

---

## 3) 根据要求修改其他文件

也许有其他文件要根据用户需求修改

同样的，修改通过复制新文件实现，前面已经提及

例如：

训练配置：policy/ACT/train.sh

评估配置：policy/ACT/eval.sh 

评估脚本：script/eval_policy.py

可能包括，但也许不止这些

鼓励你探索项目和文档，根据运行反馈来决定

---

## 4) 产物指针（必须记录在 worklog）
每次成功 run，worklog 必须写清：
- raw data 目录
- processed dataset 目录
- checkpoint 目录
- eval 输出（指标日志、csv、视频等）
