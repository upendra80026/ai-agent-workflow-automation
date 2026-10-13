import json
import os
import re
from typing import Dict, Any, Optional
from core.tool_registry import register_tool


@register_tool(name="order_database_api", description="Looks up order records by Order ID (ORD-XXXX) or customer email", category="order")
def lookup_order_record(identifier: str, orders_path: str = "data/orders.json") -> Optional[Dict[str, Any]]:
    if not os.path.exists(orders_path):
        raise FileNotFoundError(f"Orders database file missing: {orders_path}")

    with open(orders_path, "r", encoding="utf-8") as f:
        orders = json.load(f)

    clean_id = identifier.strip().upper()

    # Exact Order ID match
    if clean_id in orders:
        return orders[clean_id]

    # Email lookup match
    clean_lower = identifier.strip().lower()
    for order in orders.values():
        if order.get("customer_email", "").lower() == clean_lower:
            return order

    # Partial / regex match for ORD-\d+
    match = re.search(r"ORD-\d+", clean_id)
    if match and match.group(0) in orders:
        return orders[match.group(0)]

    return None


@register_tool(name="shipment_tracking_api", description="Retrieves live shipment routing, carrier, and transit status", category="order")
def lookup_shipment_details(tracking_id: Optional[str], shipments_path: str = "data/shipments.json") -> Optional[Dict[str, Any]]:
    if not tracking_id or not os.path.exists(shipments_path):
        return None

    with open(shipments_path, "r", encoding="utf-8") as f:
        shipments = json.load(f)

    return shipments.get(tracking_id.strip())


@register_tool(name="order_status_synthesizer", description="Validates identifier, queries order & shipment APIs, and handles not-found condition", category="order")
def query_customer_order_status(identifier: str) -> Dict[str, Any]:
    cleaned = identifier.strip()

    # Decision Logic: If no order is found, ask for another identifier
    if not cleaned:
        return {
            "found": False,
            "status": "ERROR_MISSING_IDENTIFIER",
            "message": "No Order ID or customer email was provided. Please provide an Order ID (e.g. ORD-1001) or customer email address."
        }

    order = lookup_order_record(cleaned)

    if not order:
        return {
            "found": False,
            "status": "ORDER_NOT_FOUND",
            "query_used": cleaned,
            "message": f"No order records found for identifier '{cleaned}'. Please check the order number or provide the customer's registered email address."
        }

    tracking_id = order.get("shipment_tracking_id")
    shipment_info = lookup_shipment_details(tracking_id) if tracking_id else None

    return {
        "found": True,
        "status": order.get("status", "Unknown"),
        "order_id": order.get("order_id"),
        "customer_name": order.get("customer_name"),
        "customer_email": order.get("customer_email"),
        "order_date": order.get("order_date"),
        "total_amount": f"${order.get('total_amount', 0.0):.2f}",
        "items": order.get("items", []),
        "shipping_address": order.get("shipping_address"),
        "tracking_id": tracking_id,
        "carrier": shipment_info.get("carrier") if shipment_info else ("Pending Carrier" if not tracking_id else "Standard Shipping"),
        "shipment_status": shipment_info.get("shipment_status") if shipment_info else "Awaiting Carrier Pickup",
        "estimated_delivery": shipment_info.get("estimated_delivery") if shipment_info else ("1-2 Business Days" if order.get("status") == "Processing" else "Delivered"),
        "transit_history": shipment_info.get("history", []) if shipment_info else []
    }
