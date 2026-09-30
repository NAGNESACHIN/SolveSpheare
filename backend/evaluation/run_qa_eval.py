"""Run the product Q&A benchmark against a deployed SolveSpheare API.

Usage:
  python backend/evaluation/run_qa_eval.py --api-url http://localhost:8000 --product-id <UUID>

The evaluator uses deterministic checks for evidence/uncertainty and writes a JSON report.
"""
import argparse
import json
import re
import urllib.error
import urllib.request
from pathlib import Path


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.loads(response.read().decode())


def score_answer(case, answer):
    text = answer.get("answer", "")
    evidence = answer.get("evidence_points", [])
    confidence = answer.get("confidence")
    lower = text.lower()

    scores = {"correctness": 0, "evidence_support": 0, "completeness": 0, "no_hallucination": 2, "uncertainty_handling": 2}
    if text.strip():
        scores["correctness"] = 1
        scores["completeness"] = 1
        scores["evidence_support"] = 1
    if len(evidence) >= 2:
        scores["evidence_support"] = 2
        scores["completeness"] = 2

    if case["type"] == "insufficient_evidence":
        uncertainty_markers = ["insufficient", "not enough evidence", "does not establish", "cannot determine", "not supported"]
        scores["uncertainty_handling"] = 2 if any(marker in lower for marker in uncertainty_markers) else 0
        scores["no_hallucination"] = 2 if scores["uncertainty_handling"] == 2 else 0
    elif re.search(r"\b\d+(?:\.\d+)?%?\b", text) and len(evidence) == 0:
        scores["no_hallucination"] = 0

    if isinstance(confidence, (int, float)) and 0 <= confidence <= 1:
        scores["uncertainty_handling"] = min(scores["uncertainty_handling"], 2)
    else:
        scores["uncertainty_handling"] = 0

    scores["total"] = sum(scores.values())
    return scores


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--output", default="backend/evaluation/qa_eval_report.json")
    args = parser.parse_args()

    benchmark = json.loads(Path(__file__).with_name("qa_eval.json").read_text(encoding="utf-8"))
    results = []
    for case in benchmark["questions"]:
        try:
            payload = post(f"{args.api_url.rstrip('/')}/api/qa/products/{args.product_id}", {"question": case["question"]})
            answer = payload.get("answer", {})
            scores = score_answer(case, answer)
            results.append({"id": case["id"], "question": case["question"], "type": case["type"], "answer": answer, "scores": scores})
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            results.append({"id": case["id"], "question": case["question"], "type": case["type"], "error": str(exc), "scores": {"total": 0}})

    total = len(results)
    scored = [r for r in results if "error" not in r]
    max_score = total * 10
    achieved = sum(r["scores"]["total"] for r in results)
    insufficient = [r for r in results if r["type"] == "insufficient_evidence"]
    correct_uncertainty = sum(1 for r in insufficient if r["scores"].get("uncertainty_handling") == 2)
    hallucinations = sum(1 for r in results if r["scores"].get("no_hallucination") == 0)

    report = {
        "questions": total,
        "successful_requests": len(scored),
        "average_score_percent": round((achieved / max_score) * 100, 2) if max_score else 0,
        "hallucination_rate_percent": round((hallucinations / total) * 100, 2) if total else 0,
        "correct_uncertainty_rate_percent": round((correct_uncertainty / len(insufficient)) * 100, 2) if insufficient else 0,
        "results": results,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k != "results"}, indent=2))


if __name__ == "__main__":
    main()
