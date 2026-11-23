"""
Unit and Integration Tests: Evidence Management
===============================================
Tests adding evidence, multiple sources, duplicate detection (URL & hash),
HTTPS validation, hash validation, and state immutability.
"""

import pytest
from contracts.validation import compute_sha256
from contracts.models import ClaimStatus


def test_add_valid_evidence(proof_guard, vm, bob, sample_claim_data):
    """Verifies that evidence can be attached to a submitted claim."""
    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )

        test_url = "https://example.com/press-release"
        test_hash = compute_sha256("Evidence text here")
        eid = proof_guard.add_evidence(
            claim_id=cid,
            source_url=test_url,
            content_hash=test_hash,
            source_version="1.0",
        )

    assert eid == f"{cid}_ev_1"

    ev = proof_guard.get_evidence(eid)
    assert ev["evidence_id"] == eid
    assert ev["claim_id"] == cid
    assert ev["source_url"] == test_url
    assert ev["content_hash"] == test_hash
    assert ev["source_version"] == "1.0"
    assert ev["submitter"] == bob

    claim = proof_guard.get_claim(cid)
    assert claim["evidence_sources"] == [eid]


def test_add_multiple_evidence_sources(proof_guard, vm, bob, sample_claim_data):
    """Verifies registering multiple distinct evidence sources."""
    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )

        eid1 = proof_guard.add_evidence(
            claim_id=cid,
            source_url="https://source1.example.org/article",
            content_hash=compute_sha256("source 1 content"),
        )
        eid2 = proof_guard.add_evidence(
            claim_id=cid,
            source_url="https://source2.example.org/publication",
            content_hash=compute_sha256("source 2 content"),
        )

    assert eid1 == f"{cid}_ev_1"
    assert eid2 == f"{cid}_ev_2"

    claim = proof_guard.get_claim(cid)
    assert len(claim["evidence_sources"]) == 2
    assert claim["evidence_sources"] == [eid1, eid2]


def test_reject_duplicate_url(proof_guard, vm, bob, sample_claim_data):
    """Ensures duplicate evidence URLs cannot be registered for the same claim."""
    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )

        url = "https://duplicate-source.example.com/item"
        proof_guard.add_evidence(
            claim_id=cid,
            source_url=url,
            content_hash=compute_sha256("First instance"),
        )

        with pytest.raises(ValueError, match="is already registered"):
            proof_guard.add_evidence(
                claim_id=cid,
                source_url=url,
                content_hash=compute_sha256("Second instance with different hash"),
            )


def test_reject_duplicate_content_hash(proof_guard, vm, bob, sample_claim_data):
    """Ensures duplicate evidence content hashes cannot be registered for the same claim."""
    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )

        shared_hash = compute_sha256("Identical payload")
        proof_guard.add_evidence(
            claim_id=cid,
            source_url="https://source-a.example.com/one",
            content_hash=shared_hash,
        )

        with pytest.raises(ValueError, match="is already registered"):
            proof_guard.add_evidence(
                claim_id=cid,
                source_url="https://source-b.example.com/different-url",
                content_hash=shared_hash,
            )


@pytest.mark.parametrize(
    "invalid_url, error_pattern",
    [
        ("http://insecure.example.com/doc", "strictly 'https'"),
        ("ftp://ftp.example.com/file", "strictly 'https'"),
        ("file:///etc/passwd", "strictly 'https'"),
        ("not-a-url", "strictly 'https'"),
        ("https://", "valid hostname"),
    ],
)
def test_reject_invalid_url_schemes(proof_guard, vm, bob, sample_claim_data, invalid_url, error_pattern):
    """Ensures non-HTTPS or malformed URLs are rejected."""
    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )

        with pytest.raises(ValueError, match=error_pattern):
            proof_guard.add_evidence(
                claim_id=cid,
                source_url=invalid_url,
                content_hash=compute_sha256("Valid content"),
            )


@pytest.mark.parametrize(
    "invalid_hash",
    [
        "not-a-hex",
        "12345",  # Too short
        "a" * 63,  # 63 chars
        "a" * 65,  # 65 chars
        "z" * 64,  # Invalid hex characters
    ],
)
def test_reject_invalid_content_hash(proof_guard, vm, bob, sample_claim_data, invalid_hash):
    """Ensures non-SHA256 hex strings are rejected."""
    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )

        with pytest.raises(ValueError, match="valid 64-character hex SHA-256"):
            proof_guard.add_evidence(
                claim_id=cid,
                source_url="https://valid.example.com",
                content_hash=invalid_hash,
            )


def test_reject_adding_evidence_to_nonexistent_claim(proof_guard, vm, bob):
    """Ensures adding evidence to an unknown claim raises an error."""
    with vm.prank(bob):
        with pytest.raises(ValueError, match="Claim 'unknown_id' does not exist"):
            proof_guard.add_evidence(
                claim_id="unknown_id",
                source_url="https://valid.example.com",
                content_hash=compute_sha256("Valid"),
            )


def test_reject_adding_evidence_to_finalized_claim(proof_guard, vm, bob, sample_claim_data):
    """Ensures evidence cannot be attached once a claim has been verified (immutable state)."""
    with vm.prank(bob):
        cid = proof_guard.submit_claim(
            title=sample_claim_data["title"],
            description=sample_claim_data["description"],
            criteria=sample_claim_data["criteria"],
        )
        proof_guard.add_evidence(
            claim_id=cid,
            source_url="https://source.example.com",
            content_hash=compute_sha256("Initial evidence"),
        )
        # Verify the claim
        proof_guard.verify_claim(cid)

        # Now claim is in VERIFIED status, adding more evidence must fail
        with pytest.raises(ValueError, match="Cannot add evidence to claim in 'VERIFIED' status"):
            proof_guard.add_evidence(
                claim_id=cid,
                source_url="https://new-source.example.com",
                content_hash=compute_sha256("Late evidence"),
            )
