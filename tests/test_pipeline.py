import json
import sys
import types
import duckdb
import pandas as pd
import pytest
from pipeline.failure_injector import inject
from pipeline.etl import load_fixes
import run as orch


def rows():
    con = duckdb.connect("warehouse.duckdb")
    n = con.execute("select count(*) from orders").fetchone()[0]
    con.close()
    return n


def test_clean_data_succeeds(env):
    inject("none")
    res = orch.run_with_healing()
    assert res["status"] == "success" and res["attempt"] == 1
    assert rows() == 200 and load_fixes() == []


def test_column_rename_autoheals(env):
    inject("column_rename")
    assert orch.run_with_healing()["status"] == "success"
    assert load_fixes() == [{"action": "rename_column", "from": "total_amount", "to": "amount"}]
    assert rows() == 200


def test_type_change_autoheals_and_values_correct(env):
    inject("type_change")
    assert orch.run_with_healing()["status"] == "success"
    got = duckdb.connect("warehouse.duckdb").execute("select sum(amount) from orders").fetchone()[0]
    expected = pd.read_csv("data/clean_orders.csv")["amount"].sum()
    assert got == pytest.approx(expected, rel=1e-6)


def test_duplicates_autoheal(env):
    inject("duplicates")
    assert orch.run_with_healing()["status"] == "success"
    assert rows() == 200


def test_nulls_need_approval_then_approve(env):
    inject("null_values")
    res = orch.run_with_healing()
    assert res["status"] == "needs_approval"
    assert not __import__("pathlib").Path("warehouse.duckdb").exists()   # bad data load nahi hua
    final = orch.approve(res["diagnosis"]["fix"])
    assert final["status"] == "success" and rows() == 185


def test_multiple_failures_healed_in_multiple_attempts(env):
    inject("column_rename")
    df = pd.read_csv("data/incoming/orders.csv")
    pd.concat([df, df.head(5)]).to_csv("data/incoming/orders.csv", index=False)
    res = orch.run_with_healing()
    assert res["status"] == "success" and res["attempt"] == 3
    assert rows() == 200


def test_idempotent_fixes(env):
    inject("duplicates")
    orch.run_with_healing(); orch.run_with_healing()
    assert len(load_fixes()) == 1


def test_incident_log_written(env):
    inject("column_rename")
    orch.run_with_healing()
    statuses = [i["status"] for i in orch.read_incidents()]
    assert statuses == ["auto_fixed", "success"]


def test_guardrail_blocks_disallowed_action(env, monkeypatch):
    from agent import diagnose as d
    monkeypatch.setattr(d, "_rule_based", lambda e, x: {
        "root_cause": "x", "reasoning": "", "confidence": 1,
        "fix": {"action": "run_shell", "cmd": "rm -rf /"}})
    out = d.diagnose({"error_type": "x", "details": {}}, {}, [])
    assert out["fix"]["action"] == "escalate"


def test_llm_path_parses_fenced_json(env, monkeypatch):
    """Fake Anthropic client: LLM ```json fences ke saath reply kare to bhi parse ho."""
    reply = '```json\n{"root_cause":"renamed","reasoning":"r","confidence":0.9,' \
            '"fix":{"action":"rename_column","from":"total_amount","to":"amount"}}\n```'

    class FakeClient:
        class messages:
            @staticmethod
            def create(**kw):
                return types.SimpleNamespace(content=[types.SimpleNamespace(text=reply)])

    fake = types.ModuleType("anthropic"); fake.Anthropic = lambda: FakeClient
    monkeypatch.setitem(sys.modules, "anthropic", fake)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    inject("column_rename")
    assert orch.run_with_healing()["status"] == "success"
    assert orch.read_incidents()[0]["diagnosis"]["source"].startswith("llm:")
