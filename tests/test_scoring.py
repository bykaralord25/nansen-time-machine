from app.scoring import score_decision

def test_buy_up_scores_correct():
    r = score_decision("BUY", 10)
    assert r["correct"] is True
    assert r["score"] > 55

def test_short_up_scores_wrong():
    r = score_decision("SHORT", 10)
    assert r["correct"] is False
    assert r["score"] < 55
