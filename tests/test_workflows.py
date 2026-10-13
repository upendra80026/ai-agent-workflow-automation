import pytest
from core.engine import WorkflowEngine
from core.excel_loader import load_workflows_from_excel, load_test_questions_from_excel
from core.tool_registry import registry
from core.models import WorkflowDefinition


@pytest.fixture(scope="module")
def engine():
    return WorkflowEngine("AI_Agent_Workflow_Assessment.xlsx")


def test_excel_loading():
    wfs = load_workflows_from_excel("AI_Agent_Workflow_Assessment.xlsx")
    assert len(wfs) == 10
    assert "WF001" in wfs
    assert "WF010" in wfs

    questions = load_test_questions_from_excel("AI_Agent_Workflow_Assessment.xlsx")
    assert len(questions) == 10


def test_tool_registry_registered():
    tools = registry.list_tools()
    assert len(tools) >= 20
    # Execute a sample tool
    res = registry.execute_tool("csv_inventory_reader", filepath="data/inventory.csv")
    assert res["status"] == "SUCCESS"
    assert len(res["result"]) > 0


@pytest.mark.parametrize("expected_id,query", [
    ("WF001", "Which products need restocking?"),
    ("WF002", "Find products where vendor price differs by more than 10%."),
    ("WF003", "Process this vendor spreadsheet and show invalid rows."),
    ("WF004", "Generate SEO content for this product."),
    ("WF005", "Where is order ORD-1001?"),
    ("WF006", "Find likely duplicate products in the catalog."),
    ("WF007", "Create a campaign brief for the new collection."),
    ("WF008", "Classify these keywords and map them to pages."),
    ("WF009", "Assign this urgent task to the best available developer."),
    ("WF010", "Which workflows are failing most often?"),
])
def test_all_10_workflows_routing(engine, expected_id, query):
    result = engine.execute(query)
    assert result.workflow_id == expected_id
    assert result.confidence_score >= 0.70
    assert len(result.steps_executed) > 0
    assert result.status == "SUCCESS"


def test_wf001_inventory_restock(engine):
    res = engine.execute("Which products need restocking?")
    assert res.workflow_id == "WF001"
    data = res.structured_data
    assert data["products_needing_restock_count"] > 0
    # Confirm deficit logic
    for item in data["restock_list"]:
        assert item["current_stock"] < item["minimum_stock"]


def test_wf002_price_validation(engine):
    res = engine.execute("Find products where vendor price differs by more than 10%.")
    assert res.workflow_id == "WF002"
    data = res.structured_data
    assert data["total_exceptions"] > 0
    for exc in data["exceptions"]:
        if "percentage_diff" in exc:
            assert exc["percentage_diff"] > 10.0


def test_wf003_vendor_data_cleaning(engine):
    res = engine.execute("Process this vendor spreadsheet and show invalid rows.")
    assert res.workflow_id == "WF003"
    data = res.structured_data
    assert data["invalid_rows_count"] > 0
    assert data["valid_rows_count"] > 0


def test_wf005_order_lookup_found_and_not_found(engine):
    # Found order
    res_found = engine.execute("Where is order ORD-1001?")
    assert res_found.workflow_id == "WF005"
    assert res_found.structured_data.get("found") is True
    assert res_found.structured_data.get("order_id") == "ORD-1001"

    # Missing order handling
    res_missing = engine.execute("Where is order ORD-9999?")
    assert res_missing.workflow_id == "WF005"
    assert res_missing.structured_data.get("found") is False


def test_wf006_duplicate_detection(engine):
    res = engine.execute("Find likely duplicate products in the catalog.")
    assert res.workflow_id == "WF006"
    data = res.structured_data
    assert data["definite_duplicates_count"] >= 1
    assert data["possible_duplicates_count"] >= 1


def test_wf010_performance_report(engine):
    res = engine.execute("Which workflows are failing most often?")
    assert res.workflow_id == "WF010"
    data = res.structured_data
    assert data["flagged_workflows_count"] > 0


def test_extensibility_11th_workflow(engine):
    wf011_def = WorkflowDefinition(
        workflow_id="WF011",
        workflow_name="Customer Refund Policy Evaluation",
        trigger="User requests a refund or asks to approve a return",
        inputs="Order ID; return reason; days since purchase",
        steps_raw="Load order -> audit return window -> verify condition -> evaluate auto-refund threshold -> dispatch decision",
        steps=["Load order", "Audit return window", "Verify condition", "Evaluate threshold", "Dispatch decision"],
        decision_logic="If days <= 30 and amount < $500, auto-approve; else escalate to supervisor",
        tools_required=["order_database_api", "refund_policy_evaluator"],
        expected_output="Refund approval status, decision reasoning, and transaction reference"
    )
    engine.register_workflow(wf011_def)

    res = engine.execute("Evaluate refund request for order ORD-1002")
    assert res.workflow_id == "WF011"
    assert len(res.steps_executed) > 0
    assert len(res.decisions_made) > 0
