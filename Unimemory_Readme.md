环境要求
基础版 (轻量，就是没下载模型和没用API的版本，两种都用稀疏检索)
适用无 GPU、无外网环境，仅使用稀疏检索 (TF-IDF)。
- Python 3.10+
- scikit-learn
- loguru
- pydantic
- tree-sitter (CodeRAG 原来的依赖)
完整版 (API)
启用Dense和 LLM Rerank
- 上述所有依赖
- torch
- transformers
- openai (用于调用 LLM API)
*   模型文件:  Embedding 模型 (`Salesforce/codet5p-110m-embedding`) 。
快速开始
1. 离线 Demo 
使用 unified_memory.py，仅依赖 TF-IDF。

配置:
打开 unified_memory.py，修改底部的路径配置：
if __name__ == "__main__":
    ROBOTWIN_CODE_PATH = "/path/to/your/code_repo"      # 代码根目录
    ROBOTWIN_DOC_PATH = "/path/to/your/README.md"       # 文档文件路径，这里就是和repoagent接的地方
运行
python unified_memory.py

2. 完整版 (需配置)
使用 unified_memory_full.py，启用混合检索和 LLM rerank。

配置:
打开 unified_memory_full.py，填入 API Key 和模型路径：
config = {
    "repo_path": "/path/to/code",
    "doc_path": "/path/to/doc.md",
    "embedding_model": "Salesforce/codet5p-110m-embedding", # 或本地绝对路径
    "api_key": "sk",
    "api_url": "https://api.openai.com/v1",
    "rerank_model": "gpt-4"
}
运行:
python unified_memory_full.py

 技术原理 (详细的见Program Log中的Coderag魔改这个部分)

为了让 CodeRAG 框架（原设计仅支持代码 AST 节点）能够处理文档文本，我们在运行时对底层函数进行了动态替换：
1.  定义TextNode: 创建一个新的数据结构来支持doc。
2.  render_node: 修改 coderag.static_analysis.parse_repo_v2.render_node。
    当输入是 TextNode 时 -> 直接返回文本内容。
    当输入是 FunctionNode 等 -> 调用原框架逻辑生成代码字符串。

 目录
CodeRAG/
├── unified_memory.py       
├── unified_memory_full.py  
├── demo_data/              
│   └── metadata.jsonl      # 预处理后的robotwin的数据，这个地方要自己处理一下，目前我是用的robotwin的readme
├── coderag/                
└── README_MEMORY.md        
效果
[图片]
