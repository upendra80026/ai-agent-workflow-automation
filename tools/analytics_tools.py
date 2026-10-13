import csv
import os
from typing import List, Dict, Any
from core.tool_registry import register_tool


@register_tool(name="execution_log_reader", description="Loads execution logs from CSV tracking past runs, latencies, and errors", category="analytics")
def load_execution_logs(filepath: str = "data/workflow_logs.csv") -> List[Dict[str, Any]]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Logs file missing: {filepath}")

    logs = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            logs.append({
                "execution_id": row.get("execution_id"),
                "workflow_id": row.get("workflow_id"),
                "workflow_name": row.get("workflow_name"),
                "status": row.get("status"),
                "execution_time_ms": float(row.get("execution_time_ms", 0.0)),
                "error_type": row.get("error_type", ""),
                "timestamp": row.get("timestamp")
            })
    return logs


@register_tool(name="performance_analyzer", description="Calculates failure rates and latencies, flagging workflows above 10% failures or 3000ms latency", category="analytics")
def analyze_workflow_performance(
    filepath: str = "data/workflow_logs.csv",
    failure_threshold_pct: float = 10.0,
    latency_threshold_ms: float = 2500.0
) -> Dict[str, Any]:
    logs = load_execution_logs(filepath)

    grouped = {}
    for log in logs:
        wf_id = log["workflow_id"]
        if wf_id not in grouped:
            grouped[wf_id] = {
                "workflow_id": wf_id,
                "workflow_name": log["workflow_name"],
                "total_runs": 0,
                "success_count": 0,
                "failure_count": 0,
                "total_time_ms": 0.0,
                "errors": []
            }
        g = grouped[wf_id]
        g["total_runs"] += 1
        g["total_time_ms"] += log["execution_time_ms"]
        if log["status"] == "SUCCESS":
            g["success_count"] += 1
        else:
            g["failure_count"] += 1
            if log["error_type"]:
                g["errors"].append(log["error_type"])

    metrics_list = []
    flagged_workflows = []

    for wf_id, data in grouped.items():
        total = data["total_runs"]
        fail_count = data["failure_count"]
        fail_rate = round((fail_count / total) * 100.0, 2) if total else 0.0
        avg_time = round(data["total_time_ms"] / total, 1) if total else 0.0

        # Most frequent error
        error_counts = {}
        for err in data["errors"]:
            error_counts[err] = error_counts.get(err, 0) + 1
        top_error = max(error_counts.items(), key=lambda x: x[1])[0] if error_counts else "None"

        # Decision Logic: Flag workflows with failure rate above 10% or average execution time above defined threshold
        reasons = []
        if fail_rate > failure_threshold_pct:
            reasons.append(f"High Failure Rate ({fail_rate}% > {failure_threshold_pct}%)")
        if avg_time > latency_threshold_ms:
            reasons.append(f"Elevated Latency ({avg_time}ms > {latency_threshold_ms}ms)")

        is_flagged = len(reasons) > 0

        metric_entry = {
            "workflow_id": wf_id,
            "workflow_name": data["workflow_name"],
            "total_runs": total,
            "success_rate_pct": round(100.0 - fail_rate, 2),
            "failure_rate_pct": fail_rate,
            "avg_execution_time_ms": avg_time,
            "top_error": top_error,
            "is_flagged": is_flagged,
            "flag_reasons": reasons
        }
        metrics_list.append(metric_entry)

        if is_flagged:
            # Actionable recommendations
            recs = []
            if fail_rate > failure_threshold_pct:
                recs.append(f"Implement retry exponential backoff and sanitize upstream payloads for '{top_error}'")
            if avg_time > latency_threshold_ms:
                recs.append("Add response caching and parallelize multi-step LLM completion calls")

            flagged_workflows.append({
                **metric_entry,
                "recommendations": recs
            })

    # Sort flagged workflows by failure rate descending
    flagged_workflows.sort(key=lambda x: x["failure_rate_pct"], reverse=True)
    metrics_list.sort(key=lambda x: x["workflow_id"])

    return {
        "total_log_entries_analyzed": len(logs),
        "total_workflows_evaluated": len(metrics_list),
        "flagged_workflows_count": len(flagged_workflows),
        "failure_threshold_applied": f"{failure_threshold_pct}%",
        "latency_threshold_applied": f"{latency_threshold_ms}ms",
        "flagged_workflows": flagged_workflows,
        "all_metrics": metrics_list
    }
