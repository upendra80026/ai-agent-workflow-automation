import csv
import os
from typing import List, Dict, Any
from core.tool_registry import register_tool
from core.llm_client import llm_client


@register_tool(name="keyword_csv_reader", description="Loads keyword list from CSV and deduplicates terms", category="seo")
def load_and_deduplicate_keywords(filepath: str = "data/keywords.csv") -> List[Dict[str, Any]]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Keywords file missing: {filepath}")

    seen = set()
    unique_keywords = []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kw = row.get("keyword", "").strip().lower()
            if kw and kw not in seen:
                seen.add(kw)
                unique_keywords.append({
                    "keyword": row.get("keyword", "").strip(),
                    "search_volume": int(row.get("search_volume", 1000)),
                    "cpc": float(row.get("cpc", 0.5)),
                    "competition": float(row.get("competition", 0.5))
                })
    return unique_keywords


@register_tool(name="seo_intent_classifier", description="Classifies search intent (Informational, Commercial, Transactional, Navigational) and maps to categories and target pages", category="seo")
def classify_and_map_keywords(filepath: str = "data/keywords.csv") -> Dict[str, Any]:
    keywords = load_and_deduplicate_keywords(filepath)
    results = []

    for item in keywords:
        kw = item["keyword"]
        vol = item["search_volume"]
        cpc = item["cpc"]

        # Decision Logic: Classify each keyword as informational, commercial, transactional, or navigational
        intent = llm_client._classify_offline_keyword(kw)

        # Map to category & recommended landing page
        kw_lower = kw.lower()
        if "keyboard" in kw_lower:
            category = "Peripherals / Keyboards"
            page = "/collections/mechanical-keyboards" if intent in ["Transactional", "Commercial"] else "/blog/keyboard-guides"
        elif "monitor" in kw_lower or "panel" in kw_lower:
            category = "Displays & Monitors"
            page = "/collections/4k-monitors" if intent in ["Transactional", "Commercial"] else "/blog/monitor-buying-guide"
        elif "chair" in kw_lower or "desk" in kw_lower:
            category = "Ergonomic Office Furniture"
            page = "/collections/ergonomic-desks-chairs" if intent in ["Transactional", "Commercial"] else "/guides/ergonomics-workspace"
        elif "mouse" in kw_lower or "mice" in kw_lower:
            category = "Peripherals / Mice"
            page = "/collections/wireless-mice"
        else:
            category = "Electronics & Tech Accessories"
            page = "/shop/accessories"

        # Priority calculation based on commercial value and search volume
        if intent in ["Transactional", "Commercial"] and vol >= 15000:
            priority = "HIGH"
        elif intent in ["Transactional", "Commercial"] or vol >= 20000:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        results.append({
            "keyword": kw,
            "search_volume": vol,
            "cpc": f"${cpc:.2f}",
            "intent": intent,
            "category": category,
            "priority": priority,
            "recommended_target_page": page
        })

    # Summary by intent
    intent_counts = {}
    for r in results:
        intent_counts[r["intent"]] = intent_counts.get(r["intent"], 0) + 1

    return {
        "total_keywords_processed": len(results),
        "intent_distribution": intent_counts,
        "high_priority_count": sum(1 for r in results if r["priority"] == "HIGH"),
        "classified_keywords": results
    }
