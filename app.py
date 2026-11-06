import streamlit as st
import pandas as pd
from pathlib import Path
from pipeline.generate_data import generate
from pipeline.failure_injector import SCENARIOS, inject
from pipeline.etl import reset_fixes, load_fixes
from run import run_with_healing, approve, read_incidents, LOG

st.set_page_config(page_title="Self-Healing Pipeline", layout="wide")
st.title("🩺 Self-Healing Data Pipeline")

if not Path("data/clean_orders.csv").exists():
    generate()

with st.sidebar:
    st.header("Controls")
    sc = st.selectbox("Failure scenario", list(SCENARIOS), format_func=lambda k: f"{k} — {SCENARIOS[k]}")
    if st.button("1) Inject failure"):
        inject(sc); st.success(f"Injected: {sc}")
    if st.button("2) Run pipeline 🚀", type="primary"):
        run_with_healing(); st.rerun()
    if st.button("Reset (fixes + logs)"):
        reset_fixes(); LOG.unlink(missing_ok=True); st.rerun()
    st.caption("Active fixes"); st.json(load_fixes())

incidents = read_incidents()
if not incidents:
    st.info("Sidebar se failure inject karo, phir pipeline run karo.")
for i, inc in enumerate(reversed(incidents)):
    icon = {"success": "✅", "auto_fixed": "🛠️", "needs_approval": "⏳", "human_approved": "👤",
            "escalated": "🚨", "gave_up": "❌"}.get(inc["status"], "•")
    with st.expander(f"{icon} {inc['ts']} — {inc['status']}", expanded=(i == 0)):
        if "error" in inc:
            st.error(inc["error"]["message"])
            st.json(inc["error"]["details"], expanded=False)
        if "diagnosis" in inc:
            d = inc["diagnosis"]
            st.markdown(f"**Root cause:** {d['root_cause']}")
            st.markdown(f"**Reasoning:** {d['reasoning']}  \n**Confidence:** {d['confidence']} · `{d['source']}`")
            st.code(str(d["fix"]), language="json")
            if inc["status"] == "needs_approval" and i == 0:
                if st.button("✅ Approve fix & rerun", key=f"ap{i}"):
                    approve(d["fix"]); st.rerun()
        if "rows_loaded" in inc:
            st.success(f"{inc['rows_loaded']} rows warehouse me load hui")

if Path("warehouse.duckdb").exists():
    import duckdb
    try:
        st.subheader("warehouse.orders (preview)")
        st.dataframe(duckdb.connect("warehouse.duckdb", read_only=True)
                     .execute("SELECT * FROM orders LIMIT 10").df())
    except Exception:
        pass
