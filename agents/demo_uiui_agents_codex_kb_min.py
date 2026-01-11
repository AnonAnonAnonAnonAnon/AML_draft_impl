#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最小层级跑通（分离后端配置）：
- 外层：UIUI(OpenAI兼容) + OpenAI Agents SDK（chat.completions）
- 工具：kb_search（占位检索）
- 工具：codex_exec（subprocess 调 codex exec；使用 CODEX_HOME + UIUI_API_KEY）
- Agent：每次回答前强制调用 kb_search -> codex_exec，然后汇总输出
"""

# =========================
# CONFIG（只改这里）
# =========================
from pathlib import Path

# ---------- 外层 Agent（OpenAI SDK / Agents SDK） ----------
AGENT_UIUI_BASE_URL = "https://sg.uiuiapi.com/v1"   # 或 https://api1.uiuiapi.com/v1
AGENT_MODEL_ID = "gpt-5.2"
AGENT_API_KEY = "sk-c0sBK7t2p6LV84r5s7KUknm4BvzcEdiwjd3jRNE1IdV0Ero5"   # 外层 Agent 用的 UIUI Key（不要提交 Git）

# （可选）大陆环境可能受代理变量影响；如不需要可保持 True
AGENT_TRUST_ENV = True  # True=继承 ALL_PROXY/HTTP_PROXY 等；False=忽略这些环境变量


# ---------- Codex（CLI） ----------
# 脚本在 .../AML_draft_impl/agents/ 下时：parents[1] 就是 repo root
REPO_ROOT = Path(__file__).resolve().parents[1]

CODEX_BIN = "codex"
CODEX_HOME = REPO_ROOT / ".codex_uiui"  # 你已跑通的 codex provider 配置目录
CODEX_UIUI_KEY = "sk-c0sBK7t2p6LV84r5s7KUknm4BvzcEdiwjd3jRNE1IdV0Ero5"   # Codex 用的 UIUI Key（不要提交 Git）
CODEX_SANDBOX = "read-only"

# 为了避免输出过长，可以截断 codex stdout/stderr
CODEX_STDOUT_MAX_CHARS = 6000


# =========================
# CODE（一般不用改）
# =========================
import os
import subprocess
from typing import Dict

import httpx
from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    function_tool,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
)


def _base_env_for_codex() -> Dict[str, str]:
    """
    按你已跑通的方式：
    - 只给 codex 子进程设置 CODEX_HOME + UIUI_API_KEY
    - 不干预 codex 的 base_url（由 .codex_uiui 内部 provider 配置决定）
    """
    env = os.environ.copy()
    env["CODEX_HOME"] = str(CODEX_HOME)
    env["UIUI_API_KEY"] = CODEX_UIUI_KEY
    return env


@function_tool
def kb_search(query: str) -> str:
    """（占位）检索知识库：当前不接真实 KB，只返回固定文本，用于验证工具链路。"""
    print(f"[tool:kb_search] query={query!r}")
    return "你成功检索了知识库。"


@function_tool
def codex_exec(prompt: str) -> str:
    """调用 codex CLI 执行一次命令（使用单独的 Codex 后端配置）。"""
    print("[tool:codex_exec] running codex exec ...")

    cmd = [
        CODEX_BIN,
        "exec",
        "--cd",
        str(REPO_ROOT),
        "--sandbox",
        CODEX_SANDBOX,
        prompt,
    ]

    proc = subprocess.run(
        cmd,
        env=_base_env_for_codex(),
        capture_output=True,
        text=True,
        check=False,
    )

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    if len(stdout) > CODEX_STDOUT_MAX_CHARS:
        stdout = stdout[:CODEX_STDOUT_MAX_CHARS] + "\n...[stdout truncated]..."
    if len(stderr) > CODEX_STDOUT_MAX_CHARS:
        stderr = stderr[:CODEX_STDOUT_MAX_CHARS] + "\n...[stderr truncated]..."

    if proc.returncode == 0:
        return f"[codex ok]\n{stdout}"
    return f"[codex failed] returncode={proc.returncode}\n[stdout]\n{stdout}\n\n[stderr]\n{stderr}"


def _build_agent() -> Agent:
    # 外层 Agent：走 OpenAI 兼容 chat.completions；这里用你“直接参数区配置”的方式
    http_client = httpx.AsyncClient(trust_env=AGENT_TRUST_ENV)

    client = AsyncOpenAI(
        base_url=AGENT_UIUI_BASE_URL,
        api_key=AGENT_API_KEY,
        http_client=http_client,
    )

    set_default_openai_api("chat_completions")
    set_default_openai_client(client)
    set_tracing_disabled(True)

    return Agent(
        name="MiniCoordinator",
        model=AGENT_MODEL_ID,
        tools=[kb_search, codex_exec],
        instructions=(
            "你是一个简洁的中文助手。\n"
            "重要：每次用户提问，你必须按顺序做两步：\n"
            "1) 调用 kb_search(query=用户问题)；\n"
            "2) 调用 codex_exec(prompt=一个对 codex 的指令，要求它回答用户问题；必要时让它说明是否能读取文件、在 read-only 下能做什么)。\n"
            "然后把 kb_search 结果 + codex_exec 结果整合成最终答复。\n"
            "输出结构：\n"
            "- KB: ...\n"
            "- Codex: ...\n"
            "- Final: ...\n"
        ),
    )


def run_once(user_text: str) -> str:
    agent = _build_agent()
    result = Runner.run_sync(agent, user_text)
    return result.final_output


if __name__ == "__main__":
    import sys

    user_query = "你好，能看文件吗？如果只能 read-only，你能做什么、不能做什么？"
    if len(sys.argv) >= 2:
        user_query = sys.argv[1]

    print(f"[main] REPO_ROOT={REPO_ROOT}")
    print(f"[main] CODEX_HOME={CODEX_HOME}")
    print(f"[main] AGENT_UIUI_BASE_URL={AGENT_UIUI_BASE_URL}, AGENT_MODEL_ID={AGENT_MODEL_ID}")
    print(f"[main] user_query={user_query!r}\n")

    out = run_once(user_query)
    print("\n========== FINAL OUTPUT ==========")
    print(out)
