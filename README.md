# MAID 秘书处

在 Windows 上与 Gemini 对话，按项目提交任务、启动执行、查阅审核结果。会话使用 agy，任务、授权和验收由 AWO 管理。

需要 Python 3.10+。使用 Gemini 前，请在本机登录 agy，用 `agy models` 查看可选模型。从项目目录运行：

```powershell
git submodule update --init
python maid.py --thread threads/demo chat --model gemini-3.8-flash-low
```

输入问题即可交谈。输入 `exit` 后，再执行同一命令即可续聊。任务操作需要 AWO 项目任务描述文件，在对话中输入 `submit SPEC_PATH`，随后输入 `start --confirm-execute` 启动。输入 `status` 查询任务的独立审核结果。

当前为源码开发版。入口随 MAID 管理，秘书实现和调度依赖固定在 AWO 提交 5deb47c。自然语言自动生成并派发任务仍待实现。
