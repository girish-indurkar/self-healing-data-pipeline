"""Orchestrator: run -> fail -> diagnose -> (safe? auto-fix : approval) -> rerun"""
import json
import time
from pathlib import Path
from pipeline.etl import run_pipeline, PipelineError, load_fixes, add_fix, EXPECTED
from agent.diagnose import diagnose, SAFE_ACTIONS

LOG = Path("logs/incidents.jsonl")


def log(entry):
    LOG.parent.mkdir(exist_ok=True)
    entry["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with LOG.open("a") as f:
        f.write(json.dumps(entry, default=str) + "\n")
    return entry


def run_with_healing(max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        try:
            rows = run_pipeline()
            return log({"status": "success", "attempt": attempt, "rows_loaded": rows})
        except PipelineError as e:
            err = e.to_dict()
            diag = diagnose(err, EXPECTED, load_fixes())
            fix = diag["fix"]
            if fix["action"] in SAFE_ACTIONS:
                add_fix(fix)
                log({"status": "auto_fixed", "attempt": attempt, "error": err, "diagnosis": diag})
                continue
            return log({"status": "needs_approval", "attempt": attempt, "error": err, "diagnosis": diag})
    return log({"status": "gave_up", "attempt": max_attempts})


def approve(fix):
    """Human approve kare to fix apply karke rerun."""
    if fix["action"] == "escalate":
        return log({"status": "escalated", "fix": fix})
    add_fix(fix)
    log({"status": "human_approved", "fix": fix})
    return run_with_healing()


def read_incidents():
    if not LOG.exists():
        return []
    return [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]


if __name__ == "__main__":
    print(json.dumps(run_with_healing(), indent=2, default=str))
