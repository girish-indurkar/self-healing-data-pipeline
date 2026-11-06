
import json
import os
import re
import logging

logger = logging.getLogger(__name__)

SAFE_ACTIONS = {"rename_column", "cast_type", "drop_duplicates"}      # auto-apply
RISKY_ACTIONS = {"fill_nulls", "drop_null_rows", "escalate"}          # human approval

# Grok (xAI) configuration
XAI_BASE_URL = "https://api.x.ai/v1"
MODEL = os.getenv("GROK_MODEL", "grok-3")

SYSTEM = """You are a data pipeline reliability agent. Given a failed pipeline's error, expected schema and
sample rows, find the root cause and propose ONE fix using ONLY these actions:
- {"action":"rename_column","from":"<old>","to":"<expected name>"}
- {"action":"cast_type","column":"<col>","type":"int|float|date"}
- {"action":"drop_duplicates","column":"<col>"}
- {"action":"fill_nulls","column":"<col>","value":<value>}
- {"action":"drop_null_rows","column":"<col>"}
- {"action":"escalate","reason":"<why a human is needed>"}
Respond with ONLY valid JSON:
{"root_cause":"...","reasoning":"...","confidence":0.0-1.0,"fix":{...}}
Never invent data. If unsure, use escalate."""


def _rule_based(error, expected):
    """Rule-based fallback diagnosis when no LLM API is available."""
    t, d = error["error_type"], error["details"]
    if t == "schema_mismatch" and d["missing"] and d["unexpected"]:
        return {"root_cause": f"Upstream renamed {d['unexpected'][0]} (expected {d['missing'][0]})",
                "reasoning": "One missing + one unexpected column -> likely rename.", "confidence": 0.8,
                "fix": {"action": "rename_column", "from": d["unexpected"][0], "to": d["missing"][0]}}
    if t == "type_mismatch":
        return {"root_cause": f"'{d['column']}' contains formatted strings like {d['bad_samples']}",
                "reasoning": "Currency/formatting characters block numeric parsing.", "confidence": 0.85,
                "fix": {"action": "cast_type", "column": d["column"], "type": d["expected_type"]}}
    if t == "duplicate_violation":
        return {"root_cause": f"Duplicate keys in '{d['column']}'", "reasoning": "Replayed upstream batch.",
                "confidence": 0.8, "fix": {"action": "drop_duplicates", "column": d["column"]}}
    if t == "null_violation":
        return {"root_cause": f"NULLs in required column '{d['column']}'", "reasoning": "Cannot guess missing values.",
                "confidence": 0.6, "fix": {"action": "drop_null_rows", "column": d["column"]}}
    return {"root_cause": "Unknown", "reasoning": "", "confidence": 0.2,
            "fix": {"action": "escalate", "reason": "Unrecognized error"}}


def _parse(text):
    """Extract JSON from LLM response text."""
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"No JSON found in response: {text[:200]}")
    return json.loads(m.group(0))


def diagnose(error, expected, current_fixes):
    """
    Diagnose a data pipeline error and propose a fix.

    Uses Grok (xAI) API if XAI_API_KEY is set, otherwise falls back to
    rule-based diagnosis.

    Args:
        error: Dict with error_type and details from validation
        expected: Expected schema dict
        current_fixes: List of fixes already applied in this healing session

    Returns:
        Dict with root_cause, reasoning, confidence, fix, and source
    """
    api_key = os.getenv("XAI_API_KEY")

    if not api_key:
        logger.info("No XAI_API_KEY found, using rule-based fallback")
        out = _rule_based(error, expected)
        out["source"] = "rule_based_fallback"
    else:
        logger.info(f"Using Grok model: {MODEL}")
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=api_key,
                base_url=XAI_BASE_URL,
            )

            user_msg = json.dumps({
                "error": error,
                "expected_schema": expected,
                "already_applied_fixes": current_fixes
            }, default=str, indent=2)

            resp = client.chat.completions.create(
                model=MODEL,
                max_tokens=800,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.1,  # Low temp for deterministic fixes
            )

            out = _parse(resp.choices[0].message.content)
            out["source"] = f"llm:{MODEL}"
            logger.info(f"LLM diagnosis: {out['root_cause']} (confidence: {out.get('confidence', 'N/A')})")

        except ImportError:
            logger.warning("openai package not installed, falling back to rule-based")
            out = _rule_based(error, expected)
            out["source"] = "rule_based_fallback"
        except Exception as e:
            logger.error(f"Grok API call failed: {e}, falling back to rule-based")
            out = _rule_based(error, expected)
            out["source"] = "rule_based_fallback"

    # Safety check: only allow whitelisted actions
    action = out.get("fix", {}).get("action")
    if action not in SAFE_ACTIONS | RISKY_ACTIONS:
        out["fix"] = {"action": "escalate", "reason": f"Disallowed action proposed: {action}"}

    return out
