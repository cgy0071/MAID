# Multi-Agent Inter-harness Dispatch - Your Multi-Agent Project Secretary

English | [Chinese](README.zh-CN.md)

When you juggle several coding or research projects at once, you should not have to hop across a dozen terminals to track what each AI changed. **MAID is your multi-agent project secretary**: talk to one secretary about your goals and boundaries, review a clear task draft before any work begins, and get concise, evidence-backed reports when independent review finishes.

## How it works

![From request to independent review](docs/images/maid-overview.svg)

Tell your secretary which project you mean and what you want to achieve. It prepares a **task draft** spelling out the goal, the files that may change, and how success will be verified. Send the draft back if the scope is off; **nothing is dispatched until you explicitly approve it**. Execution and independent review can run on a compatible backend engine such as [AWO](https://github.com/cgy0071/agent-workflow-orchestrator), and your secretary reports the verdict and evidence ID back to you.

> MAID and AWO are two independent projects with separate releases; the documented dispatch-and-review workflow pairs MAID with a compatible AWO checkout.

## Core modules and capabilities

- **Flexible secretary interface, direct terminal escape hatch**
  Runs with **Antigravity CLI (agy)** by default, or switch to **Claude** or another trusted local command. Stay in one conversation with your secretary, or jump straight into an executor's terminal whenever you want hands-on control.
- **Draft-first approval gate**
  Every request produces an undispatched draft listing the target repository, allowed file scope, and verification check. No code is touched and no paid execution runs until you confirm.
- **Multi-project index and session recovery**
  A local index maps project and task names to their working directories. Switch between projects freely, or close and reopen your terminal to check status, review verdicts, and evidence IDs without ever triggering duplicate dispatch.
- **Authorized read-only project knowledge**
  Attach an authorized published document when a task needs reference material. Version and permission checks run during both drafting and task preparation; once access is revoked, future reads are blocked.
- **Plain-language reporting**
  Your secretary leads with what happened and what it means for your project, translates internal jargon into plain language, and preserves exact numbers, verbatim quotes, evidence IDs, and open items.

## Three things that always stay in your hands

1. **Independent role choices**: pick your secretary separately from the worker that edits code.
2. **Explicit file boundaries**: each task gets its own thread, and you approve which files may change.
3. **Review before done**: never take a worker's word for it; wait for the independent review verdict and evidence ID.

## Let your AI set this up

You do not need to type setup commands by hand. Copy this prompt into your local AI assistant (Codex, Claude Code, Antigravity CLI (agy), or Cursor) to install and verify MAID safely:

~~~text
Help me set up Multi-Agent Inter-harness Dispatch (MAID) by following docs/setup.md in this repository.
First check Git, Python 3.10+, and installed AI clients. Ask me which folder to use, and install the documented release into a fresh subdirectory.
Run only maid.py doctor to verify the compatible backend.
Do not modify my existing projects, accounts, or keys, and do not make paid model calls or dispatch real work.
Report the check results and the next command, then wait for my decision.
~~~

## Further reading

- [Manual setup and walkthrough](docs/setup.md): full steps for choosing a secretary, binding a Git repo, drafting, and confirming dispatch
- [Multi-project indexing, shared scheduling, and troubleshooting](docs/setup.md#troubleshooting): managing multiple projects with a local index, session recovery, and common fixes
- [Secretary reporting rules](SECRETARY.md): plain-language reporting while keeping numbers, quotes, and evidence IDs exact
- [AWO backend workflow and review engine](https://github.com/cgy0071/agent-workflow-orchestrator#readme): how isolated execution, independent review, and knowledge search work under the hood
