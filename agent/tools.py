import math
from datetime import datetime


def normalize_score(value, min_val=0, max_val=10):
    try:
        value = float(value)
        return max(min_val, min(max_val, value))
    except:
        return 0.0


def compute_final_score(market, execution, risk):
    market = normalize_score(market)
    execution = normalize_score(execution)
    risk = normalize_score(risk)
    score = (market * 0.4) + (execution * 0.35) + ((10 - risk) * 0.25)
    return round(score, 2)


def score_from_analysis(analysis_text):
    import re

    def extract(label):
        pattern = rf"{label}\s*[:\-]\s*(\d+(\.\d+)?)"
        match = re.search(pattern, analysis_text, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return None

    market = extract("market")
    execution = extract("execution")
    risk = extract("risk")

    if market is None:
        market = 6.0
    if execution is None:
        execution = 6.0
    if risk is None:
        risk = 5.0

    final_score = compute_final_score(market, execution, risk)

    return {
        "market_score": normalize_score(market),
        "execution_score": normalize_score(execution),
        "risk_score": normalize_score(risk),
        "final_score": final_score
    }


def confidence_from_critique(critique_text):
    import re
    match = re.search(r"(0\.\d+|1\.0|1)", critique_text)
    if match:
        return float(match.group(1))
    return 0.7


def current_time_tool():
    return datetime.now().isoformat()


def safe_tool_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return f"TOOL_ERROR: {str(e)}"