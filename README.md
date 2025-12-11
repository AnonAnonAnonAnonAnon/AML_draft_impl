AML's agile implementation repository, with the task of rapid implementation


### (1) Env

RoboTwin 2.0 Env:
https://robotwin-platform.github.io/doc/usage/robotwin-install.html

Other：

```bash
pip install openai-agents
```

### (2) Some debugging and running

Some minimal demo of Doubao + OpenAI Agent SDK: 

```bash
python agents/test_openaiagentsdk_doubao.py
python agents/test_openaiagentsdk_doubao_vision.py
```

A demo of Multi-Agent+ using tools to read file trees and perform file read/write:

```bash
python agents/test_oasdk_db_file_io.py
```

Output in: docs/agents_summary_20251211_194318.md

### (n) Ref

openai agent sdk:

https://github.com/openai/openai-agents-python
https://openai.github.io/openai-agents-python/quickstart/

doubao:

https://console.volcengine.com/ark/region:ark+cn-beijing/model/detail?Id=doubao-seed-1-6
https://www.volcengine.com/docs/82379/1399008?lang=zh

RoboTwin 2.0:

https://robotwin-platform.github.io/doc/index.html

### (m) TODO

工具调用，文件修改；封装

LiteLLM





