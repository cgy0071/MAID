# Multi-Agent Inter-harness Dispatch (MAID)

English | [Chinese](README.zh-CN.md)

MAID is a secretary for people managing several projects. Name the project and the result you want. Your secretary drafts a task with the allowed files and a way to check the work. Choose Antigravity CLI (agy), Claude or another local command.

## How it works

![From request to independent review](docs/images/maid-overview.svg)

Return a draft for revision or approve it. The documented dispatch workflow uses [AWO](https://github.com/cgy0071/agent-workflow-orchestrator) to execute the task and review it independently. The two projects release separately; this workflow requires a compatible AWO checkout.

## Capabilities and safeguards

Switch projects and tasks by name. After reopening a terminal, retrieve the original status, review and evidence ID without sending the task again. You can still speak directly to the executor in its terminal.

## Let your AI set this up

~~~text
Help me set up Multi-Agent Inter-harness Dispatch (MAID) using docs/setup.md in the maid repository. Check Git, Python 3.10+ and installed clients. Ask for a destination; use the documented release in a fresh subdirectory. Run only the maid.py doctor checks against the documented compatible backend. Do not modify my projects, accounts or keys, make paid calls, or dispatch work. Report results and the next command, then stop.
~~~

## Guides

[Manual setup, troubleshooting and advanced guides](docs/setup.md) | [Secretary reporting rules](SECRETARY.md)
