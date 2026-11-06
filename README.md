<div align="center">

# 🩺 Self-Healing Data Pipeline

### *Autonomous Data Quality Engineering Powered by Grok (xAI)*

<p align="center">
  <a href="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1000&color=6366F1&center=true&vCenter=true&width=650&lines=Autonomous+Data+Reliability+Agent;Powered+by+Grok+(xAI)+LLM+Diagnosis;Detects+Anomalies%2C+Synthesizes+Fixes+%26+Self-Heals;Conversational+CLI%3A+Type+'hi+dataset'+to+Begin;Sub-Second+In-Memory+DuckDB+Analytics">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1000&color=6366F1&center=true&vCenter=true&width=650&lines=Autonomous+Data+Reliability+Agent;Powered+by+Grok+(xAI)+LLM+Diagnosis;Detects+Anomalies%2C+Synthesizes+Fixes+%26+Self-Heals;Conversational+CLI%3A+Type+'hi+dataset'+to+Begin;Sub-Second+In-Memory+DuckDB+Analytics" alt="Typing SVG" />
  </a>
</p>

<p align="center">
  <strong>An enterprise-grade, closed-loop data pipeline that detects schema drift, corrupted formats, and data anomalies—then autonomously diagnoses root causes and heals the pipeline before downstream warehouses break.</strong>
</p>

<p align="center">
  <a href="https://github.com/girish-indurkar/self-healing-data-pipeline/actions/workflows/ci.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/girish-indurkar/self-healing-data-pipeline/ci.yml?branch=main&style=for-the-badge&logo=githubactions&logoColor=white&label=CI%2FCD&color=10B981" alt="CI/CD" />
  </a>
  <a href="https://github.com/girish-indurkar/self-healing-data-pipeline/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/girish-indurkar/self-healing-data-pipeline?style=for-the-badge&color=6366F1" alt="License" />
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  </a>
  <a href="https://x.ai/">
    <img src="https://img.shields.io/badge/AI_Engine-Grok_(xAI)-000000?style=for-the-badge&logo=x&logoColor=white" alt="Grok xAI" />
  </a>
  <a href="https://duckdb.org/">
    <img src="https://img.shields.io/badge/Warehouse-DuckDB-FFF000?style=for-the-badge&logo=duckdb&logoColor=black" alt="DuckDB" />
  </a>
  <a href="https://streamlit.io/">
    <img src="https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  </a>
</p>

<p align="center">
  <a href="#-quick-start"><strong>🚀 Quick Start</strong></a> •
  <a href="#-architecture"><strong>🏗️ Architecture</strong></a> •
  <a href="#-interactive-cli"><strong>💬 Conversational CLI</strong></a> •
  <a href="#-features"><strong>✨ Features</strong></a> •
  <a href="#-tech-stack"><strong>🛠️ Tech Stack</strong></a> •
  <a href="#-faq"><strong>❓ FAQ</strong></a>
</p>

</div>

---

## 🎯 Executive Summary

Data pipelines frequently break due to unexpected upstream alterations: **renamed columns, dirty currency strings, replayed batches with duplicate IDs, or unexpected nulls**. Traditional ETL systems crash, wake up on-call data engineers at 3 AM, and require hours of manual scripting to patch.

The **Self-Healing Data Pipeline** introduces an autonomous reliability agent that:
1. **Intercepts Failures:** Catches structured schema mismatches, type violations, nulls, and duplicate anomalies.
2. **Cognitive Root-Cause Diagnosis:** Leverages **Grok (xAI)** via fast LLM reasoning (with zero-dependency deterministic rule fallback) to deduce upstream causes.
3. **Guardrailed Auto-Remediation:** Safely auto-applies non-destructive fixes (`cast_type`, `rename_column`, `drop_duplicates`) while gating high-impact actions behind human approval.
4. **Resilient Warehouse Ingestion:** Validates the healed dataset and persists clean records into an embedded **DuckDB** data warehouse.

---

## ✨ Features

