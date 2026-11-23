"""
Unit and Integration Tests: Decentralized Verification & Consensus
===================================================================
Tests intelligent evaluation, Equivalence Principle consensus validation,
leader/validator agreement & disagreement, unavailable source handling,
and malformed model outputs.
"""

import json
import pytest
from contracts.models import ClaimStatus, Verdict, ConsensusStatus
from contracts.validation import compute_sha256, check_substantive_equivalence


def test_successful_verification_consensus(
    proof_guard, vm, bob, sample_claim_data, sample_evidence_url, sample_evidence_content
):
    """
    Tests full positive flow:
    1. Bob submits claim.
    2. Bob adds evidence URL.
    3. Mock web returns matching evidence content.
    4. Consensus reaches VERIFIED verdict.
    5. Claim status updates to VERIFIED.
    """
    vm.register_web(sample_evidence_url, sample_evidence_content)

    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )
        eid = proof_guard.add_evidence(
            claim_id=cid,
            source_url=sample_evidence_url,
            content_hash=compute_sha256(sample_evidence_content),
        )

        verification = proof_guard.verify_claim(cid)

    assert verification["verdict"] == Verdict.VERIFIED.value
    assert verification["claim_id"] == cid
    assert verification["consensus_status"] == ConsensusStatus.ACCEPTED.value
    assert eid in verification["evidence_ids"]
    assert len(verification["supporting_facts"]) > 0

    claim = proof_guard.get_claim(cid)
    assert claim["status"] == ClaimStatus.VERIFIED.value
    assert claim["current_verification_id"] == verification["verification_id"]
    assert len(claim["verification_history"]) == 1


def test_conflicting_evidence_rejected_verdict(
    proof_guard, vm, bob, sample_claim_data
):
    """
    Tests evaluation where evidence refutes the claim:
    Output produces REJECTED verdict with identified contradictions.
    """
    refute_url = "https://retractionwatch.com/paper-retracted"
    refute_content = "Correction: DeepMind did NOT release AlphaGenome v2 on October 15. The project was postponed."
    vm.register_web(refute_url, refute_content)

    # Set mock LLM to produce REJECTED output noting contradictions
    def mock_reject_llm(prompt: str) -> str:
        return json.dumps({
            "verdict": "REJECTED",
            "relevant_evidence_ids": ["claim_1_ev_1"],
            "supporting_facts": [],
            "contradictions": ["Official retraction states project was postponed and never released."],
            "explanation": "Evidence directly refutes the claim.",
        })

    vm.set_llm_handler(mock_reject_llm)

    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )
        proof_guard.add_evidence(
            claim_id=cid,
            source_url=refute_url,
            content_hash=compute_sha256(refute_content),
        )
        verification = proof_guard.verify_claim(cid)

    assert verification["verdict"] == Verdict.REJECTED.value
    assert len(verification["contradictions"]) > 0

    claim = proof_guard.get_claim(cid)
    assert claim["status"] == ClaimStatus.REJECTED.value


def test_unavailable_sources_fallback_to_inconclusive(
    proof_guard, vm, bob, sample_claim_data
):
    """
    Tests graceful degradation when external evidence sources fail to respond.
    Must safely produce INCONCLUSIVE outcome without halting the chain.
    """
    dead_url = "https://server-down.example.com/unavailable"
    # Register exception for this URL
    vm.web_responses[dead_url] = ConnectionError("503 Service Unavailable")

    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )
        proof_guard.add_evidence(
            claim_id=cid,
            source_url=dead_url,
            content_hash=compute_sha256("Unreachable content"),
        )
        verification = proof_guard.verify_claim(cid)

    assert verification["verdict"] == Verdict.INCONCLUSIVE.value
    assert "unreachable" in verification["contradictions"][0].lower() or "halted" in verification["explanation"].lower()

    claim = proof_guard.get_claim(cid)
    assert claim["status"] == ClaimStatus.INCONCLUSIVE.value


def test_leader_validator_consensus_disagreement(
    proof_guard, vm, bob, sample_claim_data, sample_evidence_url
):
    """
    Simulates a split committee where the leader proposes VERIFIED
    but independent validators determine REJECTED, causing Equivalence
    Principle failure.
    """
    vm.consensus_disagreement = True
    vm.consensus_validator_override = {
        "verdict": "REJECTED",
        "relevant_evidence_ids": ["claim_1_ev_1"],
        "supporting_facts": [],
        "contradictions": ["Independent committee found the evidence fraudulent."],
        "explanation": "Committee rejects leader proposal.",
    }

    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )
        proof_guard.add_evidence(
            claim_id=cid,
            source_url=sample_evidence_url,
            content_hash=compute_sha256("Some content"),
        )

        with pytest.raises(ValueError, match="GenLayer Consensus Failure"):
            proof_guard.verify_claim(cid)


def test_malformed_model_output_rejection(
    proof_guard, vm, bob, sample_claim_data, sample_evidence_url
):
    """Ensures completely invalid non-JSON AI output is caught and rejected."""
    vm.set_llm_handler(lambda prompt: "I am an AI and I think this claim is TRUE! (Not valid JSON)")

    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )
        proof_guard.add_evidence(
            claim_id=cid,
            source_url=sample_evidence_url,
            content_hash=compute_sha256("Test"),
        )

        with pytest.raises(ValueError, match="Malformed JSON from model"):
            proof_guard.verify_claim(cid)


def test_verify_claim_without_evidence_rejected(proof_guard, vm, bob, sample_claim_data):
    """Ensures verifying a claim with zero registered evidence sources is refused."""
    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )

        with pytest.raises(ValueError, match="has no registered evidence sources"):
            proof_guard.verify_claim(cid)


def test_substantive_equivalence_logic():
    """Unit test for check_substantive_equivalence policy rules."""
    leader = {
        "verdict": "VERIFIED",
        "relevant_evidence_ids": ["ev_1", "ev_2"],
        "supporting_facts": ["Fact A", "Fact B"],
        "contradictions": [],
        "explanation": "Verified based on official source.",
    }
    validator_equiv = {
        "verdict": "VERIFIED",
        "relevant_evidence_ids": ["ev_1"],
        "supporting_facts": ["Fact A is confirmed."],
        "contradictions": [],
        "explanation": "Independent review agrees with conclusion.",
    }
    is_equiv, msg = check_substantive_equivalence(leader, validator_equiv)
    assert is_equiv is True

    # Mismatch in verdict
    validator_diff_verdict = {
        "verdict": "REJECTED",
        "relevant_evidence_ids": ["ev_1"],
        "supporting_facts": [],
        "contradictions": ["Counter-evidence found"],
        "explanation": "Rejected.",
    }
    is_equiv, msg = check_substantive_equivalence(leader, validator_diff_verdict)
    assert is_equiv is False
    assert "Verdict mismatch" in msg

    # Completely disjoint evidence
    validator_diff_evidence = {
        "verdict": "VERIFIED",
        "relevant_evidence_ids": ["ev_99"],
        "supporting_facts": ["Other fact"],
        "contradictions": [],
        "explanation": "Different source used.",
    }
    is_equiv, msg = check_substantive_equivalence(leader, validator_diff_evidence)
    assert is_equiv is False
    assert "Evidence mismatch" in msg
