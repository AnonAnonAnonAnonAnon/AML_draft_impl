import os
import subprocess
from pathlib import Path

# 脚本在 .../AML_draft_impl/agents/ 下
# 仓库根是上一层：.../AML_draft_impl
REPO_ROOT = Path(__file__).resolve().parents[1]
CODEX_HOME = REPO_ROOT / ".codex_uiui"

UIUI_KEY = "sk-c0sBK7t2p6LV84r5s7KUknm4BvzcEdiwjd3jRNE1IdV0Ero5"  # 你已有

def main():
    env = os.environ.copy()
    env["CODEX_HOME"] = str(CODEX_HOME)
    env["UIUI_API_KEY"] = UIUI_KEY

    cmd = [
        "codex", "exec",
        "--cd", str(REPO_ROOT),          # 关键：让 Codex 以仓库根为工作目录
        "--sandbox", "read-only",
        '如果我让你在进行项目开发时，只能新增文件，不能修改或删除已有文件，你能不能做到？你如何做到？'
    ]
    subprocess.run(cmd, env=env, check=True)

if __name__ == "__main__":
    main()