<table>
  <tr>
    <td width="33%" valign="top">
      <h3>🤖 Grok (xAI) Diagnosis</h3>
      <p>Uses high-speed reasoning from xAI's Grok model to parse error traces, evaluate sample records, and generate valid remediation plans.</p>
    </td>
    <td width="33%" valign="top">
      <h3>🔄 Closed-Loop Healing</h3>
      <p>Automatic retry loop: <code>Validate &rarr; Diagnose &rarr; Fix &rarr; Re-validate</code>. Repeats until data meets 100% compliance.</p>
    </td>
    <td width="33%" valign="top">
      <h3>🛡️ Dual Safety Guardrails</h3>
      <p>Whitelisted action taxonomy. Safe actions auto-apply instantly; risky operations (null drops, escalations) pause for human authorization.</p>
    </td>
  </tr>
  <tr>
    <td width="33%" valign="top">
      <h3>💬 Conversational CLI</h3>
      <p>Natural language interactive terminal. Type <code>"hi dataset"</code> to preview data and <code>"datapipeline"</code> to trigger healing.</p>
    </td>
    <td width="33%" valign="top">
      <h3>⚡ DuckDB Analytics</h3>
      <p>Blazing-fast columnar storage engine stores clean records with transactional guarantees and sub-second SQL queries.</p>
    </td>
    <td width="33%" valign="top">
      <h3>📊 Streamlit Web UI</h3>
      <p>Interactive web control center to inject synthetic upstream anomalies, trigger pipelines, and inspect real-time audit logs.</p>
    </td>
  </tr>
</table>

---

## 🏗️ Architecture

```mermaid
flowchart TD
    subgraph INGESTION ["📥 Ingestion & Interface Layer"]
        CLI["💬 Conversational CLI<br/>('hi dataset' / 'datapipeline')"]
        UI["📊 Streamlit Web Dashboard<br/>(Failure Injector & Metrics)"]
        CSV["📄 Upstream Data Batch<br/>(orders.csv)"]
    end

    subgraph QUALITY_GATE ["🔍 Data Quality & Validation Engine"]
        VAL{"⚖️ Schema & Type Validator"}
        ERR["⚠️ Structured Pipeline Error<br/>(Type / Schema / Null / Duplicate)"]
    end

    subgraph COGNITIVE_LAYER ["🧠 Cognitive Diagnosis Layer"]
        AGENT["🤖 Diagnosis Agent"]
        GROK["⚡ Grok (xAI) LLM<br/>(api.x.ai/v1)"]
        RULES["📏 Deterministic Rule Engine<br/>(Zero-API Fallback)"]
    end

    subgraph SAFETY_GATE ["🛡️ Policy & Safety Controller"]
        GATE{"Is Action Safe?"}
        AUTO["✅ Safe Actions<br/>(rename_column, cast_type, drop_duplicates)"]
        HUMAN["👤 Human Approval Gate<br/>(fill_nulls, drop_null_rows, escalate)"]
    end

    subgraph EXECUTION ["⚙️ Transformation & Storage Layer"]
        FIX["🛠️ Fix Applicator Engine"]
        WAREHOUSE[("⚡ DuckDB Warehouse<br/>(warehouse.orders)")]
        LOGS[("📝 JSONL Incident Ledger<br/>(logs/incidents.jsonl)")]
    end

    CLI --> CSV
    UI --> CSV
    CSV --> VAL
    VAL -- "Valid Data" --> WAREHOUSE
    VAL -- "Violations Found" --> ERR
    ERR --> AGENT
    AGENT --> GROK
    AGENT -.->|Fallback| RULES
    GROK --> GATE
    RULES --> GATE
    GATE -- "Safe" --> AUTO
    GATE -- "Risky" --> HUMAN
    AUTO --> FIX
    HUMAN -- "Approved" --> FIX
    FIX --> VAL
    FIX --> LOGS

    style INGESTION fill:#1E293B,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC
    style QUALITY_GATE fill:#1E293B,stroke:#F59E0B,stroke-width:2px,color:#F8FAFC
    style COGNITIVE_LAYER fill:#1E293B,stroke:#818CF8,stroke-width:2px,color:#F8FAFC
    style SAFETY_GATE fill:#1E293B,stroke:#10B981,stroke-width:2px,color:#F8FAFC
    style EXECUTION fill:#1E293B,stroke:#EC4899,stroke-width:2px,color:#F8FAFC
```

---

## 💬 Conversational CLI Experience

The pipeline includes a conversational terminal assistant powered by `rich`. You can interact naturally using phrases like **`"hi dataset"`** or **`"datapipeline"`**:

