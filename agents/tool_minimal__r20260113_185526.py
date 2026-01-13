#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Minimal tool module for Agents SDK tool-calling smoke test.
"""

import json
import time

try:
    from agents import function_tool
except Exception as exc:
    raise ImportError(
        "Failed to import agents.function_tool. "
        "If you have a local 'agents/' folder, it may be shadowing the "
        "OpenAI Agents SDK package. Ensure the SDK is installed and "
        "imported before loading this module."
    ) from exc


@function_tool
def ping(message: str) -> str:
    """
    Echo a message with a timestamp so we can verify tool execution.
    """
    payload = {
        "message": message,
        "ts": time.time(),
    }
    print(f"[tool:ping] {payload}")
    return json.dumps(payload, ensure_ascii=True)
