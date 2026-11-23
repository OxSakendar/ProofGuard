"""
ProofGuard Contract State Models
---------------------------------
Defines the core state models and data structures for the ProofGuard
Intelligent Contract on GenLayer.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

try:
    from genlayer import allow_storage
except ImportError:
    # Graceful fallback when executed outside the GenVM runtime
    def allow_storage(cls):
        return cls


class ClaimStatus(str, Enum):
    """Lifecycle states of a claim."""
    SUBMITTED = "SUBMITTED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    DISPUTED = "DISPUTED"


class Verdict(str, Enum):
    """Possible outcomes of an intelligent verification."""
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    INCONCLUSIVE = "INCONCLUSIVE"


class DisputeStatus(str, Enum):
    """Lifecycle states of a verification dispute."""
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class ConsensusStatus(str, Enum):
    """Consensus state of a verification record."""
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    DISPUTED = "DISPUTED"
    SUPERSEDED = "SUPERSEDED"


@allow_storage
@dataclass
class Evidence:
    """
    Represents an external evidence source registered for a claim.
    """
    evidence_id: str
    claim_id: str
    source_url: str
    content_hash: str
    source_version: str
    created_at: int
    submitter: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "claim_id": self.claim_id,
            "source_url": self.source_url,
            "content_hash": self.content_hash,
            "source_version": self.source_version,
            "created_at": self.created_at,
            "submitter": self.submitter,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Evidence":
        return cls(
            evidence_id=str(data["evidence_id"]),
            claim_id=str(data["claim_id"]),
            source_url=str(data["source_url"]),
            content_hash=str(data["content_hash"]),
            source_version=str(data["source_version"]),
            created_at=int(data.get("created_at", 0)),
            submitter=str(data.get("submitter", "")),
        )


@allow_storage
@dataclass
class Verification:
    """
    Represents the result of an intelligent verification attempt.
    """
    verification_id: str
    claim_id: str
    verdict: str  # Verdict enum value
    evidence_ids: List[str]
    supporting_facts: List[str]
    contradictions: List[str]
    explanation: str
    consensus_status: str  # ConsensusStatus enum value
    timestamp: int
    proposer: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verification_id": self.verification_id,
            "claim_id": self.claim_id,
            "verdict": self.verdict,
            "evidence_ids": list(self.evidence_ids),
            "supporting_facts": list(self.supporting_facts),
            "contradictions": list(self.contradictions),
            "explanation": self.explanation,
            "consensus_status": self.consensus_status,
            "timestamp": self.timestamp,
            "proposer": self.proposer,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Verification":
        return cls(
            verification_id=str(data["verification_id"]),
            claim_id=str(data["claim_id"]),
            verdict=str(data["verdict"]),
            evidence_ids=list(data.get("evidence_ids", [])),
            supporting_facts=list(data.get("supporting_facts", [])),
            contradictions=list(data.get("contradictions", [])),
            explanation=str(data.get("explanation", "")),
            consensus_status=str(data.get("consensus_status", ConsensusStatus.ACCEPTED.value)),
            timestamp=int(data.get("timestamp", 0)),
            proposer=str(data.get("proposer", "")),
        )


@allow_storage
@dataclass
class Dispute:
    """
    Represents a formal challenge to a verification outcome.
    """
    dispute_id: str
    claim_id: str
    challenger: str
    reason: str
    status: str  # DisputeStatus enum value
    resolution: str
    created_at: int
    resolved_at: int = 0
    resolved_by: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dispute_id": self.dispute_id,
            "claim_id": self.claim_id,
            "challenger": self.challenger,
            "reason": self.reason,
            "status": self.status,
            "resolution": self.resolution,
            "created_at": self.created_at,
            "resolved_at": self.resolved_at,
            "resolved_by": self.resolved_by,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Dispute":
        return cls(
            dispute_id=str(data["dispute_id"]),
            claim_id=str(data["claim_id"]),
            challenger=str(data["challenger"]),
            reason=str(data["reason"]),
            status=str(data.get("status", DisputeStatus.OPEN.value)),
            resolution=str(data.get("resolution", "")),
            created_at=int(data.get("created_at", 0)),
            resolved_at=int(data.get("resolved_at", 0)),
            resolved_by=str(data.get("resolved_by", "")),
        )


@allow_storage
@dataclass
class Claim:
    """
    Represents an assertion submitted for decentralized verification.
    """
    claim_id: str
    creator: str
    title: str
    description: str
    criteria: str
    evidence_sources: List[str] = field(default_factory=list)
    status: str = ClaimStatus.SUBMITTED.value
    created_at: int = 0
    updated_at: int = 0
    current_verification_id: Optional[str] = None
    verification_history: List[str] = field(default_factory=list)
    dispute_history: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "creator": self.creator,
            "title": self.title,
            "description": self.description,
            "criteria": self.criteria,
            "evidence_sources": list(self.evidence_sources),
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "current_verification_id": self.current_verification_id,
            "verification_history": list(self.verification_history),
            "dispute_history": list(self.dispute_history),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Claim":
        return cls(
            claim_id=str(data["claim_id"]),
            creator=str(data["creator"]),
            title=str(data["title"]),
            description=str(data["description"]),
            criteria=str(data["criteria"]),
            evidence_sources=list(data.get("evidence_sources", [])),
            status=str(data.get("status", ClaimStatus.SUBMITTED.value)),
            created_at=int(data.get("created_at", 0)),
            updated_at=int(data.get("updated_at", 0)),
            current_verification_id=data.get("current_verification_id"),
            verification_history=list(data.get("verification_history", [])),
            dispute_history=list(data.get("dispute_history", [])),
        )
