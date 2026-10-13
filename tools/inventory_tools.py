import csv
import os
from typing import List, Dict, Any, Optional
from core.tool_registry import register_tool


@register_tool(name="csv_inventory_reader", description="Reads inventory stock levels from CSV file", category="inventory")
def load_inventory_csv(filepath: str = "data/inventory.csv") -> List[Dict[str, Any]]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Inventory file not found: {filepath}")
    items = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append({
                "product_id": row.get("product_id", "").strip(),
                "sku": row.get("sku", "").strip(),
                "name": row.get("name", "").strip(),
                "category": row.get("category", "").strip(),
                "current_stock": int(row.get("current_stock", 0)),
                "minimum_stock": int(row.get("minimum_stock", 0)),
                "reorder_batch_size": int(row.get("reorder_batch_size", 10)),
                "unit_cost": float(row.get("unit_cost", 0.0))
            })
    return items


@register_tool(name="stock_threshold_evaluator", description="Compares current stock with minimum thresholds and calculates reorder batches", category="inventory")
def evaluate_inventory_restock(inventory_items: List[Dict[str, Any]], custom_threshold_multiplier: float = 1.0) -> Dict[str, Any]:
    restock_needed = []
    adequate_stock = []

    for item in inventory_items:
        threshold = int(item["minimum_stock"] * custom_threshold_multiplier)
        current = item["current_stock"]

        # Decision Logic: If current_stock < minimum_stock, mark product for restock
        if current < threshold:
            deficit = threshold - current
            # Calculate batch-aligned reorder quantity
            batch = item["reorder_batch_size"]
            suggested_reorder = max(batch, ((deficit + batch - 1) // batch) * batch)
            estimated_cost = round(suggested_reorder * item["unit_cost"], 2)

            restock_needed.append({
                "product_id": item["product_id"],
                "sku": item["sku"],
                "name": item["name"],
                "current_stock": current,
                "minimum_stock": threshold,
                "deficit": deficit,
                "suggested_reorder_qty": suggested_reorder,
                "unit_cost": item["unit_cost"],
                "estimated_cost": estimated_cost,
                "status": "CRITICAL_LOW" if current <= (threshold // 3) else "LOW_STOCK"
            })
        else:
            adequate_stock.append({
                "sku": item["sku"],
                "name": item["name"],
                "current_stock": current,
                "minimum_stock": threshold
            })

    total_cost = sum(x["estimated_cost"] for x in restock_needed)

    return {
        "total_products_checked": len(inventory_items),
        "products_needing_restock_count": len(restock_needed),
        "products_adequate_count": len(adequate_stock),
        "total_estimated_restock_cost": round(total_cost, 2),
        "restock_list": restock_needed,
        "adequate_list": adequate_stock
    }
