AML's agile implementation repository, with the task of rapid implementation


### (1) Env

RoboTwin 2.0 Env:
https://robotwin-platform.github.io/doc/usage/robotwin-install.html

Agents framework：

```bash
pip install openai-agents
pip install "litellm>=1.76.0"
pip install arize-phoenix
pip install openai-agents openinference-instrumentation-openai-agents arize-phoenix-otel
pip install arize-phoenix arize-phoenix-otel \
  openinference-instrumentation-openai \
  openinference-instrumentation-openai-agents
```

codex (global) (optional):

```bash
mkdir -p ~/.npm-global
npm config set prefix "$HOME/.npm-global"
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
conda activate aml
npm i -g @openai/codex
```

codex (Under the project directory):
```bash
npm init -y
npm i -D @openai/codex
npx codex --version
```

### (2) Some Running of Wheels

Demo of Doubao/Siliconflow/uiui + OpenAI Agent SDK, with visual input：

```bash
python agents/test_oasdk_uiui_vision.py
python agents/test_oasdk_doubao_vision.py
python agents/test_oasdk_siliconflow_vision.py
```

Demo of Doubao/Siliconflow/uiui + LiteLLM + OpenAI Agent SDK. However, when there is image input, a large number of data URLs are printed in the terminal, which is difficult to block.: 

```bash
python agents/test_oasdk_litellm_vision.py
```

Demo of Multi-Agent + using tools to read file trees and perform file read/write:

```bash
python agents/test_oasdk_doubao_file_io.py
```

Output in: docs/agents_summary_20251211_194318.md

Demo of Tracking the agent's execution: 

```bash
python -m phoenix.server.main serve
python agents/test_oasdk_doubao_phoenix.py
```

Demo of uiui + Codex. Create File:

.codex_uiui/config.toml

```bash
python agents/run_codex_uiui_demo.py
```

### (3) Full pipeline: Primitive

#### (3.1) ACT 

Collect Data, Install ACT environment, Data Conversion, Train, Eval: 

```bash
bash collect_data.sh beat_block_hammer demo_clean 7

cd policy/ACT
pip install pyquaternion pyyaml rospkg pexpect mujoco==2.3.7 dm_control==1.0.14 opencv-python matplotlib einops packaging h5py ipython
cd detr && pip install -e . && cd ..

bash process_data.sh beat_block_hammer demo_clean 50

nohup bash train.sh beat_block_hammer demo_clean 50 0 7 > logs/act_train_bbh_demo_clean_50_s0_g7.log 2>&1 &

nohup bash eval.sh beat_block_hammer demo_clean demo_clean 50 0 7 > logs/act_EVAL_bbh_demo_clean_50_s0_g7_12202207.log 2>&1 &
```

Ref：

https://robotwin-platform.github.io/doc/usage/collect-data.html

https://robotwin-platform.github.io/doc/usage/ACT.html

#### (3.2) DP 

Collect Data, Install DP environment, Data Conversion, Train, Eval: 

```bash
bash collect_data.sh beat_block_hammer demo_clean 7

cd policy/DP
pip install zarr==2.12.0 wandb ipdb gpustat dm_control omegaconf hydra-core==1.2.0 dill==0.3.5.1 einops==0.4.1 diffusers==0.11.1 numba==0.56.4 moviepy imageio av matplotlib termcolor sympy
pip install -e .

bash process_data.sh beat_block_hammer demo_clean 50

nohup bash train.sh beat_block_hammer demo_clean 50 0 14 7 > logs/dp_train_bbh_demo_clean_50_s0_g7_12211613.log 2>&1 &

nohup bash eval.sh beat_block_hammer demo_clean demo_clean 50 0 7 > logs/dp_eval_bbh_demo_clean_50_s0_g7_12212112.log 2>&1 &

```

Ref：

https://robotwin-platform.github.io/doc/usage/collect-data.html

https://robotwin-platform.github.io/doc/usage/DP.html

### (4) Full ACT pipeline: Edit

#### (4.1) Smoke

Link together ACT's data collection, processing, training, and inference.

Smoke test, now reduce all quantities, for example, there is only one piece of data.

Create these files: 

```bash
task_config/smoke_seed.yml
task_config/smoke_act.yml
policy/ACT/train_smoke.sh
script/eval_policy_smoke.py
```

Authorization:

```bash
chmod +x policy/ACT/train_smoke.sh
chmod +x policy/ACT/eval_smoke.sh
```

Smoke test:

```bash
python run_robotwin_smoke.py
```

#### (4.2) ACT

New 6 files:

full_pipeline/run_robotwin_act_full.py

task_config/act_full_12211636.yml (copy demo_clean.yml)

policy/ACT/process_full.sh (copy process_data.sh)

policy/ACT/train_full.sh (copy train.sh)

policy/ACT/eval_full.sh 

script/eval_policy_full.py (copy eval_policy_smoke.py)

```bash
chmod +x policy/ACT/process_full.sh policy/ACT/train_full.sh policy/ACT/eval_full.sh

cd full_pipeline

nohup python run_robotwin_act_full.py > logs/act_full_run_11211636.log 2>&1 &
```

#### (4.3) DP

New 6 files:

full_pipeline/run_robotwin_dp_full.py

task_config/dp_full_12212127.yml (copy demo_clean.yml)

policy/DP/process_full.sh (copy policy/DP/process_data.sh)

policy/DP/train_full.sh (copy policy/DP/train.sh)

policy/DP/eval_full.sh

script/eval_policy_full.py (exists)

```bash
chmod +x policy/DP/process_full.sh policy/DP/train_full.sh policy/DP/eval_full.sh

cd full_pipeline

nohup python -u run_robotwin_dp_full.py > logs/dp_full_run_11212127.log 2>&1 &
```

#### (4.3) ACT (Codex Skill Ver)

```bash
python agents/run_codex_uiui_act_skill.py
```

Do not use sandbox, otherwise rendering will not work.

Users can specify some modifications: 

```bash
python agents/run_codex_uiui_act_skill_edit.py
```

### (n) Ref

openai agent sdk:

https://github.com/openai/openai-agents-python
https://openai.github.io/openai-agents-python/quickstart/

RoboTwin 2.0:

https://robotwin-platform.github.io/doc/index.html

Codex:

https://developers.openai.com/codex

doubao:

https://console.volcengine.com/ark/region:ark+cn-beijing/model/detail?Id=doubao-seed-1-6
https://www.volcengine.com/docs/82379/1399008?lang=zh

Siliconflow:

https://cloud.siliconflow.cn/me/models
https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions

Phoenix:

https://google.github.io/adk-docs/observability/phoenix/

W&B Weave:

https://github.com/wandb/weave

uiui:

https://sg.uiuiapi.com/console
https://sg.uiuiapi.com/pricing
https://7sqmooerpq.apifox.cn/

### (m) TODO

Manually encapsulate API calls from different sources

simple RAG

trace: W&B Weave; other func of trace





