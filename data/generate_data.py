import csv
import json
import os
import random
import openpyxl

os.makedirs('data', exist_ok=True)

# 1. WF001: inventory.csv
inventory_rows = [
    {"product_id": "PRD-001", "sku": "SKU-CHAIR-01", "name": "Ergonomic Mesh Office Chair", "category": "Furniture", "current_stock": 4, "minimum_stock": 15, "reorder_batch_size": 20, "unit_cost": 120.00},
    {"product_id": "PRD-002", "sku": "SKU-KB-01", "name": "Wireless Mechanical Keyboard (RGB)", "category": "Peripherals", "current_stock": 2, "minimum_stock": 20, "reorder_batch_size": 30, "unit_cost": 45.00},
    {"product_id": "PRD-003", "sku": "SKU-HUB-01", "name": "USB-C 8-in-1 Multiport Hub", "category": "Accessories", "current_stock": 8, "minimum_stock": 25, "reorder_batch_size": 40, "unit_cost": 22.50},
    {"product_id": "PRD-004", "sku": "SKU-MON-01", "name": "27-inch 4K UHD IPS Monitor", "category": "Displays", "current_stock": 35, "minimum_stock": 10, "reorder_batch_size": 15, "unit_cost": 210.00},
    {"product_id": "PRD-005", "sku": "SKU-MOU-01", "name": "Precision Ergonomic Wireless Mouse", "category": "Peripherals", "current_stock": 50, "minimum_stock": 15, "reorder_batch_size": 25, "unit_cost": 28.00},
    {"product_id": "PRD-006", "sku": "SKU-DESK-01", "name": "Motorized Standing Desk Frame", "category": "Furniture", "current_stock": 3, "minimum_stock": 10, "reorder_batch_size": 10, "unit_cost": 240.00},
    {"product_id": "PRD-007", "sku": "SKU-HEAD-01", "name": "Active Noise-Cancelling Headphones", "category": "Audio", "current_stock": 18, "minimum_stock": 12, "reorder_batch_size": 20, "unit_cost": 85.00},
    {"product_id": "PRD-008", "sku": "SKU-LAMP-01", "name": "LED Monitor Light Bar with Remote", "category": "Lighting", "current_stock": 5, "minimum_stock": 18, "reorder_batch_size": 25, "unit_cost": 32.00},
]
with open('data/inventory.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(inventory_rows[0].keys()))
    writer.writeheader()
    writer.writerows(inventory_rows)

# 2. WF002: internal_prices.csv and vendor_prices.csv
internal_prices = [
    {"sku": "SKU-CHAIR-01", "product_name": "Ergonomic Mesh Office Chair", "internal_price": 189.99, "currency": "USD"},
    {"sku": "SKU-KB-01", "product_name": "Wireless Mechanical Keyboard (RGB)", "internal_price": 79.99, "currency": "USD"},
    {"sku": "SKU-HUB-01", "product_name": "USB-C 8-in-1 Multiport Hub", "internal_price": 49.99, "currency": "USD"},
    {"sku": "SKU-MON-01", "product_name": "27-inch 4K UHD IPS Monitor", "internal_price": 349.99, "currency": "USD"},
    {"sku": "SKU-MOU-01", "product_name": "Precision Ergonomic Wireless Mouse", "internal_price": 49.99, "currency": "USD"},
    {"sku": "SKU-DESK-01", "product_name": "Motorized Standing Desk Frame", "internal_price": 399.99, "currency": "USD"},
    {"sku": "SKU-HEAD-01", "product_name": "Active Noise-Cancelling Headphones", "internal_price": 149.99, "currency": "USD"},
    {"sku": "SKU-LAMP-01", "product_name": "LED Monitor Light Bar with Remote", "internal_price": 59.99, "currency": "USD"},
]
vendor_prices = [
    {"sku": "SKU-CHAIR-01", "vendor_name": "Apex Furnishings", "vendor_price": 192.00, "currency": "USD"},  # 1.0% diff -> OK
    {"sku": "SKU-KB-01", "vendor_name": "KeyTech Global", "vendor_price": 65.00, "currency": "USD"},     # 18.7% diff -> EXCEPTION (>10%)
    {"sku": "SKU-HUB-01", "vendor_name": "ConnectPlus Electronics", "vendor_price": 42.00, "currency": "USD"}, # 16.0% diff -> EXCEPTION (>10%)
    {"sku": "SKU-MON-01", "vendor_name": "Apex Displays", "vendor_price": 345.00, "currency": "USD"},   # 1.4% diff -> OK
    {"sku": "SKU-MOU-01", "vendor_name": "KeyTech Global", "vendor_price": 48.50, "currency": "USD"},    # 3.0% diff -> OK
    {"sku": "SKU-DESK-01", "vendor_name": "Apex Furnishings", "vendor_price": 310.00, "currency": "USD"}, # 22.5% diff -> EXCEPTION (>10%)
    {"sku": "SKU-HEAD-01", "vendor_name": "SoundWave Inc", "vendor_price": 148.00, "currency": "USD"},   # 1.3% diff -> OK
    {"sku": "SKU-LAMP-01", "vendor_name": "LumiGear Ltd", "vendor_price": 75.00, "currency": "USD"},     # 25.0% diff -> EXCEPTION (>10%)
    {"sku": "SKU-VEND-ONLY", "vendor_name": "NewTech", "vendor_price": 99.00, "currency": "USD"}          # Unmatched SKU -> EXCEPTION
]
with open('data/internal_prices.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(internal_prices[0].keys()))
    writer.writeheader()
    writer.writerows(internal_prices)

with open('data/vendor_prices.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(vendor_prices[0].keys()))
    writer.writeheader()
    writer.writerows(vendor_prices)

# 3. WF003: vendor_products_dirty.xlsx and vendor_products_dirty.csv
vendor_dirty_rows = [
    {"vendor_sku": "VND-101", "product_name": "Anodized Aluminum Laptop Stand", "category": "Accessories", "wholesale_price": 28.50, "stock_qty": 140, "lead_time_days": 5},
    {"vendor_sku": "VND-102", "product_name": "Braided Thunderbolt 4 Cable 2m", "category": "Cables", "wholesale_price": 19.99, "stock_qty": 350, "lead_time_days": 3},
    {"vendor_sku": "", "product_name": "Missing SKU Headphone Stand", "category": "Accessories", "wholesale_price": 14.00, "stock_qty": 80, "lead_time_days": 7}, # Invalid: Missing SKU
    {"vendor_sku": "VND-104", "product_name": "Ultra-Wide Gaming Mouse Pad", "category": "Accessories", "wholesale_price": 11.20, "stock_qty": 210, "lead_time_days": 4},
    {"vendor_sku": "VND-105", "product_name": "", "category": "Power", "wholesale_price": 34.00, "stock_qty": 65, "lead_time_days": 6}, # Invalid: Missing Name
    {"vendor_sku": "VND-106", "product_name": "Magnetic Wireless MagSafe Charger", "category": "Charging", "wholesale_price": 22.00, "stock_qty": 180, "lead_time_days": 5},
    {"vendor_sku": "VND-107", "product_name": "Under-Desk Cable Management Tray", "category": "Organization", "wholesale_price": -5.00, "stock_qty": 90, "lead_time_days": 3}, # Invalid: Negative Price
    {"vendor_sku": None, "product_name": "Another Null SKU Item", "category": "Peripherals", "wholesale_price": 45.00, "stock_qty": 20, "lead_time_days": 10}, # Invalid: Missing SKU
    {"vendor_sku": "VND-109", "product_name": "Noise Isolating Foam Ear Tips (3-Pack)", "category": "Audio", "wholesale_price": 6.50, "stock_qty": 500, "lead_time_days": 2},
    {"vendor_sku": "VND-110", "product_name": None, "category": "Displays", "wholesale_price": 89.00, "stock_qty": 30, "lead_time_days": 8}, # Invalid: Missing Name
    {"vendor_sku": "VND-111", "product_name": "Dual Monitor Desk Mount Arm", "category": "Furniture", "wholesale_price": 64.00, "stock_qty": 45, "lead_time_days": 5},
]
with open('data/vendor_products_dirty.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(vendor_dirty_rows[0].keys()))
    writer.writeheader()
    writer.writerows(vendor_dirty_rows)

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Vendor_Products"
ws.append(list(vendor_dirty_rows[0].keys()))
for r in vendor_dirty_rows:
    ws.append(list(r.values()))
wb.save('data/vendor_products_dirty.xlsx')

# 4. WF005: orders.json & shipments.json
orders_data = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "customer_email": "sarah.connor@example.com",
        "customer_name": "Sarah Connor",
        "order_date": "2026-10-10",
        "status": "In Transit",
        "currency": "USD",
        "total_amount": 289.98,
        "items": [
            {"sku": "SKU-KB-01", "name": "Wireless Mechanical Keyboard (RGB)", "quantity": 1, "unit_price": 79.99},
            {"sku": "SKU-MON-01", "name": "27-inch 4K UHD IPS Monitor", "quantity": 1, "unit_price": 209.99}
        ],
        "shipping_address": "104 Cyberdyne Way, Los Angeles, CA 90001",
        "shipment_tracking_id": "TRK-FEDEX-99214"
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "customer_email": "tony.stark@example.com",
        "customer_name": "Tony Stark",
        "order_date": "2026-10-06",
        "status": "Delivered",
        "currency": "USD",
        "total_amount": 399.99,
        "items": [
            {"sku": "SKU-DESK-01", "name": "Motorized Standing Desk Frame", "quantity": 1, "unit_price": 399.99}
        ],
        "shipping_address": "10880 Malibu Point, Malibu, CA 90265",
        "shipment_tracking_id": "TRK-UPS-88123"
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "customer_email": "peter.parker@example.com",
        "customer_name": "Peter Parker",
        "order_date": "2026-10-13",
        "status": "Processing",
        "currency": "USD",
        "total_amount": 49.99,
        "items": [
            {"sku": "SKU-HUB-01", "name": "USB-C 8-in-1 Multiport Hub", "quantity": 1, "unit_price": 49.99}
        ],
        "shipping_address": "20 Ingram St, Forest Hills, NY 11375",
        "shipment_tracking_id": None
    }
}
shipments_data = {
    "TRK-FEDEX-99214": {
        "tracking_id": "TRK-FEDEX-99214",
        "carrier": "FedEx Express",
        "service_level": "2-Day Priority",
        "shipment_status": "Out for Delivery",
        "origin": "Memphis, TN Hub",
        "destination": "Los Angeles, CA",
        "estimated_delivery": "2026-10-14 by 4:30 PM",
        "history": [
            {"timestamp": "2026-10-11 08:30:00", "location": "Memphis, TN", "status": "Package picked up"},
            {"timestamp": "2026-10-12 14:15:00", "location": "Fort Worth, TX", "status": "In transit through regional sort facility"},
            {"timestamp": "2026-10-13 06:45:00", "location": "Los Angeles, CA", "status": "Arrived at local distribution center"},
            {"timestamp": "2026-10-13 08:00:00", "location": "Los Angeles, CA", "status": "On FedEx vehicle for delivery"}
        ]
    },
    "TRK-UPS-88123": {
        "tracking_id": "TRK-UPS-88123",
        "carrier": "UPS Ground",
        "service_level": "Ground",
        "shipment_status": "Delivered",
        "origin": "Louisville, KY Hub",
        "destination": "Malibu, CA",
        "delivered_at": "2026-10-09 11:42:00",
        "signed_by": "J.A.R.V.I.S.",
        "history": [
            {"timestamp": "2026-10-07 10:00:00", "location": "Louisville, KY", "status": "Shipped"},
            {"timestamp": "2026-10-09 11:42:00", "location": "Malibu, CA", "status": "Delivered at front porch"}
        ]
    }
}
with open('data/orders.json', 'w', encoding='utf-8') as f:
    json.dump(orders_data, f, indent=2)
with open('data/shipments.json', 'w', encoding='utf-8') as f:
    json.dump(shipments_data, f, indent=2)

# 5. WF006: product_catalog.json
product_catalog = [
    {
        "id": "PROD-101",
        "sku": "SKU-AUDIO-XM5-BLK",
        "name": "Sony WH-1000XM5 Wireless Noise-Canceling Headphones - Black",
        "category": "Headphones",
        "brand": "Sony",
        "price": 398.00,
        "description": "Premium wireless over-ear headphones with industry-leading noise cancelation, 30-hour battery life, and crystal clear hands-free calling."
    },
    {
        "id": "PROD-102",
        "sku": "SKU-AUDIO-XM5-BLK",  # Exact SKU duplicate!
        "name": "Sony WH-1000XM5 Wireless Headphones (Black)",
        "category": "Headphones",
        "brand": "Sony",
        "price": 399.99,
        "description": "Sony WH-1000XM5 over ear noise cancelling bluetooth headphones black."
    },
    {
        "id": "PROD-103",
        "sku": "SKU-AUDIO-XM5-SLV",
        "name": "Sony WH-1000XM5 Wireless Noise-Canceling Headphones - Silver",
        "category": "Headphones",
        "brand": "Sony",
        "price": 398.00,
        "description": "Premium wireless over-ear headphones in elegant silver finish with dual processor noise canceling."
    },
    {
        "id": "PROD-104",
        "sku": "SKU-LOGI-MXM3S",
        "name": "Logitech MX Master 3S Performance Wireless Mouse",
        "category": "Mice",
        "brand": "Logitech",
        "price": 99.99,
        "description": "Quiet click wireless ergonomic mouse with 8K DPI sensor for Mac and Windows."
    },
    {
        "id": "PROD-105",
        "sku": "SKU-LOGI-MXM3S-GRY",
        "name": "Logitech MX Master 3S Wireless Mouse - Pale Grey",  # Near duplicate of MX Master 3S
        "category": "Mice",
        "brand": "Logitech",
        "price": 99.99,
        "description": "Logitech MX Master 3S quiet clicks ergonomic bluetooth wireless mouse pale grey 8000 DPI."
    },
    {
        "id": "PROD-106",
        "sku": "SKU-APPL-MBP16-M3",
        "name": "Apple MacBook Pro 16-inch M3 Max (36GB RAM, 1TB SSD) Space Black",
        "category": "Laptops",
        "brand": "Apple",
        "price": 3499.00,
        "description": "Liquid Retina XDR display, M3 Max chip with 14-core CPU and 30-core GPU."
    },
    {
        "id": "PROD-107",
        "sku": "SKU-APPL-MBP-16M3MAX",  # Near duplicate of MacBook Pro
        "name": "Apple 16-Inch MacBook Pro M3 Max 36GB / 1TB SSD Space Black",
        "category": "Laptops",
        "brand": "Apple",
        "price": 3499.00,
        "description": "Apple 16\" MacBook Pro notebook with Apple M3 Max processor, 36GB unified memory, 1TB solid state drive."
    },
    {
        "id": "PROD-108",
        "sku": "SKU-CHAIR-HERMAN",
        "name": "Herman Miller Aeron Ergonomic Chair - Size B Carbon",
        "category": "Chairs",
        "brand": "Herman Miller",
        "price": 1495.00,
        "description": "Ergonomic icon with PostureFit SL back support, breathable pellicle mesh, and fully adjustable arms."
    }
]
with open('data/product_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(product_catalog, f, indent=2)

# 6. WF008: keywords.csv
keywords_data = [
    {"keyword": "how to clean mechanical keyboard switches", "search_volume": 12500, "cpc": 0.45, "competition": 0.22},
    {"keyword": "buy wireless mechanical keyboard rgb", "search_volume": 28400, "cpc": 2.80, "competition": 0.78},
    {"keyword": "best budget 4k monitors 2026", "search_volume": 45000, "cpc": 1.95, "competition": 0.65},
    {"keyword": "difference between ips and va panel", "search_volume": 18200, "cpc": 0.35, "competition": 0.18},
    {"keyword": "order ergonomic office chair with lumbar support", "search_volume": 16500, "cpc": 3.40, "competition": 0.82},
    {"keyword": "logitech official driver download support", "search_volume": 95000, "cpc": 0.10, "competition": 0.05},
    {"keyword": "usb-c multiport hub deals discount code", "search_volume": 14200, "cpc": 2.10, "competition": 0.71},
    {"keyword": "standing desk height calculator for ergonomics", "search_volume": 22100, "cpc": 0.50, "competition": 0.25},
    {"keyword": "sony headphones warranty claim portal", "search_volume": 19000, "cpc": 0.15, "competition": 0.08},
    {"keyword": "top rated wireless mice for programmers comparison", "search_volume": 11000, "cpc": 1.75, "competition": 0.55},
]
with open('data/keywords.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(keywords_data[0].keys()))
    writer.writeheader()
    writer.writerows(keywords_data)

# 7. WF009: employees.json
employees_data = [
    {
        "id": "EMP-001",
        "name": "Aarav Sharma",
        "role": "Senior Fullstack Developer",
        "skills": ["Python", "FastAPI", "React", "Docker", "PostgreSQL", "LangChain"],
        "current_workload_hours": 26,
        "max_capacity_hours": 40,
        "available_hours": 14,
        "status": "Available"
    },
    {
        "id": "EMP-002",
        "name": "Priya Patel",
        "role": "Lead AI Engineer",
        "skills": ["Python", "LLM", "LangChain", "LangGraph", "PyTorch", "NLP", "Prompt Engineering"],
        "current_workload_hours": 32,
        "max_capacity_hours": 40,
        "available_hours": 8,
        "status": "Available"
    },
    {
        "id": "EMP-003",
        "name": "Vikram Malhotra",
        "role": "Backend Architect",
        "skills": ["Python", "Go", "Kubernetes", "Microservices", "Kafka", "Redis"],
        "current_workload_hours": 39,
        "max_capacity_hours": 40,
        "available_hours": 1,
        "status": "Near Capacity"
    },
    {
        "id": "EMP-004",
        "name": "Ananya Roy",
        "role": "Frontend Specialist",
        "skills": ["React", "Next.js", "TypeScript", "TailwindCSS", "UI/UX", "State Management"],
        "current_workload_hours": 20,
        "max_capacity_hours": 40,
        "available_hours": 20,
        "status": "Available"
    },
    {
        "id": "EMP-005",
        "name": "Rohan Deshmukh",
        "role": "DevOps & Cloud Engineer",
        "skills": ["AWS", "Terraform", "CI/CD", "Docker", "Linux", "Security"],
        "current_workload_hours": 40,
        "max_capacity_hours": 40,
        "available_hours": 0,
        "status": "Fully Booked"
    }
]
with open('data/employees.json', 'w', encoding='utf-8') as f:
    json.dump(employees_data, f, indent=2)

# 8. WF010: workflow_logs.csv
random.seed(42)
workflow_names = {
    "WF001": "Inventory Restock Check",
    "WF002": "Product Price Validation",
    "WF003": "Vendor File Processing",
    "WF004": "Product Description Generator",
    "WF005": "Customer Order Status",
    "WF006": "Duplicate Product Detection",
    "WF007": "Marketing Campaign Brief",
    "WF008": "SEO Keyword Classification",
    "WF009": "Employee Task Assignment",
    "WF010": "Workflow Performance Report"
}

log_rows = []
for i in range(1, 151):
    wf_id = f"WF{random.randint(1, 10):03d}"
    wf_name = workflow_names[wf_id]
    
    # Specific realistic anomalies to trigger decision logic:
    # WF003 has higher failure rate (corrupt files ~18%)
    # WF004 has higher execution time (LLM latency ~3600ms)
    # WF005 has occasional lookup timeouts (~12% failure)
    if wf_id == "WF003":
        status = "FAILED" if random.random() < 0.18 else "SUCCESS"
        exec_time = random.randint(650, 1800)
        error = "FileValidationError: Missing SKU header or malformed CSV rows" if status == "FAILED" else ""
    elif wf_id == "WF004":
        status = "FAILED" if random.random() < 0.04 else "SUCCESS"
        exec_time = random.randint(2800, 4900)  # Average > 3000ms threshold!
        error = "LLMRateLimitError: API token quota throttle" if status == "FAILED" else ""
    elif wf_id == "WF005":
        status = "FAILED" if random.random() < 0.14 else "SUCCESS"  # Failure rate > 10%!
        exec_time = random.randint(400, 1200)
        error = "OrderLookupError: Upstream Carrier API timeout" if status == "FAILED" else ""
    else:
        status = "FAILED" if random.random() < 0.03 else "SUCCESS"
        exec_time = random.randint(300, 1400)
        error = "NetworkTransientError" if status == "FAILED" else ""
    
    log_rows.append({
        "execution_id": f"EXEC-{i:04d}",
        "workflow_id": wf_id,
        "workflow_name": wf_name,
        "status": status,
        "execution_time_ms": exec_time,
        "error_type": error,
        "timestamp": f"2026-10-{random.randint(1, 13):02d}T{random.randint(8, 22):02d}:{random.randint(10, 59):02d}:00Z"
    })

with open('data/workflow_logs.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(log_rows[0].keys()))
    writer.writeheader()
    writer.writerows(log_rows)

# 9. WF011: refund_requests.json (Proof of Extensibility)
refunds_data = [
    {"refund_id": "REF-501", "order_id": "ORD-1002", "customer_email": "tony.stark@example.com", "amount": 399.99, "reason": "Defective item upon arrival", "days_since_purchase": 5, "policy_max_days": 30, "auto_approved": True},
    {"refund_id": "REF-502", "order_id": "ORD-1001", "customer_email": "sarah.connor@example.com", "amount": 289.98, "reason": "Buyer remorse after 45 days", "days_since_purchase": 45, "policy_max_days": 30, "auto_approved": False}
]
with open('data/refund_requests.json', 'w', encoding='utf-8') as f:
    json.dump(refunds_data, f, indent=2)

print("All realistic simulated datasets created successfully!")
