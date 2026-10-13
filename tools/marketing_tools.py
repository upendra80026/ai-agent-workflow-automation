from typing import Dict, Any, List, Optional
from core.tool_registry import register_tool
from core.llm_client import llm_client


@register_tool(name="campaign_input_validator", description="Validates campaign parameters and enforces presence of campaign goal and dates", category="marketing")
def validate_campaign_requirements(params: Dict[str, Any]) -> Dict[str, Any]:
    goal = params.get("campaign_goal") or params.get("goal")
    dates = params.get("dates") or params.get("timeline") or params.get("start_date")

    missing = []
    # Decision Logic: If campaign goal or dates are missing, request them before generating the brief
    if not goal or not str(goal).strip():
        missing.append("Campaign Goal (e.g., 'Q4 Holiday sales push', 'Acquire 5,000 new users')")
    if not dates or not str(dates).strip():
        missing.append("Campaign Dates/Timeline (e.g., 'Nov 15 - Dec 31, 2026')")

    if missing:
        return {
            "valid": False,
            "status": "MISSING_REQUIRED_INPUTS",
            "missing_fields": missing,
            "decision_action": "Request missing fields from user before brief generation",
            "message": f"Cannot generate complete campaign brief. Missing required inputs: {', '.join(missing)}. Please provide these details."
        }

    return {
        "valid": True,
        "status": "VALID",
        "missing_fields": [],
        "decision_action": "Proceed with brief synthesis"
    }


@register_tool(name="campaign_brief_generator", description="Generates structured marketing campaign brief with objectives, channels, and launch checklist", category="marketing")
def generate_campaign_brief(params: Dict[str, Any]) -> Dict[str, Any]:
    validation = validate_campaign_requirements(params)
    if not validation["valid"]:
        return {
            "brief_generated": False,
            "validation_report": validation,
            "content": validation["message"]
        }

    goal = params.get("campaign_goal") or params.get("goal", "Q4 E-Commerce Launch")
    dates = params.get("dates", "Q4 2026")
    products = params.get("product_list") or ["Ergonomic Mesh Chair", "Standing Desk", "RGB Mechanical Keyboard"]
    audience = params.get("target_audience", "Remote professionals, developers, and tech creators aged 22-45")
    promotion = params.get("promotion", "15% Bundle Discount with free expedited shipping")

    system_prompt = (
        "You are a Chief Marketing Officer. Produce a structured, executive-ready Marketing Campaign Brief. "
        "Include: 1. Executive Summary & Objective, 2. Target Audience & Personas, 3. Core Messaging Pillars, "
        "4. Channel Mix (Social, Search, Influencers, Email), 5. Timeline & Milestones, 6. Launch Checklist."
    )

    user_prompt = (
        f"Goal: {goal}\n"
        f"Dates: {dates}\n"
        f"Featured Products: {', '.join(products) if isinstance(products, list) else products}\n"
        f"Target Audience: {audience}\n"
        f"Promotion: {promotion}\n"
    )

    brief_content = llm_client.generate_completion(system_prompt, user_prompt)

    return {
        "brief_generated": True,
        "campaign_goal": goal,
        "timeline": dates,
        "products": products,
        "target_audience": audience,
        "promotion": promotion,
        "brief_content": brief_content,
        "checklist": [
            "[ ] Creative asset signoff (Hero banners, video cuts, ad copy)",
            "[ ] Landing page conversion tracking and pixel QA",
            "[ ] Influencer seeding product dispatch",
            "[ ] Email automation flow activation",
            "[ ] Live dashboard KPI review"
        ]
    }
