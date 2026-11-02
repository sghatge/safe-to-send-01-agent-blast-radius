"""Agent blast radius: what is the worst an AI agent could do with the access you gave it?

Reads an agent's tool grants and the controls in place, and reports which dangerous
CRM outcomes are reachable, in how many calls, and which control (if any) stops them.
Standard library only. Synthetic data only.
"""
import json
import sys

# Each dangerous outcome is a chain of tool:mode steps an agent would need.
# "mitigated_by" lists controls that stop the chain before it reaches customers or data.
OUTCOMES = [
    {"id": "full_table_delete", "label": "Full-table DELETE on recipients", "severity": 10,
     "steps": ["schema_browse:read", "query_run:write"], "mitigated_by": ["sql_write_block"]},
    {"id": "pause_gdpr_purge", "label": "Pause the GDPR purge workflow", "severity": 9,
     "steps": ["workflow_control:list", "workflow_control:stop"], "mitigated_by": ["protected_workflows"]},
    {"id": "pii_egress", "label": "Copy recipient personal data outside the platform", "severity": 9,
     "steps": ["query_run:read", "js_execute:http"], "mitigated_by": ["egress_block", "pii_masking"]},
    {"id": "consent_overwrite", "label": "Bulk-overwrite marketing consent", "severity": 9,
     "steps": ["js_execute:write"], "mitigated_by": ["js_dry_run_only"]},
    {"id": "send_no_unsubscribe", "label": "Send a delivery with no unsubscribe link", "severity": 8,
     "steps": ["delivery_send:execute"], "mitigated_by": ["presend_qa", "human_approval_on_send"]},
    {"id": "wrong_audience_send", "label": "Send to an unfiltered audience (no consent filter)", "severity": 8,
     "steps": ["query_run:read", "delivery_send:execute"], "mitigated_by": ["presend_qa", "human_approval_on_send"]},
]


def granted(grants, step):
    tool, mode = step.split(":")
    return mode in grants.get(tool, [])


def analyse(grants, controls, outcomes=OUTCOMES):
    """Return one row per outcome: reachable?, calls needed, stopped by which control."""
    rows = []
    for o in outcomes:
        reachable = all(granted(grants, s) for s in o["steps"])
        stoppers = [c for c in o["mitigated_by"] if c in controls]
        if not reachable:
            status = "unreachable"
        elif stoppers:
            status = "mitigated"
        else:
            status = "EXPOSED"
        rows.append({"id": o["id"], "label": o["label"], "severity": o["severity"],
                     "calls": len(o["steps"]), "status": status, "stopped_by": stoppers})
    order = {"EXPOSED": 0, "mitigated": 1, "unreachable": 2}
    rows.sort(key=lambda r: (order[r["status"]], -r["severity"], r["calls"]))
    return rows


def risk_score(rows):
    """0-100: share of total severity that is exposed with no control."""
    total = sum(r["severity"] for r in rows) or 1
    exposed = sum(r["severity"] for r in rows if r["status"] == "EXPOSED")
    return round(100 * exposed / total)


def render(name, rows):
    lines = [f"# Blast radius: {name}", "", f"Exposure score: **{risk_score(rows)}/100**", "",
             "| Status | Outcome | Severity | Calls away | Stopped by |", "|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['status']} | {r['label']} | {r['severity']} | {r['calls']} | "
                     f"{', '.join(r['stopped_by']) or '-'} |")
    return "\n".join(lines)


def main(path):
    with open(path, encoding="utf-8") as fh:
        agent = json.load(fh)
    rows = analyse(agent["grants"], agent.get("controls", []))
    print(render(agent["name"], rows))
    return 1 if any(r["status"] == "EXPOSED" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "examples/black_friday_helper.json"))
