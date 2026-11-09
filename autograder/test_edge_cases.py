"""Additional checks for mixed intents, bounded execution and JSON persistence."""

import json
from pathlib import Path
import shutil
import sys
from datetime import datetime

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "starter-code"))
import tools
from template import ToolCallingAgent


@pytest.fixture(autouse=True)
def isolated_data(tmp_path, monkeypatch):
    source = Path(__file__).resolve().parents[1] / "raw-data"
    shutil.copy(source / "product_catalog.json", tmp_path)
    (tmp_path / "support_tickets.json").write_text("[]", encoding="utf-8")
    monkeypatch.setattr(tools, "RAW_DATA_DIR", str(tmp_path))
    return tmp_path


MIXED_QUERY = (
    "Cho tôi xem resort Vinpearl giá dưới 6 triệu. Và tôi cũng muốn ghi nhận "
    "phản hồi: tên tôi là Phạm Thị Dung, phòng tôi đặt ở Vinpearl Nha Trang "
    "bị ẩm mốc, mức độ trung bình."
)


def test_mixed_intents_execute_both_tools(isolated_data):
    result = ToolCallingAgent().run(MIXED_QUERY)
    calls = [step["Action"] for step in result["trace"] if "Action" in step]
    assert result["status"] == "completed"
    assert result["iterations"] == 2
    assert [call["name"] for call in calls] == ["search_product_catalog", "submit_support_ticket"]
    assert calls[0]["arguments"] == {"category": "du_lich", "max_price": 6000000}
    assert calls[1]["arguments"]["customer_name"] == "Phạm Thị Dung"
    assert "Discovery Phú Quốc" in result["answer"]
    assert "TK-" in result["answer"]
    assert len(json.loads((isolated_data / "support_tickets.json").read_text(encoding="utf-8"))) == 1


@pytest.mark.parametrize("limit, expected_calls", [(0, 0), (1, 1)])
def test_iteration_guard_prevents_pending_ticket(isolated_data, limit, expected_calls):
    result = ToolCallingAgent(max_iterations=limit).run(MIXED_QUERY)
    assert result["status"] == "max_iterations_reached"
    assert result["iterations"] == expected_calls
    assert sum("Action" in step for step in result["trace"]) == expected_calls
    assert json.loads((isolated_data / "support_tickets.json").read_text(encoding="utf-8")) == []


def test_append_tickets_and_timezone(isolated_data):
    first = tools.submit_support_ticket("An", "Xe VF 8 bị lỗi", "HIGH")
    second = tools.submit_support_ticket("Bình", "Phòng Vinpearl bị ẩm mốc")
    tickets = json.loads((isolated_data / "support_tickets.json").read_text(encoding="utf-8"))
    assert len(tickets) == 2
    assert tickets[0]["ticket_id"] == first["ticket_id"] != second["ticket_id"]
    assert tickets[0]["priority"] == "high"
    assert datetime.fromisoformat(tickets[0]["created_at"]).utcoffset().total_seconds() == 7 * 3600


def test_corrupt_tickets_are_not_overwritten(isolated_data):
    destination = isolated_data / "support_tickets.json"
    destination.write_text("invalid json", encoding="utf-8")
    assert "error" in tools.submit_support_ticket("An", "Xe bị lỗi")
    assert destination.read_text(encoding="utf-8") == "invalid json"


def test_missing_catalog_reports_error(isolated_data):
    (isolated_data / "product_catalog.json").unlink()
    result = ToolCallingAgent().run("Xem xe điện VinFast giá dưới 600 triệu")
    assert "not found" in result["answer"]
    assert "không tìm thấy sản phẩm" not in result["answer"].lower()


def test_unknown_customer_requires_name(isolated_data):
    result = ToolCallingAgent().run("Xe VinFast bị lỗi, cần hỗ trợ gấp")
    assert "cung cấp tên" in result["answer"]
    assert not any("Action" in step for step in result["trace"])
    assert json.loads((isolated_data / "support_tickets.json").read_text(encoding="utf-8")) == []


def test_trace_reset_and_no_false_ticket_on_khong():
    agent = ToolCallingAgent()
    previous = agent.run("Có xe điện nào giá dưới 200 triệu không?")
    assert "cung cấp tên" not in previous["answer"]
    assert sum("Action" in step for step in previous["trace"]) == 1
    current = agent.run("Chính sách bảo hành pin xe điện VinFast kéo dài bao lâu?")
    assert not any("Action" in step for step in current["trace"])
    assert len(previous["trace"]) == 2
    assert "10 năm" not in current["answer"]


@pytest.mark.parametrize("amount, limit", [("1,2 tỷ", 1200000000), ("600.000.000 VNĐ", 600000000)])
def test_vietnamese_price_formats(amount, limit):
    result = ToolCallingAgent().run(f"Xe điện VinFast giá dưới {amount}")
    assert result["trace"][0]["Action"]["arguments"]["max_price"] == limit


def test_out_of_scope_does_not_execute_tools():
    result = ToolCallingAgent().run("Hãy cho tôi công thức nấu ăn")
    assert "Vingroup" in result["answer"]
    assert not any("Action" in step for step in result["trace"])