```text
╔═══════════════════════════════════════════════════════════════╗
║           🔧 Self-Healing Data Pipeline Agent 🔧              ║
║                                                               ║
║   Automatically detect and fix data quality issues            ║
║   Powered by Grok (xAI) + Rule-based Fallback                 ║
╚═══════════════════════════════════════════════════════════════╝

🔧 Pipeline Agent: hi dataset
👋 Hello! I'm your Self-Healing Pipeline Agent!
📂 Enter CSV file path: tests/fixtures/dirty_types.csv
✅ Loaded: tests/fixtures/dirty_types.csv (5 rows × 4 columns)

          📊 Data Preview (first 5 rows)
  order_id   customer_name   amount    order_date
 ─────────────────────────────────────────────────
  1          Alice           $100.50   2024-01-15
  2          Bob             $200.00   2024-01-16
  3          Charlie         $50.75    2024-02-01
  4          Diana           $300.25   2024-02-14
  5          Eve             $75.00    2024-03-01

🔧 Pipeline Agent: datapipeline
🔄 Healing Attempt 1/3
                             🔍 Validation Errors
┌───────────────┬─────────────────────────────────────────────────────────────┐
│ Type          │ Details                                                     │
├───────────────┼─────────────────────────────────────────────────────────────┤
│ type_mismatch │ column: amount, expected_type: float, bad_samples:          │
│               │ ['$100.50', '$200.00', '$50.75', '$300.25', '$75.00']      │
└───────────────┴─────────────────────────────────────────────────────────────┘

🤖 Diagnosing...
🩺 Root Cause: 'amount' contains formatted currency strings
   Confidence: 85%
   Proposed Fix: {'action': 'cast_type', 'column': 'amount', 'type': 'float'}

🔄 Healing Attempt 2/3
✅ All validations passed!
📝 Pipeline Status: SUCCESS (1 fix applied)
✨ Data Cleaned and Loaded into DuckDB Warehouse!
```

---

## 🛠️ Supported Self-Healing Actions

| Action | Classification | Description | Automatic? |
| :--- | :---: | :--- | :---: |
| `rename_column` | `SAFE` | Maps renamed upstream column names back to expected schema definitions | ✅ Auto-applied |
| `cast_type` | `SAFE` | Strips currency symbols (`$`, `€`), commas, whitespace, and casts to numeric/dates | ✅ Auto-applied |
| `drop_duplicates` | `SAFE` | Eliminates duplicated records generated by replayed upstream network batches | ✅ Auto-applied |
| `fill_nulls` | `RISKY` | Imputes missing values with calculated or default constants | ⚠️ Requires Approval |
| `drop_null_rows` | `RISKY` | Removes records with missing non-nullable attributes | ⚠️ Requires Approval |
| `escalate` | `CRITICAL` | Alerts human engineering team when ambiguity exceeds confidence thresholds | 🚨 Human Review |

---

## 🛠 Tech Stack

<div align="center">

