USER_TASK = r"""
请运行 RoboTwin 2.0 全流程：采集 -> 处理 -> 训练 -> 评估。
严格遵守 AGENTS.md：
- 禁止 sudo
- 禁止危险/破坏性命令
- 不允许修改任何本次开始前就存在的文件（只能复制/新建带 RUNID 后缀的文件，并通过新 wrapper/新配置重定向调用）
- 不得越界仓库根目录

请使用我提供的 RUNID 来命名你创建的所有新文件，并且必须创建：
- worklog_<RUNID>.md
- docs/cache/web_refs_<RUNID>.md（如内容较多允许拆分成多个文件，例如 web_refs_<RUNID>_01.md, _02.md）

推荐自底向上调试：先做最小化 smoke test，再逐步扩大规模。
"""




def build_codex_prompt(runid: str) -> str:
    return f"""RUNID={runid}

{USER_TASK}

请先阅读 AGENTS.md，然后在执行过程中持续创建/更新：worklog_{runid}.md。
"""




def write_initial_worklog(runid: str) -> Path:
    path = REPO_ROOT / f"worklog_{runid}.md"
    if path.exists():
        return path
    path.write_text(
        f"""## Run {runid}
### 目标
- Task：RoboTwin 2.0 全流程（采集->处理->训练->评估）
- 指标：success rate、OOD success rate（如适用）
- 约束：禁 sudo；禁危险命令；不得修改旧文件；不得越界仓库根目录

### 已执行命令
-（由 agent 填写）

### 本次新增文件/目录
-（由 agent 填写）

### 日志与 PID
- 外层 driver 日志：logs/{OUTER_LOG_PREFIX}_{runid}.log

### 产物定位（必须写清）
- Raw data：
- Processed data：
- Checkpoints：
- Eval outputs：

""",
        encoding="utf-8",
    )
    return path

