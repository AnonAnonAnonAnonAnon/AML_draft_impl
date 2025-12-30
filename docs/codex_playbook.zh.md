# docs/codex_playbook.zh.md

这是操作手册，用于在本仓库中运行并迭代 RoboTwin 2.0 流水线。

---

## A. 核心约束（摘要）
- 禁止 sudo。
- 禁止危险/破坏性命令。
- 不得修改旧文件；只能 **复制 → 改新文件 → 重定向调用**。
- 不得越界仓库根目录。
- 所有新文件带 RUNID；持续维护 `worklog_<RUNID>.md`。

如何在不改旧文件的前提下修改行为：
不要编辑任何已有文件。若需要修改某个被调用的脚本/配置，请先复制出一个带 RUNID 后缀的新文件并修改它；然后再复制上游的调用脚本/入口文件，改成引用这个新文件。
例如：原来 c.sh -> a.py，则创建 b.py（由 a.py 复制并修改），再创建 d.sh（由 c.sh 复制并改为调用 b.py）。这样满足“旧文件不变，只新增新文件”的要求。

---

## B. RUNID 与记录模板（推荐做法）

### B1) Worklog 模板（粘贴到 `worklog_<RUNID>.md`）
## Run <RUNID>
### 目标
- Task：
- 指标：
- 约束：
（If not, fill in null）

### 环境
- Host：
- GPU：
- Conda env：
- 关键路径：

### 本次新增文件/目录
- （path）— 用途

### 实际执行命令
- （command）
- （command）

### 日志与 PID
- （log path）—（pid）— 说明用途

### 产物定位 (Recommended Practice)
- Raw data：
- Processed data：
- Checkpoints：
- Eval outputs：

### 备注 / 问题记录 (Recommended Practice)
- Error：
- Fix：
- Reference（见 docs/cache/...）：

---

### B2) Web refs 模板（粘贴到 `docs/cache/web_refs_<RUNID>_NN.md`） (Recommended Practice, Brief description)
## Web refs <RUNID>_<NN>
### 主题 / 报错
- 我在解决什么问题：

### 链接
- （link）— 为什么相关
- （link）— 为什么相关

### 关键结论
- 要点列表

---

## C. 修改策略：“就地复制”
因为不允许编辑旧文件，请统一遵循：

1) 找到你想改的配置/脚本：
- 例如：`task_config/<base>.yml`、`train.sh`、`eval_policy.py`

2) 在同目录复制一份并加 RUNID 后缀：
- `cp task_config/<base>.yml task_config/<base>__r<RUNID>.yml`

3) 只修改新文件：
- 例如 episode_num / domain_randomization / seed / ckpt_dir 等

4) 对上级文件（调用本文件的文件）也同样的这样做；此时上级文件的调用指向新文件

如何在不改旧文件的前提下修改行为：
不要编辑任何已有文件。若需要修改某个被调用的脚本/配置，请先复制出一个带 RUNID 后缀的新文件并修改它；然后再复制上游的调用脚本/入口文件，改成引用这个新文件。
例如：原来 c.sh -> a.py，则创建 b.py（由 a.py 复制并修改），再创建 d.sh（由 c.sh 复制并改为调用 b.py）。这样满足“旧文件不变，只新增新文件”的要求。

---

## E. nohup 模式（示例）(Recommended Practice)
### E1) 训练 nohup
nohup bash train__r<RUNID>.sh > logs/train__r<RUNID>.log 2>&1 & echo $! > logs/train__r<RUNID>.pid

### E2) 监控
tail -f logs/train__r<RUNID>.log
cat logs/train__r<RUNID>.pid
ps -fp $(cat logs/train__r<RUNID>.pid)

把命令/日志/PID 记录到 `worklog_<RUNID>.md`。

---

## F. Git 自检（非强制但建议）(Recommended Practice)
- `git status --porcelain`
- `git diff --name-only`

如果不小心改了旧文件：
- 先撤销改动，再通过“Copy in-place”的方式重做。