| Domain | Technologies |
| :--- | :--- |
| **Language** | ![Python](https://img.shields.io/badge/Python_3.10+-3776AB?style=flat-square&logo=python&logoColor=white) |
| **AI / Reasoning** | ![Grok xAI](https://img.shields.io/badge/xAI_Grok-000000?style=flat-square&logo=x&logoColor=white) ![OpenAI Compatible](https://img.shields.io/badge/OpenAI_API_Spec-412991?style=flat-square&logo=openai&logoColor=white) |
| **Warehouse & Data** | ![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?style=flat-square&logo=duckdb&logoColor=black) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) |
| **Terminal & Web UI** | ![Rich](https://img.shields.io/badge/Rich_CLI-008080?style=flat-square&logo=terminal&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) |
| **Testing & CI/CD** | ![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white) ![Ruff](https://img.shields.io/badge/Ruff-D7FF64?style=flat-square&logo=ruff&logoColor=black) ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white) |
| **Containerization** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) |

</div>

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13
- Git

### 2. Installation
```powershell
# Clone the repository
git clone https://github.com/girish-indurkar/self-healing-data-pipeline.git
cd self-healing-data-pipeline

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1    # On Windows PowerShell
# source venv/bin/activate     # On Linux / macOS

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### 3. Configure Grok (xAI) API (Optional)
The pipeline automatically uses a deterministic rule-based engine offline. To enable Grok LLM cognitive diagnosis:
```powershell
cp .env.example .env
# Edit .env:
# XAI_API_KEY=xai-your-api-key-here
# GROK_MODEL=grok-3
```

### 4. Run the Conversational Agent
```powershell
python -m self_healing_pipeline.interactive
```

### 5. Launch the Web Dashboard
```powershell
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser to simulate pipeline errors and trigger self-healing.

### 6. Run the Test Suite
```powershell
$env:PYTHONPATH="."
pytest tests/ -v
```

---

## 🐳 Docker Deployment

Run the complete pipeline inside an isolated lightweight container:

```bash
# Build the container
docker build -t self-healing-pipeline .

# Run the interactive agent
docker run -it --rm -e XAI_API_KEY="your-key" self-healing-pipeline
```

---

## 📁 Project Directory Structure

```text
self-healing-data-pipeline/
├── .github/
│   └── workflows/
│       ├── ci.yml              # Multi-Python CI/CD pipeline (Lint, Test, Docker)
│       └── snake.yml           # Automated contribution snake animation generator
├── agent/
│   ├── __init__.py             # Agent module interface
│   └── diagnose.py             # Grok (xAI) LLM diagnosis with rule-based fallback
├── pipeline/
│   ├── __init__.py             # Pipeline module exports
│   ├── etl.py                  # DuckDB ingestion & PipelineError definitions
│   ├── failure_injector.py     # Anomaly generator (renames, corruptions, duplicates)
│   ├── generate_data.py        # Synthetic test dataset generator
│   └── runner.py               # Main iterative self-healing execution loop
├── tests/
│   ├── fixtures/               # Test datasets (clean, dirty types, duplicates, nulls)
│   ├── conftest.py             # Pytest fixtures and environment configuration
│   └── test_pipeline.py        # 31 unit & integration tests (100% pass rate)
├── .env.example                # Environment variables template
├── .gitignore                  # Production Git ignore rules
├── Dockerfile                  # Container definition for containerized execution
├── requirements.txt            # Project dependencies manifest
├── setup.py                    # Package build and CLI entry points
├── app.py                      # Streamlit real-time interactive monitoring dashboard
├── apply_fix.py                # Remediation engine (renaming, casting, deduplication)
├── interactive.py              # Natural language interactive CLI
├── run.py                      # Orchestrator with human-in-the-loop approvals
├── validator.py                # Schema, type mismatch, null & duplicate validator
└── README.md                   # Project documentation
```

---

## 🔐 Environment Variables

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `XAI_API_KEY` | Optional | `None` | xAI API key from [console.x.ai](https://console.x.ai/). If omitted, rule-based fallback activates. |
| `GROK_MODEL` | Optional | `grok-3` | Model identifier to use (`grok-3`, `grok-2`, `grok-beta`). |
| `LOG_LEVEL` | Optional | `WARNING` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

---

## 📊 Live Repository Metrics & Contribution Snake

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/girish-indurkar/self-healing-data-pipeline/output/github-contribution-grid-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/girish-indurkar/self-healing-data-pipeline/output/github-contribution-grid-snake.svg">
  <img alt="GitHub contribution snake animation" src="https://raw.githubusercontent.com/girish-indurkar/self-healing-data-pipeline/output/github-contribution-grid-snake.svg">
</picture>

<br/><br/>

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=girish-indurkar&show_icons=true&theme=tokyonight&hide_border=true&count_private=true" alt="Girish's GitHub Stats" width="48%" />
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=girish-indurkar&layout=compact&theme=tokyonight&hide_border=true" alt="Top Languages" width="48%" />
</p>

</div>

---

## ❓ FAQ

<details>
<summary><strong>1. Does the pipeline require an active Grok (xAI) API key to run?</strong></summary>
<br/>
<strong>No.</strong> The system is architected with dual diagnosis backends. If <code>XAI_API_KEY</code> is not provided, the pipeline seamlessly engages its deterministic rule-based engine. It can run in air-gapped or offline environments while achieving full test suite pass rates.
</details>

<details>
<summary><strong>2. How does the pipeline prevent destructive data modifications?</strong></summary>
<br/>
Every proposed remediation is filtered through an action policy controller. Operations that alter or drop records (e.g. <code>fill_nulls</code>, <code>drop_null_rows</code>) are flagged as <code>RISKY</code> and pause for interactive user confirmation. Non-destructive operations (such as column renames and type parsing) are classified as <code>SAFE</code> and apply automatically.
</details>

<details>
<summary><strong>3. Can I connect this to PostgreSQL, Snowflake, or BigQuery instead of DuckDB?</strong></summary>
<br/>
<strong>Yes.</strong> The validation and fix engines operate directly on <code>pandas.DataFrame</code> objects. Replacing the DuckDB connector in <code>pipeline/etl.py</code> with SQLAlchemy, Snowflake-connector, or BigQuery Client allows seamless integration into any warehouse architecture.
</details>

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

<div align="center">
  <sub>Built with precision by <a href="https://github.com/girish-indurkar"><strong>Girish Indurkar</strong></a>. If this project helped you, consider starring ⭐ the repository!</sub>
</div>
