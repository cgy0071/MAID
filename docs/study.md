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
