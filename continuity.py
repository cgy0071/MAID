"""Render an optional status card without changing the protocol on stdout."""


def render(response):
    c = response.get("result", response).get("continuity")
    if not isinstance(c, dict) or c.get("version") != 1:
        return ""
    labels = {"running": "运行中", "blocked": "卡住了", "decision": "等我决定",
              "awaiting_review": "已交付待审核", "unknown": "状态待核实",
              "accepted": "审核通过", "repair": "需要返工", "reject": "审核拒绝"}
    changes = c.get("changes")
    lines = ["任务：" + labels.get(c.get("state"), "状态待核实"),
             "改了什么：" + ("、".join(changes) if changes else "尚无改动记录"),
             "查了什么：" + ("；".join(f"{v['name']} (exit {v['returncode']})"
                                  for v in c.get("checks", [])) or "尚无检查回执"),
             "还有哪些问题：" + ("；".join(c.get("issues", [])) or "暂无已记录问题"),
             "交付：" + ("已交付" if c.get("delivered") else "未登记"),
             "独立审核：" + (labels.get(c.get("review")) or
                          {"accept": "通过"}.get(c.get("review"), "尚无结论")),
             "合并：" + (c.get("merge") or "未登记")]
    if c.get("accepted_evidence_id"):
        lines.append("验收证据：" + c["accepted_evidence_id"])
    if c.get("decision"):
        lines.append(c["decision"]["question"])
        lines.extend(f"  {option}: {impact}" for option, impact in c["decision"]["options"])
    session = c.get("session")
    if isinstance(session, dict) and session.get("records") is True:
        lines.append("查看记录 / 查看交付和工作区：session --action records")
        if session.get("focus") is True:
            lines.append("定位原终端：session --action focus")
        if session.get("resume") is True:
            lines.append("恢复原生对话：session --action resume")
    return "\n".join(lines)
