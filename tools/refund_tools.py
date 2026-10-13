import json
import os
from typing import Dict, Any
from core.tool_registry import register_tool
from tools.order_tools import lookup_order_record


@register_tool(name="refund_policy_evaluator", description="Evaluates customer refund requests against the 30-day policy and auto-approval limits", category="refund")
def evaluate_refund_request(order_id: str, reason: str = "Defective item", days_since_purchase: int = 7) -> Dict[str, Any]:
    order = lookup_order_record(order_id)
    if not order:
        return {
            "approved": False,
            "status": "REJECTED_ORDER_NOT_FOUND",
            "message": f"Order {order_id} could not be found in active records."
        }

    amount = order.get("total_amount", 0.0)

    # Decision Logic: If days_since_purchase <= 30 and amount < $500, auto-approve; otherwise route for manual review
    is_within_window = days_since_purchase <= 30
    is_under_limit = amount < 500.0

    if is_within_window and is_under_limit:
        return {
            "order_id": order_id,
            "approved": True,
            "status": "AUTO_APPROVED",
            "refund_amount": f"${amount:.2f}",
            "reason": reason,
            "days_elapsed": days_since_purchase,
            "decision_rule": f"Days elapsed ({days_since_purchase}) <= 30 policy limit AND amount (${amount}) < $500 threshold",
            "action": f"Refund of ${amount:.2f} credited to original payment method. Transaction ID: REF-TXN-{order_id.replace('ORD-', '')}"
        }
    else:
        reasons = []
        if not is_within_window:
            reasons.append(f"Exceeds 30-day standard return window ({days_since_purchase} days elapsed)")
        if not is_under_limit:
            reasons.append(f"Amount (${amount}) exceeds $500 auto-approval threshold")

        return {
            "order_id": order_id,
            "approved": False,
            "status": "PENDING_SUPERVISOR_REVIEW",
            "refund_amount": f"${amount:.2f}",
            "reason": reason,
            "days_elapsed": days_since_purchase,
            "decision_rule": "Escalated to Operations Supervisor: " + "; ".join(reasons),
            "action": f"Manual ticket created (#SUP-{order_id}). Customer notified of 24h escalation SLA."
        }
