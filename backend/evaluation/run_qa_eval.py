"""Run the product Q&A benchmark against a deployed SolveSpheare API."""
import argparse, json, urllib.error, urllib.request
from pathlib import Path


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.loads(response.read().decode())


def score_answer(case, answer):
    text = str(answer.get("answer", "")); lower = text.lower()
    evidence = answer.get("evidence_points", [])
    expected = case["expected"]
    scores = {"correctness":0,"evidence_support":0,"completeness":0,"no_hallucination":2,"uncertainty_handling":2}
    facts = expected.get("facts", [])
    required = expected.get("required_terms", [])
    forbidden = expected.get("must_not_claim", [])

    matched_terms = sum(1 for term in required if term.lower() in lower)
    scores["correctness"] = 2 if text.strip() and (not required or matched_terms == len(required)) else (1 if text.strip() else 0)
    scores["completeness"] = 2 if len(evidence) >= 2 else (1 if evidence else 0)
    scores["evidence_support"] = 2 if len(evidence) >= 2 else (1 if evidence else 0)

    forbidden_hits = [claim for claim in forbidden if claim.lower() in lower]
    scores["no_hallucination"] = 0 if forbidden_hits else 2

    if case["type"] == "insufficient_evidence":
        markers = ["insufficient", "not enough evidence", "does not establish", "cannot determine", "not supported"]
        scores["uncertainty_handling"] = 2 if any(marker in lower for marker in markers) else 0
        scores["no_hallucination"] = 0 if forbidden_hits else scores["no_hallucination"]
    elif case["type"] == "contradictory_evidence":
        mixed_markers = ["mixed", "both", "however", "while", "different", "disagree"]
        scores["uncertainty_handling"] = 2 if any(marker in lower for marker in mixed_markers) else 1

    confidence = answer.get("confidence")
    if not isinstance(confidence, (int,float)) or not 0 <= confidence <= 1:
        scores["uncertainty_handling"] = 0

    scores["total"] = sum(scores.values())
    return scores


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--api-url",required=True); parser.add_argument("--product-id",required=True); parser.add_argument("--output",default="backend/evaluation/qa_eval_report.json")
    args=parser.parse_args()
    benchmark=json.loads(Path(__file__).with_name("qa_eval.json").read_text(encoding="utf-8"))
    results=[]
    for case in benchmark["questions"]:
        try:
            payload=post(f"{args.api_url.rstrip('/')}/api/qa/products/{args.product_id}",{"question":case["question"]})
            answer=payload.get("answer",{}); scores=score_answer(case,answer)
            results.append({"id":case["id"],"question":case["question"],"type":case["type"],"answer":answer,"scores":scores})
        except (urllib.error.URLError,urllib.error.HTTPError,TimeoutError,json.JSONDecodeError) as exc:
            results.append({"id":case["id"],"question":case["question"],"type":case["type"],"error":str(exc),"scores":{"total":0}})

    total=len(results); successful=[r for r in results if "error" not in r]; achieved=sum(r["scores"]["total"] for r in results); max_score=total*10
    insufficient=[r for r in results if r["type"]=="insufficient_evidence"]
    mixed=[r for r in results if r["type"]=="contradictory_evidence"]
    report={
        "questions":total,"successful_requests":len(successful),
        "average_score_percent":round(achieved/max_score*100,2) if max_score else 0,
        "grounding_rate_percent":round(sum(r["scores"]["evidence_support"]==2 and r["scores"]["no_hallucination"]==2 for r in results)/total*100,2) if total else 0,
        "hallucination_rate_percent":round(sum(r["scores"]["no_hallucination"]==0 for r in results)/total*100,2) if total else 0,
        "correct_uncertainty_rate_percent":round(sum(r["scores"]["uncertainty_handling"]==2 for r in insufficient)/len(insufficient)*100,2) if insufficient else 0,
        "contradictory_evidence_handling_percent":round(sum(r["scores"]["uncertainty_handling"]==2 for r in mixed)/len(mixed)*100,2) if mixed else 0,
        "results":results}
    Path(args.output).parent.mkdir(parents=True,exist_ok=True); Path(args.output).write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="results"},indent=2))

if __name__=="__main__": main()
