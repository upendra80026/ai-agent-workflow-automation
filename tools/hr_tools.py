import json
import os
from typing import List, Dict, Any, Optional
from core.tool_registry import register_tool


@register_tool(name="employee_database_reader", description="Loads employee skills, current workload hours, and capacity", category="hr")
def load_employees(filepath: str = "data/employees.json") -> List[Dict[str, Any]]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Employee database file missing: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


@register_tool(name="candidate_ranking_engine", description="Evaluates required skills and capacity, ranks employees, and triggers escalation if no suitable match exists", category="hr")
def assign_employee_task(
    task_description: str,
    required_skills: Optional[List[str]] = None,
    estimated_hours: int = 8,
    priority: str = "High",
    deadline: str = "Friday, 5:00 PM",
    roster_path: str = "data/employees.json"
) -> Dict[str, Any]:
    employees = load_employees(roster_path)

    # If required skills not explicitly provided, extract from description
    if not required_skills:
        desc_lower = task_description.lower()
        extracted = []
        for kw in ["python", "fastapi", "react", "docker", "llm", "langchain", "devops", "cloud", "security"]:
            if kw in desc_lower:
                extracted.append(kw.capitalize() if kw != "llm" else "LLM")
        required_skills = extracted or ["Python", "Backend"]

    candidates = []

    for emp in employees:
        emp_skills_lower = [s.lower() for s in emp.get("skills", [])]
        matched_skills = [s for s in required_skills if s.lower() in emp_skills_lower]
        skill_match_pct = round((len(matched_skills) / len(required_skills)) * 100.0, 1) if required_skills else 0.0

        current_workload = emp.get("current_workload_hours", 0)
        max_capacity = emp.get("max_capacity_hours", 40)
        available_hours = max_capacity - current_workload
        has_capacity = available_hours >= estimated_hours

        # Ranking score: skill match (60%) + capacity availability (40%)
        capacity_score = min(100.0, (available_hours / 15.0) * 100.0) if available_hours > 0 else 0.0
        composite_score = round((skill_match_pct * 0.6) + (capacity_score * 0.4), 1)

        candidates.append({
            "id": emp["id"],
            "name": emp["name"],
            "role": emp["role"],
            "skills": emp["skills"],
            "matched_skills": matched_skills,
            "skill_match_pct": skill_match_pct,
            "current_workload_hours": current_workload,
            "available_hours": available_hours,
            "has_capacity": has_capacity,
            "composite_score": composite_score,
            "eligible": (len(matched_skills) > 0) and has_capacity
        })

    # Sort: Eligible first, then highest composite score, then highest available capacity
    candidates.sort(key=lambda x: (x["eligible"], x["composite_score"], x["available_hours"]), reverse=True)

    eligible_candidates = [c for c in candidates if c["eligible"]]

    # Decision Logic: Prefer employees with required skills and available capacity; escalate if no suitable employee exists
    if eligible_candidates:
        selected = eligible_candidates[0]
        escalation_required = False
        decision_reasoning = (
            f"Selected {selected['name']} ({selected['role']}) who matches required skills "
            f"({', '.join(selected['matched_skills'])}) and has {selected['available_hours']}h available capacity "
            f"(task requires {estimated_hours}h)."
        )
    else:
        selected = None
        escalation_required = True
        decision_reasoning = (
            f"ESCALATION: No available employee possesses the required skills ({', '.join(required_skills)}) "
            f"with sufficient bandwidth ({estimated_hours}h needed). Escalating task to Engineering Manager for rebalancing."
        )

    return {
        "task_summary": task_description,
        "priority": priority,
        "deadline": deadline,
        "required_skills": required_skills,
        "estimated_hours": estimated_hours,
        "escalation_required": escalation_required,
        "recommended_employee": selected["name"] if selected else "NONE (ESCALATED)",
        "selected_candidate_details": selected,
        "decision_reasoning": decision_reasoning,
        "all_ranked_candidates": candidates
    }
