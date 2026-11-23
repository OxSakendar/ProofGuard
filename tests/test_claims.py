"""
Unit and Integration Tests: Claim Lifecycle
===========================================
Tests valid claim creation, validation bounds, invalid rejections,
creator tracking, and registry counters.
"""

import pytest
from contracts.models import ClaimStatus


def test_submit_valid_claim(proof_guard, vm, bob, sample_claim_data):
    """Verifies that an authorized user can submit a valid claim."""
    with vm.prank(bob):
        claim_id = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )

    assert claim_id == "claim_1"
    assert proof_guard.get_total_claims() == 1

    claim = proof_guard.get_claim(claim_id)
    assert claim["claim_id"] == "claim_1"
    assert claim["creator"] == bob
    assert claim["title"] == sample_claim_data["title"]
    assert claim["description"] == sample_claim_data["description"]
    assert claim["criteria"] == sample_claim_data["criteria"]
    assert claim["status"] == ClaimStatus.SUBMITTED.value
    assert claim["evidence_sources"] == []
    assert claim["current_verification_id"] is None


def test_submit_multiple_claims(proof_guard, vm, bob, charlie, sample_claim_data):
    """Verifies that multiple distinct claims are assigned incrementing IDs."""
    with vm.prank(bob):
        cid1 = proof_guard.submit_claim(
            title="First Claim Title",
            description="First valid description statement.",
            criteria="First valid criteria condition.",
        )

    with vm.prank(charlie):
        cid2 = proof_guard.submit_claim(
            title="Second Claim Title",
            description="Second valid description statement.",
            criteria="Second valid criteria condition.",
        )

    assert cid1 == "claim_1"
    assert cid2 == "claim_2"
    assert proof_guard.get_total_claims() == 2

    c1 = proof_guard.get_claim(cid1)
    c2 = proof_guard.get_claim(cid2)
    assert c1["creator"] == bob
    assert c2["creator"] == charlie


@pytest.mark.parametrize(
    "invalid_title, expected_error",
    [
        ("", "at least 3 characters"),
        ("ab", "at least 3 characters"),
        ("A" * 201, "must not exceed 200"),
        (None, "must be a string"),
        (12345, "must be a string"),
    ],
)
def test_reject_invalid_title(proof_guard, vm, bob, invalid_title, expected_error):
    """Ensures claims with invalid titles are strictly rejected."""
    with vm.prank(bob):
        with pytest.raises(ValueError, match=expected_error):
            proof_guard.submit_claim(
                title=invalid_title,
                description="Valid claim description for testing.",
                criteria="Valid claim criteria for testing.",
            )


@pytest.mark.parametrize(
    "invalid_desc, expected_error",
    [
        ("", "at least 10 characters"),
        ("Too short", "at least 10 characters"),
        ("X" * 4001, "must not exceed 4000"),
        (None, "must be a string"),
    ],
)
def test_reject_invalid_description(proof_guard, vm, bob, invalid_desc, expected_error):
    """Ensures claims with invalid descriptions are strictly rejected."""
    with vm.prank(bob):
        with pytest.raises(ValueError, match=expected_error):
            proof_guard.submit_claim(
                title="Valid Claim Title",
                description=invalid_desc,
                criteria="Valid claim criteria for testing.",
            )


@pytest.mark.parametrize(
    "invalid_crit, expected_error",
    [
        ("", "at least 10 characters"),
        ("Short", "at least 10 characters"),
        ("Y" * 2001, "must not exceed 2000"),
        (None, "must be a string"),
    ],
)
def test_reject_invalid_criteria(proof_guard, vm, bob, invalid_crit, expected_error):
    """Ensures claims with invalid criteria are strictly rejected."""
    with vm.prank(bob):
        with pytest.raises(ValueError, match=expected_error):
            proof_guard.submit_claim(
                title="Valid Claim Title",
                description="Valid description for testing purposes.",
                criteria=invalid_crit,
            )


def test_get_nonexistent_claim(proof_guard):
    """Ensures querying an unknown claim raises a clean user error."""
    with pytest.raises(ValueError, match="Claim 'non_existent_id' does not exist"):
        proof_guard.get_claim("non_existent_id")
