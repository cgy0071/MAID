# Multi-Agent Inter-harness Dispatch (MAID)

English | [Chinese](README.zh-CN.md)

MAID is a secretary for people managing several projects. Name the project and the result you want. Your secretary drafts a task with the allowed files and a way to check the work. Choose Antigravity CLI (agy), Claude or another local command.

## How it works

![From request to independent review](docs/images/maid-overview.svg)

Return a draft for revision or approve it. The documented dispatch workflow uses [AWO](https://github.com/cgy0071/agent-workflow-orchestrator) to execute the task and review it independently. The two projects release separately; this workflow requires a compatible AWO checkout.

## Working with your secretary

### Choose the conversation

Use Antigravity CLI (agy) by default, choose Claude, or configure another trusted local client.
You can open the executor's terminal directly; Antigravity CLI also lets you reopen the secretary thread, while the example Claude profile starts a fresh conversation per turn.

### Review a draft before anyone starts

Ask for a concrete change: for example, fix a calculation in one file and check it with the project's verification script.
The draft names the project, allowed files and check; send it back if the scope is wrong, or confirm it to authorize dispatch.

### Find a task after switching projects

The local index maps project and task names to their working directories, so you can leave one task and work on another.
After a restart, select the original task to retrieve its recorded status, review decision and evidence ID without sending it again.

### Give a task a source to read

When a draft depends on a project document, name the published document that the task is allowed to read.
The compatible backend checks its revision and permission during drafting and again during preparation; revoking access blocks future reads.

### Get a report you can act on

The secretary leads with what happened and what it means for your project, then gives the evidence or the decision it needs from you.
It explains unfamiliar terms and keeps measurements, quotes and failure reasons intact.

## What you control

- Choose the secretary separately from the worker.
- Keep a separate thread for each task and approve its allowed files.
- Check the independent review before treating delivery as complete.

## Let your AI set this up

Paste this into your local AI assistant to check the setup before starting a task.

~~~text
Help me set up Multi-Agent Inter-harness Dispatch (MAID) using docs/setup.md in the maid repository.
Check Git, Python 3.10+ and installed clients.
Ask for a destination; use the documented release in a fresh subdirectory.
Run only the maid.py doctor checks against the documented compatible backend.
Do not modify my projects, accounts or keys, make paid calls, or dispatch work.
Report results and the next command, then stop.
~~~

## Guides

[Manual setup, troubleshooting and advanced guides](docs/setup.md) | [Secretary reporting rules](SECRETARY.md)
