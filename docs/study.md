# Learning with MAID / 独立学习

Run `python -B maid.py study --library PATH`. Select one or more source IDs, describe what you already know, and enter your learning goal. Use `ask QUESTION`, `open 1`, `answer 1 YOUR ANSWER`, `save YOUR OWN WORDS`, or `quit`. Numbers refer to the latest response. The default tutor is an offline reading guide. Add `--secretary PROFILE` for a custom model tutorial, using a trusted local secretary profile or agy. The selected excerpts and your learning goal will be sent to that secretary.

运行上述命令后，选择资料并说明已懂什么、想学什么。输出分列原文、阅读引导或 AI 解释、自测题。输入 `open 1` 回看本轮第 1 条原文，PDF 给出物理页码，Markdown 给出 UTF-8 字节区间。可追问或作答，再核对原文。输入 `save 自己的理解` 才在个人目录写入笔记与来源指针。

Use the AWO checkout containing the stage A facade (set MAID_AWO_ROOT if it is not a sibling). Text PDFs require pypdf. Put the UTF-8 JSON catalog in your **private local directory**. Only list files you personally authorize for reading. Each file entry grants that exact revision. Remove an entry to revoke it. An AWO document entry always uses the current document credential. Personal study notes go in personal-study-notes beside the catalog.

```json
{
  "sources": {
    "paper": {"file": "D:/personal/paper.pdf", "sha256": "<64 hex digits>"},
    "methods": {"file": "D:/personal/methods.md", "sha256": "<64 hex digits>"},
    "published": {"doc_id": "<published AWO document ID>"}
  },
  "awo": {"state": "D:/local/state", "root": "D:/local/project", "token_file": "D:/private/doc.token"}
}
```

Use `Get-FileHash -Algorithm SHA256 <file>` and lowercase its digest. Omit the awo section for a personal-files-only catalog. Protect the catalog and token file with your OS user permissions. Keep personal notes outside your source repository.

## Turn a selection into a draft / 将选段带入任务草案

Use `python maid.py request --query "latency" --target target.json --out draft.json`.
Keep the displayed excerpt numbers (for example 1,3), choose all, or cancel.
For learning, start study with `--target target.json --draft-out draft.json`,
then enter `draft 1,3` using original passage numbers from the latest answer.
The draft records pointers, goal, task, project, and digests. A missing grant
or changed revision blocks the operation. An empty search displays no_hits.

The target is a private local JSON file, for example:

~~~json
{"state":"D:/local/state","root":"D:/local/project","project_id":"PROJECT_ID",
 "task":"TARGET_TASK","task_token_file":"D:/private/task.token",
 "doc_token_file":"D:/private/document.token","kb":true,
 "personal_sources":{"paper":{"kind":"pdf","record_id":"S2"}}}
~~~

The target task must already exist. For published documents its AWO task body
lists allowed IDs under evidence_document_ids. Use a separate document read
credential for the same recipient. For KB records enable kb and grant the
target task read access in the plugin. To hand a personal file excerpt over,
map its library ID to the target's verified SRC record in personal_sources.
The backend compares the source file digest, excerpt digest, and physical
page or byte range. Keep token files and target configurations private.

主题查询可删选、取消；学习会话中的 draft 命令只接受原文编号。
个人资料须先有目标任务获准读取的对应记录。草案文件只保存指针，正文仅在预览中显示。

### Confirm selected evidence

After reading the draft, copy the displayed draft_sha256. Use
`maid.py runs --index INDEX --project PROJECT --run RUN start --confirm-execute --draft DRAFT.json --draft-digest SHA256`.
Prepare the named run first with an evidence_route in its operator-owned spec.
A previous confirmation cannot authorize a changed selection. If a source or
permission changed, review a fresh draft. Use status or recover for a run that
has already started; never create another run to retry its dispatch.

### Read the evidence decision or recover a run

For a confirmed evidence draft, the worker's RESULT.md ends with a JSON block:
each conclusion names its original excerpt and exact location. The independent
reviewer's REVIEW.md records which citations support each conclusion and why.
Only the AWO ledger assigns an accepted evidence ID. A missing citation or an
unsupported conclusion requires repair or rejection; unavailable material
blocks the read.

After reopening MAID, use the same index, project and run with the status
operation. Read result.task.accepted_evidence_id; a missing ID is not acceptance.
If the run stopped after freezing but before dispatch, start the same run with
the original digest. If dispatch was attempted and its receipt is missing,
inspect status and use recover on that run. Do not create a replacement run.
