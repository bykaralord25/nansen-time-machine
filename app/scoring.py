def score_decision(decision: str, market_return_pct: float) -> dict:
    """Simple transparent scoring for MVP. Easy to replace later."""
    decision = decision.upper()
    if decision == "BUY":
        simulated_return = market_return_pct
        correct = market_return_pct > 0
    elif decision == "SHORT":
        simulated_return = -market_return_pct
        correct = market_return_pct < 0
    else:
        simulated_return = 0.0
        correct = abs(market_return_pct) < 4

    score = 55 + (28 if correct else -22)
    if correct:
        score += min(12, abs(market_return_pct) * 0.45)
    score = max(0, min(100, round(score)))
    return {"score": score, "correct": correct, "simulated_return": round(simulated_return, 2)}
