AML's agile implementation repository, with the task of rapid implementation


### (1) Env

RoboTwin 2.0 Env:
https://robotwin-platform.github.io/doc/usage/robotwin-install.html

Other：

```bash
pip install openai-agents
pip install "litellm>=1.76.0"
pip install arize-phoenix
pip install openai-agents openinference-instrumentation-openai-agents arize-phoenix-otel
pip install arize-phoenix arize-phoenix-otel \
  openinference-instrumentation-openai \
  openinference-instrumentation-openai-agents
```

### (2) Some debugging and running

Demo of Doubao + OpenAI Agent SDK: 

```bash
python agents/test_oasdk_doubao_vision.py
```

Demo of Siliconflow + OpenAI Agent SDK: 

```bash
python agents/test_oasdk_siliconflow_vision.py
```

Demo of Multi-Agent+ using tools to read file trees and perform file read/write:

```bash
python agents/test_oasdk_doubao_file_io.py
```

Output in: docs/agents_summary_20251211_194318.md

Demo of LiteLLM: 

```bash
agents/test_litellm_2_source.py
```

Demo of Tracking the agent's execution: 

```bash
python -m phoenix.server.main serve
python agents/test_oasdk_doubao_phoenix.py
```

### (3) Full ACT pipeline


task_config/smoke_seed.yml

task_config/smoke_act.yml

policy/ACT/train_smoke.sh

chmod +x policy/ACT/train_smoke.sh

script/eval_policy_smoke.py

chmod +x policy/ACT/eval_smoke.sh


run_robotwin_smoke.py


### (n) Ref

openai agent sdk:

https://github.com/openai/openai-agents-python
https://openai.github.io/openai-agents-python/quickstart/

RoboTwin 2.0:

https://robotwin-platform.github.io/doc/index.html

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

### (m) TODO

simple RAG: agents/chat12121946.txt

More APIs from other sources. Stronger VLM, GPT 5.2 Thinking?

trace: W&B Weave; other func of trace





