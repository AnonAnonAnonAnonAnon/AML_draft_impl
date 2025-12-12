AML's agile implementation repository, with the task of rapid implementation


### (1) Env

RoboTwin 2.0 Env:
https://robotwin-platform.github.io/doc/usage/robotwin-install.html

Other：

```bash
pip install openai-agents
pip install "litellm>=1.76.0"
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

### (m) TODO

simple RAG, how
agents/chat12121946.txt

More APIs from other sources





