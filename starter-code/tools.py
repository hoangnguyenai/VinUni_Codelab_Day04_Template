import json
import os
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "raw-data")

# ---------------------------------------------------------------------------
# Tool #1: search_product_catalog
# Đọc product_catalog.json, lọc theo category và max_price.
# ---------------------------------------------------------------------------

def search_product_catalog(category: str, max_price: int = 999999999999) -> List[Dict[str, Any]]:
    """
    Tra cứu sản phẩm/dịch vụ Vingroup theo danh mục và giá tối đa.
    
    Args:
        category: Loại sản phẩm ('xe_dien' hoặc 'du_lich').
        max_price: Giá tối đa (VNĐ). Mặc định không giới hạn.
    
    Returns:
        Danh sách sản phẩm phù hợp điều kiện.
    """
    catalog_file = os.path.join(RAW_DATA_DIR, "product_catalog.json")
    try:
        with open(catalog_file, encoding="utf-8") as source:
            products = json.load(source)
        return [p for p in products
                if p["category"].lower() == category.strip().lower()
                and p["price_vnd"] <= max_price]
    except FileNotFoundError:
        return [{"error": "Product catalog file not found."}]
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return [{"error": f"Không thể đọc danh mục sản phẩm: {exc}"}]


# ---------------------------------------------------------------------------
# Tool #2: submit_support_ticket
# Tạo ticket mới và lưu vào support_tickets.json.
# ---------------------------------------------------------------------------

def submit_support_ticket(
    customer_name: str,
    issue_description: str,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Ghi nhận yêu cầu hỗ trợ của khách hàng vào hệ thống ticket.
    
    Args:
        customer_name: Tên khách hàng.
        issue_description: Mô tả vấn đề cần hỗ trợ.
        priority: Mức độ ưu tiên ('low', 'medium', 'high'). Mặc định 'medium'.
    
    Returns:
        Thông tin ticket vừa tạo bao gồm ticket_id, status.
    """
    tickets_file = os.path.join(RAW_DATA_DIR, "support_tickets.json")
    priority = priority.strip().lower()
    if not customer_name.strip() or not issue_description.strip():
        return {"error": "Cần tên khách hàng và mô tả vấn đề để tạo ticket."}
    if priority not in {"low", "medium", "high"}:
        return {"error": "Priority phải là low, medium hoặc high."}
    try:
        existing_tickets = []
        if os.path.exists(tickets_file):
            with open(tickets_file, encoding="utf-8") as source:
                existing_tickets = json.load(source)
        if not isinstance(existing_tickets, list):
            return {"error": "Dữ liệu ticket phải là một danh sách."}
        now = datetime.now(timezone(timedelta(hours=7)))
        prefix = f"TK-{now:%Y%m%d}-"
        used_ids = {ticket["ticket_id"] for ticket in existing_tickets}
        seq = len(existing_tickets) + 1
        while f"{prefix}{seq:03d}" in used_ids:
            seq += 1
        ticket_id = f"{prefix}{seq:03d}"
        new_ticket = {
            "ticket_id": ticket_id,
            "customer_name": customer_name.strip(),
            "issue_description": issue_description.strip(),
            "priority": priority,
            "status": "open",
            "created_at": now.isoformat(),
            "category": "general",
        }
        existing_tickets.append(new_ticket)
        with open(tickets_file, "w", encoding="utf-8") as destination:
            json.dump(existing_tickets, destination, indent=2, ensure_ascii=False)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {"error": f"Không thể lưu yêu cầu hỗ trợ: {exc}"}
    return {
        "ticket_id": ticket_id,
        "customer_name": new_ticket["customer_name"],
        "priority": priority,
        "status": "open",
        "message": f"Ticket {ticket_id} đã được tạo thành công.",
    }


# ---------------------------------------------------------------------------
# TOOL_DEFINITIONS — JSON Schemas mô tả cho LLM
# JSON Schema cho từng tool (name, description, parameters).
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "name": "search_product_catalog",
        "description": "Tra cứu sản phẩm/dịch vụ Vingroup theo danh mục và giá tối đa.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Danh mục xe điện hoặc du lịch.",
                    "enum": ["xe_dien", "du_lich"],
                },
                "max_price": {
                    "type": "integer",
                    "description": "Giá tối đa tính bằng VNĐ.",
                    "minimum": 0,
                },
            },
            "required": ["category"],
            "additionalProperties": False,
        },
    },
    {
        "name": "submit_support_ticket",
        "description": "Tạo và lưu yêu cầu hỗ trợ của khách hàng Vingroup.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_name": {"type": "string", "description": "Tên khách hàng.", "minLength": 1},
                "issue_description": {"type": "string", "description": "Mô tả vấn đề cần hỗ trợ.", "minLength": 1},
                "priority": {
                    "type": "string",
                    "description": "Mức ưu tiên xử lý.",
                    "enum": ["low", "medium", "high"],
                    "default": "medium",
                },
            },
            "required": ["customer_name", "issue_description"],
            "additionalProperties": False,
        },
    },
]


# ---------------------------------------------------------------------------
# TOOL_MAP — Ánh xạ tên tool → hàm thực thi
# ---------------------------------------------------------------------------

TOOL_MAP = {
    "search_product_catalog": search_product_catalog,
    "submit_support_ticket": submit_support_ticket
}
