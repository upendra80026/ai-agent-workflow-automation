import csv
import os
from typing import List, Dict, Any
from core.tool_registry import register_tool


@register_tool(name="price_dataset_reader", description="Loads internal prices and vendor prices from CSV files", category="pricing")
def load_price_datasets(internal_path: str = "data/internal_prices.csv", vendor_path: str = "data/vendor_prices.csv") -> Dict[str, Any]:
    if not os.path.exists(internal_path):
        raise FileNotFoundError(f"Internal price file missing: {internal_path}")
    if not os.path.exists(vendor_path):
        raise FileNotFoundError(f"Vendor price file missing: {vendor_path}")

    internal_map = {}
    with open(internal_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sku = row["sku"].strip()
            internal_map[sku] = {
                "sku": sku,
                "product_name": row.get("product_name", "").strip(),
                "internal_price": float(row.get("internal_price", 0.0)),
                "currency": row.get("currency", "USD")
            }

    vendor_list = []
    with open(vendor_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vendor_list.append({
                "sku": row["sku"].strip(),
                "vendor_name": row.get("vendor_name", "").strip(),
                "vendor_price": float(row.get("vendor_price", 0.0)),
                "currency": row.get("currency", "USD")
            })

    return {
        "internal_prices": internal_map,
        "vendor_prices": vendor_list
    }


@register_tool(name="price_discrepancy_calculator", description="Compares internal and vendor prices and flags differences exceeding 10%", category="pricing")
def validate_product_prices(internal_prices: Dict[str, Dict[str, Any]], vendor_prices: List[Dict[str, Any]], threshold_pct: float = 10.0) -> Dict[str, Any]:
    matched = []
    exceptions = []
    unmatched_vendor = []

    for v_item in vendor_prices:
        sku = v_item["sku"]
        v_price = v_item["vendor_price"]

        if sku in internal_prices:
            int_item = internal_prices[sku]
            int_price = int_item["internal_price"]
            diff = round(v_price - int_price, 2)
            pct_diff = round((abs(diff) / int_price) * 100.0, 2) if int_price > 0 else 0.0

            record = {
                "sku": sku,
                "product_name": int_item["product_name"],
                "vendor_name": v_item["vendor_name"],
                "internal_price": int_price,
                "vendor_price": v_price,
                "difference": diff,
                "percentage_diff": pct_diff,
                "direction": "VENDOR_HIGHER" if diff > 0 else ("VENDOR_LOWER" if diff < 0 else "IDENTICAL")
            }

            matched.append(record)

            # Decision Logic: Flag when price difference exceeds 10%
            if pct_diff > threshold_pct:
                record["flag_reason"] = f"Price difference of {pct_diff}% exceeds {threshold_pct}% threshold"
                exceptions.append(record)
        else:
            unmatched_vendor.append({
                "sku": sku,
                "vendor_name": v_item["vendor_name"],
                "vendor_price": v_price,
                "flag_reason": "SKU exists in vendor list but missing in internal catalog"
            })
            exceptions.append(unmatched_vendor[-1])

    return {
        "total_vendor_records": len(vendor_prices),
        "total_matched": len(matched),
        "total_exceptions": len(exceptions),
        "threshold_percentage": threshold_pct,
        "matched_items": matched,
        "exceptions": exceptions
    }
