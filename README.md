# MAID 秘书处

在 Windows 上与 Gemini 对话，按项目提交任务、启动执行、查阅审核结果。会话使用 agy，任务、授权和验收由 AWO 管理。

需要 Python 3.10+。使用 Gemini 前，请在本机登录 agy，用 `agy models` 查看可选模型。从项目目录运行：

```powershell
git submodule update --init
python maid.py --thread threads/demo chat --model gemini-3.8-flash-low
```

输入问题即可交谈。输入 `exit` 后，再执行同一命令即可续聊。任务操作需要 AWO 项目任务描述文件，在对话中输入 `submit SPEC_PATH`，随后输入 `start --confirm-execute` 启动。输入 `status` 查询任务的独立审核结果。

当前为源码开发版。入口随 MAID 管理，秘书实现和调度依赖固定在 AWO 提交 5deb47c。

已有受信任的 AWO 项目任务配置时，可以让秘书根据一句话准备任务。配置提供仓库、可修改文件、验收命令、执行者、审核者和预算。下面的 profile.json 指向你自己的配置。

```powershell
python maid.py request --profile profile.json --thread threads/sum --model gemini-3.8-flash-low "修复求和函数，空列表返回零"
python maid.py --thread threads/sum start --confirm-execute
python maid.py --thread threads/sum status
```

第一条命令显示需求原文、秘书拟定的目标和可修改文件。核对后运行第二条；第三条可以在重新打开终端后查询验收结果和证据编号。
