# MAID · 秘书处

**Multi-Agent Inter-harness Dispatch** · 面向异构 Harness 的多智能体秘书协同调度框架

你可以只和一名秘书对话，也可以在 Herdr 或习惯的终端直接与执行者交流。秘书默认用 **agy**，可以换成 Claude 等本地命令；本预览版的一次性任务由 **Codex 执行和审查**。

**MAID 是秘书入口，[AWO](https://github.com/cgy0071/agent-workflow-orchestrator) 是工作流引擎。** 在 MAID 选秘书、选项目、确认草稿；由 AWO 派工、保存任务状态和独立验收证据。两个项目分别安装和更新。

## Windows 安装与更新

在同一个父目录打开 PowerShell。需要 Git 和 Python 3.10+；执行项目任务还需要已登录的 Codex CLI。

~~~powershell
git clone https://github.com/cgy0071/MAID.git
git clone --branch maid-v0.1.0-preview.2 https://github.com/cgy0071/agent-workflow-orchestrator.git
cd MAID
python maid.py doctor
~~~

已有兼容的 AWO？跳过第二次克隆，在当前 PowerShell 指定其位置：

~~~powershell
$env:MAID_AWO_ROOT = 'D:\Tools\agent-workflow-orchestrator'
python maid.py doctor
~~~

**只更新 MAID**：在 MAID 目录运行 `git pull --ff-only`。**只更新 AWO**：在 AWO 目录运行 `git fetch --tags`，用 `git switch --detach 标签名` 切到兼容版本，再回 MAID 运行 `python maid.py doctor` 检查入口。当前验证过的 AWO 标签是 `maid-v0.1.0-preview.2`；不保证任意 main 都含秘书接口。旧 ZIP 仅作历史预览保留。

## 1. 选择秘书

先安装并登录想用的 CLI。在 PowerShell 中从下列两行**任选一行**，之后的命令都会使用这个秘书：

~~~powershell
$Secretary = 'agy'                                    # 默认：Antigravity CLI
$Secretary = '.\examples\secretary-claude.json' # Claude CLI，无需 agy
~~~

只想交谈？不需要项目配置：

~~~powershell
python maid.py --thread "$env:LOCALAPPDATA\MAID\chat-01" chat --secretary $Secretary
~~~

输入 `exit` 离开。默认 agy 支持在终端用 `python maid.py direct --thread "$env:LOCALAPPDATA\MAID\chat-01" --secretary agy` 续聊。附带的 Claude 配置每轮独立，不恢复旧对话。自定义秘书可复制该 JSON，将 `turn` 改为自己信任的命令参数数组：命令从标准输入读问题，向标准输出写答复。

## 2. 指定项目路径和允许修改的文件

把下面的项目路径、允许修改的文件和验证脚本换成你自己的。示例假定 Git 仓库已有提交，包含 `app.py` 和 `verify.py`；验证脚本应在检查失败时返回非零退出码。

~~~powershell
$Project = 'D:\Projects\MyProject'       # 已有 Git 仓库的根目录
$Thread = "$env:LOCALAPPDATA\MAID\task-01" # 新任务用新路径，不要预建此目录
$Profile = "$Thread.json"
New-Item -ItemType Directory -Force (Split-Path $Thread) | Out-Null
python configure.py --project $Project --thread $Thread --allow app.py --verify-script verify.py --profile $Profile
~~~

项目配置里的 `repository` 就是 `$Project`；`work_root` 是保存本次任务记录的 `$Thread`。两个目录不能互相包含。可重复使用 `--allow` 指定多个文件。生成器不覆盖已有配置，不调用模型。

## 3. 看草稿，再决定是否执行

~~~powershell
python maid.py request --profile $Profile --thread $Thread --secretary $Secretary "修复 app.py 的求和函数，使 verify.py 通过"
~~~

核对目标和允许修改的文件。草稿中的 `dispatched: false` 表示尚未派工。确认要使用本机登录的 Codex 并允许将通过验收的修改落到配置中的本地任务分支后，运行：

~~~powershell
python maid.py --thread $Thread start --confirm-execute
python maid.py --thread $Thread status
~~~

重开终端后，回到 MAID 目录，把 `$Thread` 设回原路径，只运行 `status` 即可查询验收结果及证据编号，不会重新派工。
