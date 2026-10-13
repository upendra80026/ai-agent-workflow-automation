import re
from typing import Dict, Any, Tuple, Optional
from core.models import WorkflowDefinition
from core.excel_loader import load_workflows_from_excel

try:
    from rapidfuzz import fuzz
except ImportError:
    class FuzzFallback:
        @staticmethod
        def token_set_ratio(s1: str, s2: str) -> float:
            w1 = set(s1.lower().split())
            w2 = set(s2.lower().split())
            if not w1 or not w2:
                return 0.0
            return round((len(w1 & w2) / len(w1 | w2)) * 100.0, 1)
    fuzz = FuzzFallback()


class WorkflowRouter:
    """
    Intelligent Workflow Router that identifies which business workflow
    corresponds to a natural language user request based on Excel triggers.
    Supports dynamic registration of any number of workflows without code changes.
    """

    def __init__(self, workflows: Optional[Dict[str, WorkflowDefinition]] = None):
        self.workflows = workflows or load_workflows_from_excel()
        self._init_semantic_signatures()

    def _init_semantic_signatures(self):
        """Constructs search signatures and keyword associations for dynamic matching."""
        self.signatures = {}
        for wf_id, wf in self.workflows.items():
            combined = f"{wf.workflow_name} {wf.trigger} {wf.inputs} {wf.decision_logic}".lower()
            self.signatures[wf_id] = combined

    def extract_parameters(self, user_request: str) -> Dict[str, Any]:
        """Extracts contextual arguments (IDs, thresholds, entities) from request."""
        params = {}
        text = user_request.strip()

        # Order ID extraction
        order_match = re.search(r"\b(ORD-\d+|#\d+)\b", text, re.IGNORECASE)
        if order_match:
            params["order_id"] = order_match.group(1).upper()

        # Percentage threshold extraction (e.g. 10%, 15%)
        pct_match = re.search(r"(\d+(\.\d+)?)\s*%", text)
        if pct_match:
            params["threshold_pct"] = float(pct_match.group(1))

        # Email extraction
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        if email_match:
            params["customer_email"] = email_match.group(0)

        # Refund policy age extraction. Keep this separate from order lookup
        # because the request may explicitly override the stored order age.
        days_patterns = (
            r"\b(\d+)\s*days?\s*(?:ago|old)\b",
            r"\bpurchased\s+(\d+)\s*days?\s*ago\b",
            r"\b(\d+)\s*days?\s*since\s*(?:purchase|purchased)\b",
        )
        for pattern in days_patterns:
            days_match = re.search(pattern, text, re.IGNORECASE)
            if days_match:
                params["days"] = int(days_match.group(1))
                break

        # File mention
        if ".xlsx" in text.lower() or ".csv" in text.lower() or "spreadsheet" in text.lower():
            params["file_context"] = True

        return params

    def route(self, user_request: str) -> Tuple[WorkflowDefinition, float, str, Dict[str, Any]]:
        """
        Routes the user request to the optimal workflow definition.
        Returns: (WorkflowDefinition, confidence_score, reasoning, extracted_params)
        """
        clean_query = user_request.strip()
        query_lower = clean_query.lower()
        extracted_params = self.extract_parameters(clean_query)

        best_wf_id = None
        best_score = -1.0
        reasoning = ""

        # High-precision domain keyword mapping
        domain_anchors = {
            "WF001": ["restock", "inventory", "stock threshold", "low stock", "reorder", "safety stock"],
            "WF002": ["vendor price", "price difference", "validate price", "pricing difference", "differ by more than", "price validation"],
            "WF003": ["vendor spreadsheet", "invalid rows", "process vendor", "clean dataset", "cleaned file", "dirty data", "vendor file"],
            "WF004": ["seo content", "product description", "generate content for this product", "meta description", "product copy"],
            "WF005": ["order ord-", "where is order", "order status", "shipment tracking", "track order", "customer order"],
            "WF006": ["duplicate product", "find duplicate", "catalog duplicate", "sku match", "likely duplicate"],
            "WF007": ["campaign brief", "marketing brief", "new collection", "campaign goal", "promotional campaign"],
            "WF008": ["classify these keywords", "seo keyword", "keyword list", "search intent", "map keywords to pages"],
            "WF009": ["assign this urgent task", "assign task", "best available developer", "assign employee", "workload", "task assignment"],
            "WF010": ["failing most often", "performance report", "workflow logs", "execution logs", "failure rate", "slow steps"],
            "WF011": [
                "refund", "refund order", "return request", "refund policy",
                "approve return", "purchased", "days ago"
            ]
        }

        # Step 1: Check domain anchor hits
        anchor_scores = {}
        for wf_id, anchors in domain_anchors.items():
            if wf_id in self.workflows:
                matched_anchors = [a for a in anchors if a in query_lower]
                if matched_anchors:
                    anchor_scores[wf_id] = len(matched_anchors) * 35.0

        # Step 2: Fuzzy semantic matching against Trigger & Name
        fuzzy_scores = {}
        for wf_id, wf in self.workflows.items():
            name_sim = fuzz.token_set_ratio(query_lower, wf.workflow_name.lower())
            trigger_sim = fuzz.token_set_ratio(query_lower, wf.trigger.lower())
            combined_sim = max(name_sim, trigger_sim)
            fuzzy_scores[wf_id] = combined_sim

        # Step 3: Combine scores
        scored_candidates = []
        for wf_id, wf in self.workflows.items():
            f_score = fuzzy_scores.get(wf_id, 0.0)
            a_score = anchor_scores.get(wf_id, 0.0)
            total_score = min(100.0, f_score + a_score)
            scored_candidates.append((wf_id, total_score))

        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        top_wf_id, top_score = scored_candidates[0]

        selected_wf = self.workflows[top_wf_id]
        normalized_confidence = min(0.99, max(0.60, round(top_score / 100.0, 2)))

        reasoning = (
            f"Query matched Workflow {selected_wf.workflow_id} ('{selected_wf.workflow_name}') "
            f"based on intent trigger '{selected_wf.trigger}' with {normalized_confidence*100:.0f}% confidence."
        )

        return selected_wf, normalized_confidence, reasoning, extracted_params


# Global router
workflow_router = WorkflowRouter()
