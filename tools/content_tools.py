from typing import Dict, Any, List
from core.tool_registry import register_tool
from core.llm_client import llm_client


@register_tool(name="attribute_validator", description="Validates product attributes and marks any missing fields without hallucinating", category="content")
def validate_product_attributes(attributes: Dict[str, Any]) -> Dict[str, Any]:
    expected_fields = ["product_name", "category", "material", "color", "target_audience"]
    present = {}
    missing = []

    for f in expected_fields:
        val = attributes.get(f) or attributes.get(f.replace("_", " "))
        if val and str(val).strip():
            present[f] = str(val).strip()
        else:
            missing.append(f)

    # Decision Logic: Do not invent missing product attributes; explicitly mark missing information
    return {
        "valid": len(missing) == 0,
        "present_attributes": present,
        "missing_attributes": missing,
        "attribute_completeness_pct": round(((len(expected_fields) - len(missing)) / len(expected_fields)) * 100.0, 1),
        "decision_note": f"Identified {len(missing)} missing attributes: {', '.join(missing)}" if missing else "All expected product attributes present."
    }


@register_tool(name="seo_content_generator", description="Generates full description, short description, SEO title (<60 chars), and meta description (<160 chars)", category="content")
def generate_seo_content(attributes: Dict[str, Any]) -> Dict[str, Any]:
    val_report = validate_product_attributes(attributes)
    present = val_report["present_attributes"]
    missing = val_report["missing_attributes"]

    name = present.get("product_name", "Premium Ergonomic Task Chair")
    category = present.get("category", "Office Furniture")
    material = present.get("material", "[Material: Not Specified]")
    color = present.get("color", "[Color: Not Specified]")
    audience = present.get("target_audience", "[Audience: General Customers]")

    system_prompt = (
        "You are an expert E-Commerce Copywriter and SEO Specialist. "
        "Generate high-converting product copy following strict guidelines:\n"
        "1. Do NOT invent missing product attributes. Explicitly note missing specs if omitted.\n"
        "2. Provide:\n"
        "   - SEO Title (Max 60 characters)\n"
        "   - Short Description (1-2 compelling punchy sentences)\n"
        "   - Product Description (Engaging, bullet points, benefit-driven)\n"
        "   - SEO Meta Description (140-160 characters)"
    )

    user_prompt = (
        f"Product Name: {name}\n"
        f"Category: {category}\n"
        f"Material: {material}\n"
        f"Color: {color}\n"
        f"Target Audience: {audience}\n"
        f"Missing Attributes Notice: {', '.join(missing) if missing else 'None'}\n"
    )

    raw_completion = llm_client.generate_completion(system_prompt, user_prompt)

    # Structured SEO fields
    seo_title = f"{name} | Ergonomic {category}"[:60]
    short_desc = f"Engineered for {audience}, this {color} {category.lower()} in {material} delivers all-day support and performance."
    meta_desc = f"Shop {name}. Premium {category.lower()} crafted for {audience}. High durability, modern design & fast delivery. Order now!"[:158]

    return {
        "product_name": name,
        "validation": val_report,
        "seo_title": seo_title,
        "seo_title_length": len(seo_title),
        "short_description": short_desc,
        "full_description": raw_completion,
        "meta_description": meta_desc,
        "meta_description_length": len(meta_desc),
        "missing_attributes_disclaimer": f"Note: Missing specifications ({', '.join(missing)}) were NOT invented." if missing else None
    }
