#!/usr/bin/env python3
"""Six-stage acceptance gate. Evidence-only: never implies a paid bounty."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STAGE_NAMES = ("官方开放赏金目标核验", "源码自动分析", "真实目标漏洞验证",
               "有效漏洞报告生成", "经授权提交与官方回执", "实际报告与奖金追踪")

def read(name, root=ROOT):
    try:
        data = json.loads((root / name).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}

def evaluate(reports):
    discovery = reports.get("eligibility_status.json") or {}
    source = reports.get("audit.json") or {}
    scan = reports.get("slither_results.json") or {}
    triage = reports.get("triage_results.json") or {}
    leads = reports.get("lead_verification.json") or {}
    poc = reports.get("specific_poc_results.json") or {}
    submissions = reports.get("submission_status.json") or {}
    projects = scan.get("projects", [])
    sources = source.get("projects", [])
    if not isinstance(projects, list): projects = []
    if not isinstance(sources, list): sources = []
    analyzed = (bool(projects) and bool(sources) and
                all(isinstance(x, dict) and x.get("status") == "analyzed" for x in projects) and
                all(isinstance(x, dict) and x.get("status") == "source retrieved; heuristic review only" for x in sources))
    verified = (leads.get("verified_vulnerabilities", 0) > 0 and
                any(isinstance(c, dict) and c.get("verified") is True
                    for c in leads.get("cases", [])) and
                poc.get("real_world_exploit_verified") is True)
    # "Report drafted" is not the same as a genuine, verified report.
    report_ready = (verified and triage.get("ready_to_submit", 0) > 0 and
                    submissions.get("approved_for_submission", 0) > 0)
    submitted = (report_ready and submissions.get("actual_submissions", 0) > 0 and
                 bool(submissions.get("official_receipts")))
    tracked = (submitted and
               isinstance(discovery.get("official_report_statuses"), list) and
               bool(discovery.get("official_report_statuses")))
    gates = [
        (discovery.get("officially_verified_targets", 0) > 0,
         "缺少官方开放状态、奖励与授权范围的独立核验；候选数量不算"),
        (analyzed, "需要成功的源码获取及 Slither 分析运行记录"),
        (verified, "缺少真实目标可复现漏洞与独立影响证据；模拟 PoC 不算"),
        (report_ready, "缺少可复现真实问题及已验证报告证据"),
        (submitted, "缺少用户授权后实际提交及官方报告回执"),
        (tracked, "缺少实际官方报告状态同步记录；API 连通不算"),
    ]
    steps=[{"stage":i+1,"name":name,"status":"PASS" if ok else "FAIL",
            "reason":"有验收证据" if ok else reason}
           for i,(name,(ok,reason)) in enumerate(zip(STAGE_NAMES,gates))]
    return {"checked_at_utc":datetime.now(timezone.utc).isoformat(),
            "workflow_run_id":os.getenv("GITHUB_RUN_ID",""),
            "workflow_sha":os.getenv("GITHUB_SHA",""),
            "passed":sum(g[0] for g in gates),"total":6,
            "full_acceptance":all(g[0] for g in gates),
            "foundry_control_tests":{"execution":poc.get("execution"),
                                     "passed":poc.get("tests_passed",0),
                                     "synthetic_only":poc.get("conditional_simulation_only") is True},
            "business_outcomes":{"verified_vulnerabilities":leads.get("verified_vulnerabilities",0),
                                 "actual_submissions":submissions.get("actual_submissions",0),
                                 "payout_confirmed_usd":submissions.get("payout_confirmed_usd",0)},
            "stages":steps}

def main():
    names=("eligibility_status.json","audit.json","slither_results.json",
           "triage_results.json","lead_verification.json",
           "specific_poc_results.json","submission_status.json")
    report=evaluate({n:read(n) for n in names})
    (ROOT/"acceptance_status.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# 赏金猎人｜今天的真实验收","",f"六阶段：**{report['passed']}/6 通过**。完整验收：**{'PASS' if report['full_acceptance'] else 'FAIL'}**。","",
           "| 环节 | 结果 | 未通过原因 |","| --- | --- | --- |"]
    for s in report["stages"]:
        lines.append(f"| {s['stage']}. {s['name']} | {s['status']} | {s['reason']} |")
    b=report["business_outcomes"]
    lines.extend(["",f"真实漏洞 **{b['verified_vulnerabilities']}**；实际提交 **{b['actual_submissions']}**；官方确认奖金 **USD {b['payout_confirmed_usd']}**。","",
                  "已通过的模拟测试不等于真实目标漏洞。报告提交必须得到具体授权及官方回执。",""])
    (ROOT/"ACCEPTANCE.md").write_text("\n".join(lines),encoding="utf-8")
    print(f"Six-stage acceptance: {report['passed']}/6; full={report['full_acceptance']}")

if __name__ == "__main__": main()
