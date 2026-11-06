# Self-Healing Data Pipeline with AI Agent

Pipeline fail -> LLM agent log + schema padhta hai -> root cause + guarded fix deta hai
-> safe fix auto-apply, risky fix human approval -> rerun.

## Run
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...      # optional; bina key ke rule-based fallback
    python -m pipeline.generate_data
    streamlit run app.py

CLI: python -c "from pipeline.failure_injector import inject; inject('column_rename')" && python run.py

## Guardrails
Agent sirf whitelisted actions de sakta hai (rename_column, cast_type, drop_duplicates auto;
fill_nulls, drop_null_rows, escalate => human approval).

## Tests
    pytest tests -v     # 12 tests: pipeline, agent guardrails, mocked LLM, Streamlit UI
