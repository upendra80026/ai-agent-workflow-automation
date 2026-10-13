import json
import os
import re
from typing import List, Dict, Any
from core.tool_registry import register_tool

try:
    from rapidfuzz import fuzz
except ImportError:
    # Lightweight fallback Levenshtein/Jaccard similarity
    class FuzzFallback:
        @staticmethod
        def token_set_ratio(s1: str, s2: str) -> float:
            w1 = set(s1.lower().split())
            w2 = set(s2.lower().split())
            if not w1 or not w2:
                return 0.0
            intersection = w1.intersection(w2)
            union = w1.union(w2)
            return round((len(intersection) / len(union)) * 100.0, 1)
    fuzz = FuzzFallback()


def normalize_sku(sku: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", sku).upper()


def normalize_text(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    return " ".join(cleaned.split())


@register_tool(name="product_catalog_reader", description="Loads product catalog JSON or CSV data", category="deduplication")
def load_catalog(filepath: str = "data/product_catalog.json") -> List[Dict[str, Any]]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Catalog file missing: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


@register_tool(name="duplicate_detection_engine", description="Detects exact SKU matches (Definite) and high attribute similarity (Possible) duplicates with confidence scores", category="deduplication")
def detect_duplicate_products(catalog_path: str = "data/product_catalog.json", similarity_threshold: float = 75.0) -> Dict[str, Any]:
    catalog = load_catalog(catalog_path)
    duplicate_groups = []
    seen_pairs = set()

    n = len(catalog)
    for i in range(n):
        for j in range(i + 1, n):
            p1 = catalog[i]
            p2 = catalog[j]
            pair_key = tuple(sorted([p1["id"], p2["id"]]))
            if pair_key in seen_pairs:
                continue

            sku1_norm = normalize_sku(p1.get("sku", ""))
            sku2_norm = normalize_sku(p2.get("sku", ""))
            name1_norm = normalize_text(p1.get("name", ""))
            name2_norm = normalize_text(p2.get("name", ""))

            name_sim = fuzz.token_set_ratio(name1_norm, name2_norm)
            desc_sim = fuzz.token_set_ratio(
                normalize_text(p1.get("description", "")),
                normalize_text(p2.get("description", ""))
            )
            brand_match = (p1.get("brand", "").lower() == p2.get("brand", "").lower()) and bool(p1.get("brand"))

            # Decision Logic: Exact SKU match is a definite duplicate; high attribute similarity is a possible duplicate
            is_exact_sku = (sku1_norm == sku2_norm) and bool(sku1_norm)

            if is_exact_sku:
                seen_pairs.add(pair_key)
                duplicate_groups.append({
                    "group_id": f"DUP-EXACT-{len(duplicate_groups) + 1}",
                    "confidence_pct": 100.0,
                    "duplicate_type": "Definite Duplicate (Exact SKU Match)",
                    "matching_fields": ["SKU", "Brand" if brand_match else ""],
                    "matched_sku": p1.get("sku"),
                    "products": [
                        {"id": p1["id"], "name": p1["name"], "price": p1.get("price")},
                        {"id": p2["id"], "name": p2["name"], "price": p2.get("price")}
                    ],
                    "recommendation": "Merge product records or delete redundant entry."
                })
            elif name_sim >= similarity_threshold and brand_match:
                overall_confidence = round((name_sim * 0.7) + (desc_sim * 0.3), 1)
                seen_pairs.add(pair_key)
                duplicate_groups.append({
                    "group_id": f"DUP-POSSIBLE-{len(duplicate_groups) + 1}",
                    "confidence_pct": overall_confidence,
                    "duplicate_type": "Possible Duplicate (High Attribute Similarity)",
                    "matching_fields": [f"Name Similarity ({name_sim}%)", f"Description Similarity ({desc_sim}%)", "Brand Match"],
                    "products": [
                        {"id": p1["id"], "sku": p1.get("sku"), "name": p1["name"], "price": p1.get("price")},
                        {"id": p2["id"], "sku": p2.get("sku"), "name": p2["name"], "price": p2.get("price")}
                    ],
                    "recommendation": "Review for canonical variant consolidation."
                })

    return {
        "catalog_size": len(catalog),
        "total_duplicate_groups": len(duplicate_groups),
        "definite_duplicates_count": sum(1 for g in duplicate_groups if "Definite" in g["duplicate_type"]),
        "possible_duplicates_count": sum(1 for g in duplicate_groups if "Possible" in g["duplicate_type"]),
        "duplicate_groups": duplicate_groups
    }
