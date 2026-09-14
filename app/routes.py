import json
from pathlib import Path
from flask import Blueprint, jsonify, render_template, request
from .scoring import score_decision

bp = Blueprint("main", __name__)
ROOT = Path(__file__).resolve().parents[1]
SCENARIO_FILE = ROOT / "data" / "scenarios" / "demo.json"

def load_scenarios():
    return json.loads(SCENARIO_FILE.read_text(encoding="utf-8"))

@bp.get("/")
def index(): return render_template("index.html")

@bp.get("/api/scenarios")
def scenarios():
    return jsonify([{k:v for k,v in s.items() if k not in {"future","answer_note"}} for s in load_scenarios()])

@bp.get("/api/scenario/<scenario_id>")
def scenario(scenario_id):
    s = next((x for x in load_scenarios() if x["id"] == scenario_id), None)
    if not s: return jsonify({"error":"Scenario not found"}),404
    return jsonify({k:v for k,v in s.items() if k not in {"future","answer_note"}})

@bp.get("/api/reveal/<scenario_id>")
def reveal(scenario_id):
    s = next((x for x in load_scenarios() if x["id"] == scenario_id), None)
    if not s: return jsonify({"error":"Scenario not found"}),404
    horizon=request.args.get("horizon","7d"); decision=request.args.get("decision","PASS").upper()
    future_price=s["future"][horizon]; market_return=(future_price/s["entry_price"]-1)*100; scored=score_decision(decision,market_return)
    return jsonify({"entry_price":s["entry_price"],"future_price":future_price,"market_return":round(market_return,2),"decision_return":scored["simulated_return"],"score":scored["score"],"direction_correct":scored["correct"],"story":s["answer_note"],"horizon":horizon})

@bp.get("/health")
def health(): return jsonify({"ok":True})
