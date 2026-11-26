# Multi-Agent Inter-harness Dispatch (MAID)

[English](README.md) | 中文

MAID 是多项目秘书。告诉它要做哪个项目、希望得到什么结果，它会起草一份任务单，写清可改哪些文件、怎样检查结果。默认秘书是 Antigravity CLI (agy)，也可选 Claude 或自定义本地命令。

## 怎么运作

![从请求到独立审核](docs/images/maid-overview.zh-CN.svg)

草稿范围不对就退回修改。你确认后，示例工作流通过 [AWO](https://github.com/cgy0071/agent-workflow-orchestrator) 执行并独立审核，再由秘书汇报。两者独立发布；运行这条派工流程需配置兼容的 AWO。

## 核心能力与安全底线

按项目和任务名切换；重开终端后可查原任务的进度、审核结论和证据编号，无需重新派工。你仍可直接与终端里的执行者对话。

## 让 AI 帮你部署

~~~text
请按 maid 仓库的 docs/setup.zh-CN.md 帮我部署。先检查 Git、Python 3.10+ 和已安装客户端；询问目标目录，仅在新的子目录中使用手册指定的正式版本。只运行 maid.py doctor 自检，检查兼容后端。不要修改我的项目、账号或密钥，不调用付费模型、不真实派工。汇报检查结果和下一条命令，等我决定。
~~~

## 详细手册

[手动配置、排错与进阶导航](docs/setup.zh-CN.md) | [秘书汇报规范](SECRETARY.md)
