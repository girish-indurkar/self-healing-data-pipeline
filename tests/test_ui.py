from streamlit.testing.v1 import AppTest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent


def test_dashboard_end_to_end(env):
    sys.path.insert(0, str(ROOT))
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    assert not at.exception
    at.sidebar.selectbox[0].select("column_rename")
    [b for b in at.sidebar.button if b.label.startswith("1)")][0].click().run()
    [b for b in at.sidebar.button if b.label.startswith("2)")][0].click().run()
    assert not at.exception
    labels = [e.label for e in at.expander]
    assert any("success" in l for l in labels) and any("auto_fixed" in l for l in labels)


def test_dashboard_approval_button(env):
    sys.path.insert(0, str(ROOT))
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    at.sidebar.selectbox[0].select("null_values")
    [b for b in at.sidebar.button if b.label.startswith("1)")][0].click().run()
    [b for b in at.sidebar.button if b.label.startswith("2)")][0].click().run()
    approve = [b for b in at.button if "Approve" in b.label]
    assert approve, "Approve button dikhna chahiye"
    approve[0].click().run()
    assert not at.exception
    assert any("human_approved" in e.label for e in at.expander)
