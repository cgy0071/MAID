# MAID · 秘书处

**Multi-Agent Inter-harness Dispatch** · 面向异构 Harness 的多智能体秘书协同调度框架

你可以只和一名秘书对话，也可以在 Herdr 或习惯的终端直接与执行者交流。秘书默认用 **agy**，可以换成 Claude 等本地命令；本预览版的一次性任务由 **Codex 执行和审查**。

**[下载 Windows 预览版 ZIP](https://github.com/cgy0071/MAID/releases/download/v0.1.0-preview.3/MAID-Windows-0.1.0-preview.3.zip)** · [发行说明和 SHA-256](https://github.com/cgy0071/MAID/releases/tag/v0.1.0-preview.3)。完整解压，在含有 `maid.py` 的目录打开 PowerShell。需要 Python 3.10+；运行项目任务还需要 Git 和已登录的 Codex CLI。源码用户请用 `git clone --recurse-submodules https://github.com/cgy0071/MAID.git`。

## 1. 选择秘书

先安装并登录想用的 CLI。在 PowerShell 中从下列两行**任选一行**，之后的命令都会使用这个秘书：

~~~powershell
$Secretary = 'agy'                                    # 默认：Antigravity CLI
$Secretary = '.\vendor\awo\examples\maid-secretary-claude.json' # Claude CLI，无需 agy
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

重开终端后，回到解压目录，把 `$Thread` 设回原路径，只运行 `status` 即可查询验收结果及证据编号，不会重新派工。
