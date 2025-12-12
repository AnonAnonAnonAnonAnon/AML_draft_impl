#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
豆包 + OpenAI Agents SDK
多 Agent 协作：
- 浏览 Python 文件树
- 读取文件
- 生成总结并写入本地文件
"""

# ===== 配置区（按需修改） =====
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_ID     = "doubao-seed-1-6-251015"      # 豆包推理接入点 ID / 模型 ID
API_KEY      = "70f0d563-91a5-4704-a00e-f00cf3a9c864"       # 直接写 Ark API Key

# 项目根目录（文件操作都相对这里）
PROJECT_ROOT = "/home/zhangw/AML/AML_draft_impl"

# 一个默认任务（用于 __main__ 演示）
DEFAULT_ROOT_REL_DIR   = "agents"            # 要分析的相对目录
DEFAULT_OUTPUT_REL_PATH = "docs/agents_summary.md"
DEFAULT_TASK_DESC      = "为新加入的开发者生成该目录下 Python 文件的中文功能说明。"


# ===== 代码区（一般不用改） =====
import os
import base64
import mimetypes
from typing import List

from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
    function_tool,
)


# ========== 工具定义 ==========

@function_tool
def list_python_files(
    root_dir: str,
    max_depth: int = 4,
    max_files: int = 200,
) -> List[str]:
    """
    列出指定目录下的 Python 文件（相对 PROJECT_ROOT 的路径）。
    """
    if os.path.isabs(root_dir):
        start_dir = root_dir
    else:
        start_dir = os.path.join(PROJECT_ROOT, root_dir)

    print(f"[tool:list_python_files] 扫描目录: {start_dir}, max_depth={max_depth}, max_files={max_files}")

    ignore_dirs = {"venv", ".git", "__pycache__", ".mypy_cache", ".pytest_cache", ".idea", ".vscode"}
    results: List[str] = []

    for current_root, dirs, files in os.walk(start_dir):
        rel_from_root = os.path.relpath(current_root, start_dir)
        depth = 0 if rel_from_root == "." else rel_from_root.count(os.sep)
        if depth >= max_depth:
            dirs[:] = []  # 不再深入
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for fname in files:
            if not fname.endswith(".py"):
                continue
            abs_path = os.path.join(current_root, fname)
            rel_to_project = os.path.relpath(abs_path, PROJECT_ROOT)
            results.append(rel_to_project)
            if len(results) >= max_files:
                print(f"[tool:list_python_files] 已找到 {len(results)} 个文件（达到上限）")
                return results

    print(f"[tool:list_python_files] 扫描结束，共找到 {len(results)} 个 Python 文件")
    return results


@function_tool
def read_file(path: str, max_bytes: int = 20000) -> str:
    """
    读取文本文件的一部分内容。
    """
    if os.path.isabs(path):
        abs_path = path
    else:
        abs_path = os.path.join(PROJECT_ROOT, path)

    print(f"[tool:read_file] 读取文件: {abs_path} (最多 {max_bytes} 字节)")

    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read(max_bytes)
    return data


from datetime import datetime

@function_tool
def write_text_file(output_path: str, content: str) -> str:
    """
    将文本写入指定文件，每次调用都会生成一个带时间戳的新 .md 文件，不覆盖已有文件。

    基准路径: docs/agents_summary.md
    实际写入: docs/agents_summary_YYYYmmdd_HHMMSS.md
    """
    if os.path.isabs(output_path):
        abs_path = output_path
    else:
        abs_path = os.path.join(PROJECT_ROOT, output_path)

    base, ext = os.path.splitext(abs_path)
    if ext == "":
        ext = ".md"

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = f"{base}_{ts}{ext}"

    os.makedirs(os.path.dirname(candidate), exist_ok=True)
    with open(candidate, "w", encoding="utf-8") as f:
        f.write(content)

    rel_path = os.path.relpath(candidate, PROJECT_ROOT)
    print(f"[tool:write_text_file] 已写入 {len(content)} 个字符到 {candidate}")
    return f"已写入 {len(content)} 个字符到 {rel_path}"



# （可选）如果后面你想在多模态总结里用到图片，这个工具可以复用
@function_tool
def image_to_data_url(path: str) -> str:
    """
    将本地图片转为 data URL（data:<mime>;base64,...），方便作为 input_image 使用。
    """
    path = os.path.expanduser(path)
    mime, _ = mimetypes.guess_type(path)
    if mime is None:
        mime = "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


# ========== Client 与全局设置 ==========

_client = AsyncOpenAI(
    base_url=ARK_BASE_URL,
    api_key=API_KEY,
)

set_default_openai_api("chat_completions")
set_default_openai_client(_client)
set_tracing_disabled(True)


# ========== Agent 定义 ==========

# 写入 Agent：整理总结并写入文件
writer_agent = Agent(
    name="WriterAgent",
    instructions=(
        "你负责整理多个文件的说明，生成整体总结，并写入到指定路径。"
        " 最终总结应使用清晰的中文结构，按目录和文件组织内容。"
        " 生成总结后，使用 write_text_file 工具，将完整总结作为 content 写入用户指定的路径。"
    ),
    tools=[write_text_file],
    model=MODEL_ID,
)

# 文件阅读 Agent：读取指定文件并做简要说明（必要时可以把结果交给 WriterAgent）
file_reader_agent = Agent(
    name="FileReaderAgent",
    instructions=(
        "你负责读取指定的 Python 文件，并总结它们的作用。"
        " 使用 read_file 工具获取文件内容，然后用简洁中文说明该文件负责的功能、关键类和函数。"
        " 避免逐行翻译代码，重点说明整体结构和用途。"
        " 如有需要，可以将已经整理好的说明交给 WriterAgent 继续写入文件。"
    ),
    tools=[read_file],
    handoffs=[writer_agent],   # 关键：允许从 FileReaderAgent handoff 到 WriterAgent
    model=MODEL_ID,
)

# 文件树 Agent：专门负责列出 Python 文件（必要时可以把任务交给 FileReaderAgent）
file_tree_agent = Agent(
    name="FileTreeAgent",
    instructions=(
        "你负责浏览项目的文件树，只关注 Python 文件（.py）。"
        " 当需要列出文件时，调用 list_python_files 工具，并把结果以简洁列表形式说明。"
        " 如有需要，可以将文件列表交给 FileReaderAgent 继续分析。"
        " 不要凭空编造不存在的文件路径。"
    ),
    tools=[list_python_files],
    handoffs=[file_reader_agent],   # 关键：允许从 FileTreeAgent handoff 到 FileReaderAgent
    model=MODEL_ID,
)

# 协调者 Agent：理解用户需求，调度其他 Agent 完成任务
coordinator_agent = Agent(
    name="CoordinatorAgent",
    instructions=(
        "你是项目文档的协调者。"
        " 用户会告诉你要分析的目录（相对于项目根目录）和输出文件路径。"
        " 你的任务是："
        " 1）使用 FileTreeAgent 列出需要分析目录下的 Python 文件；"
        " 2）使用 FileReaderAgent 读取并总结这些文件的功能；"
        " 3）使用 WriterAgent 将汇总后的结果写入指定输出文件。"
        " 你可以多轮与这些代理协作，最终向用户汇报总结已生成，并简要概括总结内容。"
        f" 项目根目录是：{PROJECT_ROOT}。"
        " 请严格使用用户给定的相对目录和输出路径，不要任意更改。"
    ),
    handoffs=[file_tree_agent, file_reader_agent, writer_agent],
    model=MODEL_ID,
)


# ========== 对外封装函数 ==========

def run_repo_summary(root_rel_dir: str, output_rel_path: str, task_desc: str) -> str:
    """
    让多 Agent 系统对指定目录的 Python 文件做总结，并写入指定输出路径。
    """
    print("========== [run_repo_summary] 开始项目总结任务 ==========")
    print(f"[run_repo_summary] 分析目录: {root_rel_dir} (相对于 {PROJECT_ROOT})")
    print(f"[run_repo_summary] 输出基准文件: {output_rel_path}")
    print(f"[run_repo_summary] 任务描述: {task_desc}")

    prompt = (
        "请根据下面的要求，对项目中的 Python 文件进行分析和总结：\n"
        f"- 项目根目录：{PROJECT_ROOT}\n"
        f"- 需要分析的相对目录：{root_rel_dir}\n"
        f"- 只分析该目录及其子目录中的 .py 文件\n"
        f"- 最终总结文件的相对路径：{output_rel_path}\n"
        f"- 任务描述：{task_desc}\n\n"
        "请合理调用 FileTreeAgent、FileReaderAgent 和 WriterAgent 来完成任务。"
        " 最终向我报告：总结已写入的文件路径，以及一段简短的整体概览。"
    )

    result = Runner.run_sync(coordinator_agent, prompt)

    print("========== [run_repo_summary] Agents 运行结束 ==========")
    return result.final_output



# ========== 演示入口 ==========

if __name__ == "__main__":
    summary_msg = run_repo_summary(
        root_rel_dir=DEFAULT_ROOT_REL_DIR,
        output_rel_path=DEFAULT_OUTPUT_REL_PATH,
        task_desc=DEFAULT_TASK_DESC,
    )
    print(summary_msg)
