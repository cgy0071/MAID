"""Render an optional status card without changing the protocol on stdout."""


def render(response):
    result = response.get("result", response)
    recovery = result.get("recovery")
    if isinstance(recovery, dict):
        return recovery_card(recovery)
    return status_card(response)


def recovery_card(report):
    actions = {"continue": "原执行者继续", "manual": "人工接手", "reassign": "换人重派"}
    if report.get("action") in actions and report.get("action_id"):
        lines = ["交接已记录：" + actions[report["action"]], "接手人：" + str(report["recipient"]),
                 "本回执只证明交接；交付与独立审核请查看任务状态。"]
        for key, label in (("workspace", "保留的工作区"), ("thread", "接手任务目录"),
                           ("checkpoint_commit", "交接提交")):
            if report.get(key):
                lines.append(label + "：" + str(report[key]))
        return "\n".join(lines)
    h = report.get("handoff")
    if not isinstance(h, dict):
        return ""
    steps = {"workspace_ready": "工作区已就绪", "assignment_claimed": "任务已认领", "prepared": "准备完成"}
    last = h.get("last_receipted_step")
    lines = ["中断诊断（只读）",
             "最后有回执的步骤：" + str(steps.get(last, last) or "未核实"),
             "工作区：" + str(h.get("workspace") or "未核实"),
             "当前提交：" + str(h.get("head") or "未核实")]
    for key, label in (("committed_changes", "已提交改动"), ("uncommitted_changes", "未提交改动")):
        entries = h.get(key)
        changes = "未核实"
        if h.get("workspace_available") and isinstance(entries, list):
            changes = "；".join(" ".join(x) if isinstance(x, list) else str(x) for x in entries) or "无"
        lines.append(label + "：" + changes)
    isolation = {"not_dispatched": "从未派工给旧执行者", "host_fenced": "宿主已确认旧执行者不能再写"}
    lines.append("旧执行者写权限：" + isolation.get(h.get("writer_isolation"), "未能证实已停写"))
    session = h.get("session") or {}
    lines.append("原会话：" + ("可恢复" if session.get("resume") is True else "未确认可恢复"))
    allowed = [actions[k] for k in h.get("allowed_actions", []) if k in actions]
    lines.append("可选操作：" + ("、".join(allowed) or "仅查看与核查，请勿重派"))
    lines.append("观察到的状态版本：" + str(h.get("state_version") or "未核实"))
    return "\n".join(lines)


def status_card(response):
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
    rework = c.get("rework")
    if isinstance(rework, dict) and rework.get("previous_review") == "repair":
        lines.append("上次交付/审核：" + str(rework["previous_commit"]) + "，要求返工")
        lines.append("本次返工：" + labels.get(rework.get("state"), "状态待核实"))
    session = c.get("session")
    if isinstance(session, dict) and session.get("records") is True:
        lines.append("查看记录 / 查看交付和工作区：session --action records")
        if session.get("focus") is True:
            lines.append("定位原终端：session --action focus")
        if session.get("resume") is True:
            lines.append("恢复原生对话：session --action resume")
    return "\n".join(lines)
