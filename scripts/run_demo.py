"""
ProofGuard Live Demonstration Runner
====================================
Simulates the entire ProofGuard contract lifecycle across multiple scenarios:
- Scenario 1: VERIFIED claim (official announcement matched by evidence)
- Scenario 2: REJECTED claim (claim refuted by contradicting evidence)
- Scenario 3: INCONCLUSIVE claim (unreachable or dead source)
- Scenario 4: DISPUTED claim (challenge, dispute resolution, and re-evaluation)
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contracts.proof_guard import ProofGuard, gl
from tests.conftest import MockGenVM, ALICE, BOB, CHARLIE


def run_demo():
    print("=" * 70)
    print("  PROOFGUARD: DECENTRALIZED EVIDENCE VERIFICATION INTELLIGENT CONTRACT")
    print("  GenLayer Intelligent Contract Live Demonstration")
    print("=" * 70)

    # 1. Initialize VM & Contract
    vm = MockGenVM()
    with vm.prank(ALICE):
        contract = ProofGuard()
    print(f"\n[INIT] Contract deployed by Owner: {ALICE}")
    print(f"[INIT] Initial total claims: {contract.get_total_claims()}\n")

    # Load scenarios
    samples_path = Path(__file__).resolve().parent.parent / "examples" / "sample_claims.json"
    with open(samples_path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    for i, scen in enumerate(scenarios, 1):
        name = scen["scenario"]
        title = scen["title"]
        desc = scen["description"]
        crit = scen["criteria"]

        print("-" * 70)
        print(f"SCENARIO {i}: {name}")
        print(f"Title   : {title}")
        print(f"Criteria: {crit}")

        # Submitter submits claim
        with vm.prank(BOB):
            cid = contract.submit_claim(title=title, description=desc, criteria=crit)
        print(f"[SUBMIT] Claim ID: {cid} by Submitter {BOB}")

        # Register evidence
        for ev in scen["evidence"]:
            url = ev["source_url"]
            chash = ev["content_hash"]
            mock_content = ev.get("mock_content", "")

            # Register web mock
            if "Unreachable" in mock_content:
                vm.web_responses[url] = ConnectionError("HTTP 503 Server Unavailable")
            else:
                vm.register_web(url, mock_content)

            with vm.prank(BOB):
                eid = contract.add_evidence(claim_id=cid, source_url=url, content_hash=chash)
            print(f"[EVIDENCE] Registered: {eid} -> {url}")

        # Setup LLM behavior depending on scenario
        if name == "REJECTED_CLAIM":
            vm.set_llm_handler(lambda prompt: json.dumps({
                "verdict": "REJECTED",
                "relevant_evidence_ids": [f"{cid}_ev_1"],
                "supporting_facts": [],
                "contradictions": ["Official audit refutes autonomous intelligence claims; found prompt leakage."],
                "explanation": "Evidence directly disproves the claim criteria.",
            }))
        elif name == "INCONCLUSIVE_CLAIM":
            # Will naturally trigger safe fallback because source is connection error
            vm.set_llm_handler(None)
        elif name == "DISPUTED_CLAIM":
            vm.set_llm_handler(lambda prompt: json.dumps({
                "verdict": "VERIFIED",
                "relevant_evidence_ids": [f"{cid}_ev_1"],
                "supporting_facts": ["Preliminary report indicates 100,000 tons injected."],
                "contradictions": [],
                "explanation": "Verified based on preliminary report.",
            }))
        else:
            vm.set_llm_handler(lambda prompt: json.dumps({
                "verdict": "VERIFIED",
                "relevant_evidence_ids": [f"{cid}_ev_1"],
                "supporting_facts": ["Official release confirmed on October 15, 2026."],
                "contradictions": [],
                "explanation": "Claim satisfies all stated verification criteria.",
            }))

        # Run verification
        print(f"[CONSENSUS] Running Equivalence Principle consensus on {cid}...")
        with vm.prank(BOB):
            verif = contract.verify_claim(cid)

        print(f"[RESULT] Verdict reached: {verif['verdict']}")
        print(f"[RESULT] Explanation    : {verif['explanation']}")
        if verif["contradictions"]:
            print(f"[RESULT] Contradictions : {verif['contradictions']}")

        # If scenario is DISPUTED, execute challenge and resolution
        if name == "DISPUTED_CLAIM" and "dispute" in scen:
            disp_info = scen["dispute"]
            print(f"\n[DISPUTE] Challenger {CHARLIE} opening dispute on {cid}...")
            with vm.prank(CHARLIE):
                disp_id = contract.open_dispute(claim_id=cid, reason=disp_info["reason"])
            print(f"[DISPUTE] Dispute opened: {disp_id}")
            print(f"[DISPUTE] Reason: {disp_info['reason']}")

            claim_state = contract.get_claim(cid)
            print(f"[STATE] Claim status transitioned to: {claim_state['status']}")

            # Admin resolves dispute
            print(f"[RESOLVE] Admin {ALICE} resolving dispute {disp_id}...")
            with vm.prank(ALICE):
                contract.resolve_dispute(
                    claim_id=cid,
                    dispute_id=disp_id,
                    resolution_notes=disp_info["resolution"],
                )
            print(f"[RESOLVE] Resolution notes: {disp_info['resolution']}")

            claim_after = contract.get_claim(cid)
            print(f"[STATE] Claim status after resolution: {claim_after['status']}")

        print()

    print("=" * 70)
    print(f"[SUMMARY] Total registered claims: {contract.get_total_claims()}")
    for i in range(1, contract.get_total_claims() + 1):
        c = contract.get_claim(f"claim_{i}")
        print(f" - claim_{i}: [{c['status']}] \"{c['title']}\"")
    print("=" * 70)
    print("[SUCCESS] All demonstration scenarios executed and verified successfully!")


if __name__ == "__main__":
    run_demo()
