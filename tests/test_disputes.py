"""
Unit and Integration Tests: Dispute Management & Audit History
==============================================================
Tests dispute opening, authorization checks, dispute resolution by admin,
re-verification workflows, and historical audit trail preservation.
"""

import json
import pytest
from contracts.models import ClaimStatus, DisputeStatus, ConsensusStatus, Verdict
from contracts.validation import compute_sha256


def test_open_dispute_on_verified_claim(
    proof_guard, vm, bob, charlie, sample_claim_data, sample_evidence_url, sample_evidence_content
):
    """
    Verifies that a third party (Charlie) can open a dispute against
    a finalized verification outcome.
    """
    vm.register_web(sample_evidence_url, sample_evidence_content)

    # 1. Bob creates and verifies claim
    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )
        proof_guard.add_evidence(
            claim_id=cid,
            source_url=sample_evidence_url,
            content_hash=compute_sha256(sample_evidence_content),
        )
        verif = proof_guard.verify_claim(cid)

    assert verif["consensus_status"] == ConsensusStatus.ACCEPTED.value

    # 2. Charlie opens dispute
    with vm.prank(charlie):
        disp_reason = "The cited URL was updated yesterday with conflicting corrections."
        disp_id = proof_guard.open_dispute(claim_id=cid, reason=disp_reason)

    assert disp_id == f"disp_{cid}_1"

    # 3. Verify dispute record
    disp = proof_guard.get_dispute(disp_id)
    assert disp["dispute_id"] == disp_id
    assert disp["claim_id"] == cid
    assert disp["challenger"] == charlie
    assert disp["reason"] == disp_reason
    assert disp["status"] == DisputeStatus.OPEN.value

    # 4. Verify claim status transitioned to DISPUTED
    claim = proof_guard.get_claim(cid)
    assert claim["status"] == ClaimStatus.DISPUTED.value
    assert claim["dispute_history"] == [disp_id]

    # 5. Verify previous verification record consensus_status is now DISPUTED
    old_verif = json.loads(proof_guard.verifications[verif["verification_id"]])
    assert old_verif["consensus_status"] == ConsensusStatus.DISPUTED.value


def test_reject_dispute_on_unverified_claim(proof_guard, vm, bob, charlie, sample_claim_data):
    """Ensures a SUBMITTED claim that has not yet been verified cannot be disputed."""
    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )

    with vm.prank(charlie):
        with pytest.raises(ValueError, match="Cannot dispute claim in status 'SUBMITTED'"):
            proof_guard.open_dispute(
                claim_id=cid,
                reason="Premature dispute attempt.",
            )


def test_reject_dispute_with_empty_or_short_reason(
    proof_guard, vm, bob, charlie, sample_claim_data, sample_evidence_url, sample_evidence_content
):
    """Ensures dispute reasons must satisfy minimum length requirements."""
    vm.register_web(sample_evidence_url, sample_evidence_content)

    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )
        proof_guard.add_evidence(
            claim_id=cid,
            source_url=sample_evidence_url,
            content_hash=compute_sha256(sample_evidence_content),
        )
        proof_guard.verify_claim(cid)

    with vm.prank(charlie):
        with pytest.raises(ValueError, match="at least 5 characters"):
            proof_guard.open_dispute(claim_id=cid, reason="bad")


def test_resolve_dispute_by_owner_and_reverify(
    proof_guard, vm, alice, bob, charlie, sample_claim_data, sample_evidence_url, sample_evidence_content
):
    """
    Tests end-to-end dispute resolution:
    1. Claim is verified.
    2. Dispute is opened by Charlie.
    3. Alice (Contract Owner) resolves dispute with resolution notes.
    4. New evidence is added.
    5. Re-verification succeeds, preserving audit history of both attempts.
    """
    vm.register_web(sample_evidence_url, sample_evidence_content)

    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )
        proof_guard.add_evidence(
            claim_id=cid,
            source_url=sample_evidence_url,
            content_hash=compute_sha256(sample_evidence_content),
        )
        v1 = proof_guard.verify_claim(cid)

    with vm.prank(charlie):
        disp_id = proof_guard.open_dispute(
            claim_id=cid,
            reason="Additional corroborating source needed from peer-reviewed paper.",
        )

    # Alice (Owner) resolves dispute
    with vm.prank(alice):
        res = proof_guard.resolve_dispute(
            claim_id=cid,
            dispute_id=disp_id,
            resolution_notes="Approved for re-evaluation with updated secondary evidence.",
        )

    assert res["status"] == DisputeStatus.RESOLVED.value
    assert res["resolved_by"] == alice

    claim_after_resolve = proof_guard.get_claim(cid)
    assert claim_after_resolve["status"] == ClaimStatus.PENDING_VERIFICATION.value

    # Bob adds secondary evidence
    sec_url = "https://nature.com/articles/alphagenome-v2"
    sec_content = "Nature Biotechnology article verifying AlphaGenome v2 performance."
    vm.register_web(sec_url, sec_content)

    with vm.prank(bob):
        proof_guard.add_evidence(
            claim_id=cid,
            source_url=sec_url,
            content_hash=compute_sha256(sec_content),
        )
        v2 = proof_guard.verify_claim(cid)

    assert v2["verification_id"] == f"verif_{cid}_2"
    assert v2["verdict"] == Verdict.VERIFIED.value

    # Check complete historical audit trail
    history = proof_guard.get_claim_history(cid)
    assert len(history) == 2
    assert history[0]["verification_id"] == v1["verification_id"]
    assert history[0]["consensus_status"] == ConsensusStatus.DISPUTED.value
    assert history[1]["verification_id"] == v2["verification_id"]
    assert history[1]["consensus_status"] == ConsensusStatus.ACCEPTED.value


def test_reject_unauthorized_dispute_resolution(
    proof_guard, vm, bob, charlie, attacker, sample_claim_data, sample_evidence_url, sample_evidence_content
):
    """Ensures unauthorized accounts cannot resolve disputes."""
    vm.register_web(sample_evidence_url, sample_evidence_content)

    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )
        proof_guard.add_evidence(
            claim_id=cid,
            source_url=sample_evidence_url,
            content_hash=compute_sha256(sample_evidence_content),
        )
        proof_guard.verify_claim(cid)

    with vm.prank(charlie):
        disp_id = proof_guard.open_dispute(claim_id=cid, reason="Legitimate challenge.")

    # Attacker tries to resolve dispute
    with vm.prank(attacker):
        with pytest.raises(ValueError, match="Unauthorized: only the contract owner"):
            proof_guard.resolve_dispute(
                claim_id=cid,
                dispute_id=disp_id,
                resolution_notes="Malicious dismissal.",
            )
