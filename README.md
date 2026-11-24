# MAID · 秘书处

**Multi-Agent Inter-harness Dispatch** · 你的多智能体项目秘书

你可以只和一名秘书对话，让它帮你整理需求、生成任务草稿并跟踪结果；也可以随时打开终端，直接和干活的 AI 交流。

- **秘书（MAID）**：默认使用 **agy**（也可换成 Claude 等本地工具），负责和你沟通、选项目、写草稿、查进度。
- **执行与验收（[AWO](https://github.com/cgy0071/agent-workflow-orchestrator)）**：负责派工、隔离运行、独立审查和保存验收证据。目前预览版的一次性任务由 **Codex** 执行和审查。

> 两个项目各自独立安装和更新：MAID 是你的“前台秘书”，AWO 是后台的“调度引擎”。

## 30 秒看懂完整流程

1. **选秘书**：决定用 `agy` 还是 Claude 和你对话。
2. **绑项目**：用 `configure.py` 指定要改哪个 Git 仓库、允许改哪些文件、用什么脚本验收。
3. **看草稿**：用 `request` 让秘书先写一份任务草稿（此时**不会**派工）。
4. **确认派工**：核对范围没问题后，运行 `start --confirm-execute` 真正交给 Codex 执行。
5. **查验收**：用 `status` 查看结果和证据编号；开新任务时换一个新目录，互不干扰。

---

## 安装与更新（Windows）

先确认本机已安装 **Git** 和 **Python 3.10+**；如果要实际派工执行代码任务，还需要已登录的 **Codex CLI**。

在同一个父目录下打开 PowerShell，分别克隆两个仓库并做一次自检：

~~~powershell
git clone https://github.com/cgy0071/MAID.git
git clone --branch maid-v0.1.0-preview.2 https://github.com/cgy0071/agent-workflow-orchestrator.git
cd MAID
python maid.py doctor
~~~

### 已经克隆过 AWO？
如果你电脑上已经有一份兼容版本的 AWO，不用重新克隆，在当前 PowerShell 告诉 MAID 它在哪里即可：

~~~powershell
$env:MAID_AWO_ROOT = 'D:\Tools\agent-workflow-orchestrator'
python maid.py doctor
~~~

**几个小提醒（最容易踩坑的地方）：**
- **默认查找位置**：`backend.py` 默认去 `MAID` 同级目录找 `agent-workflow-orchestrator`。一旦设置了 `$env:MAID_AWO_ROOT`，MAID 就只认你指定的路径，不会再自动回退到同级目录（新开 PowerShell 窗口需要重新设置）。
- **版本必须匹配**：`MAID` 需要 AWO 根目录里包含 `apps/maid/maid.py`、`scripts/secretary_adapter.py` 和 `scripts/project_entry.py`。目前验证过兼容的标签是 `maid-v0.1.0-preview.2`——**不要直接指向任意 `main` 或其他开发分支**，否则会报不兼容错误。
- **`doctor` 查什么**：它会打印实际找到的 AWO 路径并检查后端命令能否打开，但不会测试模型登录或真正跑任务。

**日常更新：**
- 只更新 MAID：在 `MAID` 目录运行 `git pull --ff-only`。
- 只更新 AWO：在 AWO 目录运行 `git fetch --tags`，用 `git switch --detach 标签名` 切到兼容版本，再回 MAID 运行 `python maid.py doctor` 确认入口正常。（仓库里的旧 ZIP 仅作历史存档，不用管。）

---

## 1. 选择你的秘书

先确保你想用的 CLI 工具已经安装并登录。在 PowerShell 里二选一：

~~~powershell
$Secretary = 'agy'                                    # 默认：Antigravity CLI
# $Secretary = '.\examples\secretary-claude.json'     # 想用 Claude 时取消这一行注释（无需 agy）
~~~

如果只想先随便聊聊、不涉及具体项目，可以直接开一个对话线程（输入 `exit` 退出）：

~~~powershell
python maid.py --thread "$env:LOCALAPPDATA\MAID\chat-01" chat --secretary $Secretary
~~~

> 提示：使用默认的 `agy` 时，可以用 `python maid.py direct --thread "$env:LOCALAPPDATA\MAID\chat-01" --secretary agy` 接着上次的对话继续聊；附带的 Claude 示例配置每次都是独立对话。如果你想接入自己的命令行工具，可以复制 `examples\secretary-claude.json`，把里面的 `turn` 改成你信任的命令（从标准输入读问题，往标准输出写答复即可）。

---

## 2. 绑定你的项目和允许修改的文件

把下面的 `$Project`（你的 Git 仓库路径）、允许修改的文件和验收脚本换成你自己的。示例假设仓库里已经有至少一次提交，并且包含 `app.py` 和一个验证脚本 `verify.py`（检查不通过时返回非零退出码）：

~~~powershell
$Project = 'D:\Projects\MyProject'          # 你的 Git 仓库根目录
$Thread  = "$env:LOCALAPPDATA\MAID\task-01" # 每次新任务用新路径，不要提前手动创建这个文件夹
$Profile = "$Thread.json"

New-Item -ItemType Directory -Force (Split-Path $Thread) | Out-Null
python configure.py --project $Project --thread $Thread --allow app.py --verify-script verify.py --profile $Profile
~~~

- `--project` 是你的代码仓库；`--thread` 用来存放本次任务的草稿与状态记录（注意两者不要互相包含）。
- 如果允许修改多个文件，可以重复传多个 `--allow`。
- `configure.py` 只生成本地配置文件，**不会**调用模型，也**不会**覆盖已经存在的配置文件。

---

## 3. 先看草稿，确认后再派工

先把需求发给秘书，让它生成一份任务草稿：

~~~powershell
python maid.py request --profile $Profile --thread $Thread --secretary $Secretary "修复 app.py 的求和函数，使 verify.py 通过"
~~~

生成后，仔细核对里面的目标和允许修改的文件。只要看到 `dispatched: false`，就说明**还没有真正派工**，可以放心检查或重来。

确认无误，并且同意使用本机登录的 Codex 执行、允许把通过验收的改动提交到本次任务分支后，再执行派工并查看进度：

~~~powershell
python maid.py --thread $Thread start --confirm-execute
python maid.py --thread $Thread status
~~~

以后重开终端想看结果时，回到 `MAID` 目录，把 `$Thread` 设回当时的路径，直接运行 `status` 就能看到验收结论和证据编号，**不会重复派工**。

---

## 4. 开启下一项任务与切换查询

同一个项目可以做很多次任务。准备下一项任务时，回到第 2 步，把 `task-01` 换成 `task-02`（生成新的 `$Profile`），再出草稿、确认派工即可。如果是另一个项目，记得一并换掉 `$Project`、允许修改的文件和验证脚本。

> `configure.py` 会用任务目录名拼出目标分支 `refs/heads/maid-<任务名>`，所以同一个仓库下请给不同任务起不同的名字。

想回头查看旧任务的状态？只要把 `--thread` 指回原来的目录就行：

~~~powershell
python maid.py --thread "$env:LOCALAPPDATA\MAID\task-01" status
python maid.py --thread "$env:LOCALAPPDATA\MAID\task-02" status
~~~

---

## 常见问题排查

| 遇到什么情况 | 怎么处理 |
| --- | --- |
| 报错 `Incompatible AWO: ... lacks ...` | 看清报错里打印的路径：如果是路径指错了，重新设置 `$env:MAID_AWO_ROOT`；如果该 AWO 分支确实缺少秘书接口，单独克隆 `maid-v0.1.0-preview.2` 标签即可，不用动你原来的 AWO 工作区。 |
| `doctor` 正常，但 `request` 找不到 `agy` | 确认当前终端里能直接运行 `agy`；如果改用 Claude，请取消 `$Secretary = '.\examples\secretary-claude.json'` 的注释，并确保 Claude CLI 已安装且登录。 |
| `configure.py` 提示验证脚本不存在或 profile 已存在 | 检查 `--verify-script` 写的是不是项目里真实存在的脚本；已有配置不会被覆盖，开新任务请换一个任务名。 |
| 草稿里显示 `dispatched: false` | 这是正常现象，说明还在审阅草稿阶段。确认范围无误后再执行 `start --confirm-execute`；不确定以前有没有派过工，先运行 `status` 查一下。 |
| 切到别的项目后，查不到刚才的结果 | 回到 `MAID` 目录，用原任务对应的 `--thread` 路径查 `status`；千万不要为了查结果重新运行 `start`。 |
