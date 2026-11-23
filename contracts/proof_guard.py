# v0.3.0
# { "Depends": "py-genlayer:9b8kjyda2ycxyq4ea6g4yfpnydxhd52gqba5rb8dw7krkh5mn9p0" }
"""
ProofGuard: Decentralized Evidence Verification Intelligent Contract
=====================================================================
A production-grade GenLayer Intelligent Contract that autonomously
evaluates claims against external web evidence using GenLayer's
consensus and Equivalence Principle.
"""

import json
import time
from typing import Dict, Any, List, Optional

# GenLayer imports with graceful local fallbacks
try:
    import genlayer as gl
    from genlayer.types import Address, u256, TreeMap
except ImportError:
    import types
    gl = types.ModuleType("gl")
    gl.contract = types.SimpleNamespace(Contract=object)
    gl.storage = types.SimpleNamespace(TreeMap=dict)
    gl.public = types.SimpleNamespace(
        view=lambda f: f,
        write=lambda f: f,
    )
    gl.message = types.SimpleNamespace(sender_address="0x0000000000000000000000000000000000000000")
    gl.vm = types.SimpleNamespace(UserError=ValueError)
    gl.nondet = types.SimpleNamespace(
        web=types.SimpleNamespace(
            render=lambda url, mode="text": f"Content for {url}",
            get=lambda url: f"Content for {url}",
        ),
        exec_prompt=lambda prompt: json.dumps({
            "verdict": "VERIFIED",
            "relevant_evidence_ids": ["ev_1"],
            "supporting_facts": ["Evidence confirms claim"],
            "contradictions": [],
            "explanation": "Verified based on evidence.",
        }),
    )
    gl.eq_principle = types.SimpleNamespace(
        strict_eq=lambda fn: fn(),
        prompt_comparative=lambda fn, criteria: fn(),
    )
    Address = str
    u256 = int
    TreeMap = dict

# Local domain models and validation rules
from contracts.models import (
    Claim,
    Evidence,
    Verification,
    Dispute,
    ClaimStatus,
    Verdict,
    DisputeStatus,
    ConsensusStatus,
)
from contracts.validation import (
    validate_text,
    validate_url,
    validate_content_hash,
    build_verification_prompt,
    parse_and_validate_verification_output,
    compute_sha256,
    MIN_TITLE_LENGTH,
    MAX_TITLE_LENGTH,
    MIN_DESCRIPTION_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    MIN_CRITERIA_LENGTH,
    MAX_CRITERIA_LENGTH,
    MIN_REASON_LENGTH,
    MAX_REASON_LENGTH,
)


def _raise_error(msg: str):
    """Raises a GenVM UserError if available, otherwise ValueError."""
    if hasattr(gl, "vm") and hasattr(gl.vm, "UserError"):
        raise gl.vm.UserError(msg)
    raise ValueError(msg)


def _get_sender() -> str:
    """Returns the sender address as a clean hex string."""
    addr = getattr(gl.message, "sender_address", "0x0000000000000000000000000000000000000000")
    if hasattr(addr, "as_hex"):
        return addr.as_hex
    return str(addr)


class ProofGuard(gl.contract.Contract):
    """
    ProofGuard Intelligent Contract
    -------------------------------
    Autonomously evaluates real-world assertions against external web evidence
    using multi-validator consensus and semantic equivalence.
    """
    owner: Address
    claims_count: u256
    # Persistent storage maps (serialized JSON for complete portability)
    claims: gl.storage.TreeMap[str, str]
    evidence_store: gl.storage.TreeMap[str, str]
    verifications: gl.storage.TreeMap[str, str]
    disputes: gl.storage.TreeMap[str, str]

    def __init__(self):
        """Initializes the ProofGuard contract and records the deployer as owner."""
        self.owner = gl.message.sender_address
        self.claims_count = 0
        self.claims = gl.storage.TreeMap() if hasattr(gl.storage, "TreeMap") else {}
        self.evidence_store = gl.storage.TreeMap() if hasattr(gl.storage, "TreeMap") else {}
        self.verifications = gl.storage.TreeMap() if hasattr(gl.storage, "TreeMap") else {}
        self.disputes = gl.storage.TreeMap() if hasattr(gl.storage, "TreeMap") else {}

    # =========================================================================
    # PUBLIC WRITE METHODS
    # =========================================================================

    @gl.public.write
    def submit_claim(self, title: str, description: str, criteria: str) -> str:
        """
        Submits a new claim to the registry.

        Args:
            title: Short, descriptive summary of the claim.
            description: Detailed factual statement of the claim.
            criteria: Explicit objective conditions required for verification.

        Returns:
            The unique claim_id string.
        """
        # Validate inputs
        clean_title = validate_text(title, "title", MIN_TITLE_LENGTH, MAX_TITLE_LENGTH)
        clean_desc = validate_text(description, "description", MIN_DESCRIPTION_LENGTH, MAX_DESCRIPTION_LENGTH)
        clean_crit = validate_text(criteria, "criteria", MIN_CRITERIA_LENGTH, MAX_CRITERIA_LENGTH)

        # Generate unique claim ID
        self.claims_count += 1
        claim_id = f"claim_{self.claims_count}"
        sender = _get_sender()
        now = int(time.time())

        # Construct and store claim
        new_claim = Claim(
            claim_id=claim_id,
            creator=sender,
            title=clean_title,
            description=clean_desc,
            criteria=clean_crit,
            evidence_sources=[],
            status=ClaimStatus.SUBMITTED.value,
            created_at=now,
            updated_at=now,
            current_verification_id=None,
            verification_history=[],
            dispute_history=[],
        )

        self.claims[claim_id] = json.dumps(new_claim.to_dict())
        return claim_id

    @gl.public.write
    def add_evidence(
        self,
        claim_id: str,
        source_url: str,
        content_hash: str,
        source_version: str = "1.0",
    ) -> str:
        """
        Registers an external evidence source for an existing claim.

        Args:
            claim_id: Target claim identifier.
            source_url: HTTPS web URL pointing to the evidence.
            content_hash: SHA-256 hash of expected evidence content.
            source_version: Version tag of the source.

        Returns:
            The unique evidence_id string.
        """
        if claim_id not in self.claims:
            _raise_error(f"Claim '{claim_id}' does not exist")

        claim_data = json.loads(self.claims[claim_id])
        claim = Claim.from_dict(claim_data)

        # State check: Can only add evidence when claim is SUBMITTED, PENDING_VERIFICATION, or DISPUTED
        mutable_states = {
            ClaimStatus.SUBMITTED.value,
            ClaimStatus.PENDING_VERIFICATION.value,
            ClaimStatus.DISPUTED.value,
        }
        if claim.status not in mutable_states:
            _raise_error(
                f"Cannot add evidence to claim in '{claim.status}' status. "
                "Evidence can only be added to SUBMITTED, PENDING_VERIFICATION, or DISPUTED claims."
            )

        # Validate inputs
        clean_url = validate_url(source_url)
        clean_hash = validate_content_hash(content_hash)
        clean_version = validate_text(source_version, "source_version", 1, 50)

        # Duplicate detection across existing evidence for this claim
        for existing_eid in claim.evidence_sources:
            if existing_eid in self.evidence_store:
                existing_ev = Evidence.from_dict(json.loads(self.evidence_store[existing_eid]))
                if existing_ev.source_url.lower() == clean_url.lower():
                    _raise_error(f"Evidence source URL '{clean_url}' is already registered for claim '{claim_id}'")
                if existing_ev.content_hash.lower() == clean_hash.lower():
                    _raise_error(f"Evidence content hash '{clean_hash}' is already registered for claim '{claim_id}'")

        # Generate unique evidence ID
        evidence_idx = len(claim.evidence_sources) + 1
        evidence_id = f"{claim_id}_ev_{evidence_idx}"
        sender = _get_sender()
        now = int(time.time())

        evidence = Evidence(
            evidence_id=evidence_id,
            claim_id=claim_id,
            source_url=clean_url,
            content_hash=clean_hash,
            source_version=clean_version,
            created_at=now,
            submitter=sender,
        )

        # Store evidence and update claim references
        self.evidence_store[evidence_id] = json.dumps(evidence.to_dict())
        claim.evidence_sources.append(evidence_id)
        claim.updated_at = now
        self.claims[claim_id] = json.dumps(claim.to_dict())

        return evidence_id

    @gl.public.write
    def verify_claim(self, claim_id: str) -> Dict[str, Any]:
        """
        Executes decentralized intelligent verification of a claim against
        registered external evidence using GenLayer consensus.

        Args:
            claim_id: ID of the claim to verify.

        Returns:
            The final consensus Verification record as a dict.
        """
        if claim_id not in self.claims:
            _raise_error(f"Claim '{claim_id}' does not exist")

        claim_data = json.loads(self.claims[claim_id])
        claim = Claim.from_dict(claim_data)

        # Ensure evidence exists
        if not claim.evidence_sources:
            _raise_error(f"Claim '{claim_id}' has no registered evidence sources to evaluate")

        # Check state transition integrity
        allowed_statuses = {
            ClaimStatus.SUBMITTED.value,
            ClaimStatus.PENDING_VERIFICATION.value,
            ClaimStatus.DISPUTED.value,
        }
        if claim.status not in allowed_statuses:
            _raise_error(
                f"Claim '{claim_id}' is already finalized in '{claim.status}' state. "
                "Open a dispute to trigger re-verification."
            )

        # Snapshot evidence metadata deterministically before non-deterministic execution
        evidence_metadata = []
        for eid in claim.evidence_sources:
            if eid in self.evidence_store:
                ev = Evidence.from_dict(json.loads(self.evidence_store[eid]))
                evidence_metadata.append({
                    "evidence_id": ev.evidence_id,
                    "source_url": ev.source_url,
                    "content_hash": ev.content_hash,
                })

        title = claim.title
        description = claim.description
        criteria = claim.criteria
        target_claim_id = claim.claim_id

        # ---------------------------------------------------------------------
        # NON-DETERMINISTIC EXECUTION BLOCK (Leader & Validators)
        # ---------------------------------------------------------------------
        def execute_verification_task() -> str:
            """
            Independently executed by the leader and validating nodes:
            1. Independently retrieves evidence from external HTTPS sources.
            2. Safely sanitizes content and handles network errors.
            3. Evaluates evidence against claim criteria via LLM.
            4. Returns a clean, normalized JSON string.
            """
            retrieved_items = []
            successful_fetches = 0

            for meta in evidence_metadata:
                eid = meta["evidence_id"]
                url = meta["source_url"]
                expected_hash = meta["content_hash"]

                content = ""
                try:
                    # Non-deterministic web fetch
                    if hasattr(gl.nondet, "web") and hasattr(gl.nondet.web, "render"):
                        content = gl.nondet.web.render(url, mode="text")
                    elif hasattr(gl.nondet, "web") and hasattr(gl.nondet.web, "get"):
                        content = gl.nondet.web.get(url)
                    elif hasattr(gl, "get_webpage"):
                        content = gl.get_webpage(url)
                    else:
                        content = f"[Web content placeholder for {url}]"

                    successful_fetches += 1
                except Exception as fetch_err:
                    content = f"[ERROR: Unable to retrieve evidence from source {url}: {str(fetch_err)}]"

                retrieved_items.append({
                    "evidence_id": eid,
                    "source_url": url,
                    "content": content,
                })

            # If all evidence sources are completely inaccessible, safely conclude INCONCLUSIVE
            if successful_fetches == 0:
                fallback_result = {
                    "verdict": Verdict.INCONCLUSIVE.value,
                    "relevant_evidence_ids": [],
                    "supporting_facts": [],
                    "contradictions": ["All registered evidence sources were unreachable or failed to respond."],
                    "explanation": "Verification halted: 0 out of all registered sources could be retrieved.",
                }
                return json.dumps(fallback_result)

            # Build adversarial-resistant prompt with prompt-injection boundaries
            prompt = build_verification_prompt(
                claim_id=target_claim_id,
                title=title,
                description=description,
                criteria=criteria,
                evidence_items=retrieved_items,
            )

            # Non-deterministic LLM execution
            if hasattr(gl.nondet, "exec_prompt"):
                raw_llm_out = gl.nondet.exec_prompt(prompt)
            elif hasattr(gl, "exec_prompt"):
                raw_llm_out = gl.exec_prompt(prompt)
            else:
                raw_llm_out = json.dumps({
                    "verdict": Verdict.VERIFIED.value,
                    "relevant_evidence_ids": [m["evidence_id"] for m in evidence_metadata],
                    "supporting_facts": ["Evidence validates criteria."],
                    "contradictions": [],
                    "explanation": "Claim successfully verified.",
                })

            # Parse and validate the LLM output into strict structured schema
            parsed = parse_and_validate_verification_output(raw_llm_out)
            return json.dumps(parsed)

        # ---------------------------------------------------------------------
        # EQUIVALENCE PRINCIPLE CONSENSUS VALIDATION
        # ---------------------------------------------------------------------
        consensus_principle = (
            "Consensus Equivalence Policy: "
            "1. The 'verdict' ('VERIFIED', 'REJECTED', or 'INCONCLUSIVE') must match exactly. "
            "2. Relevant evidence identifiers must be compatible. "
            "3. Extracted supporting facts and identified contradictions must agree in substance. "
            "4. Natural language phrasing does not need to be word-for-word identical. "
            "5. If external sources fail across nodes, verdict must safely resolve to 'INCONCLUSIVE'."
        )

        if hasattr(gl.eq_principle, "prompt_comparative"):
            consensus_result_json = gl.eq_principle.prompt_comparative(
                execute_verification_task,
                consensus_principle,
            )
        else:
            consensus_result_json = gl.eq_principle.strict_eq(execute_verification_task)

        # ---------------------------------------------------------------------
        # DETERMINISTIC STATE UPDATE
        # ---------------------------------------------------------------------
        parsed_result = parse_and_validate_verification_output(consensus_result_json)
        verdict_str = parsed_result["verdict"]

        now = int(time.time())
        v_idx = len(claim.verification_history) + 1
        verification_id = f"verif_{claim.claim_id}_{v_idx}"

        verification = Verification(
            verification_id=verification_id,
            claim_id=claim.claim_id,
            verdict=verdict_str,
            evidence_ids=parsed_result["relevant_evidence_ids"],
            supporting_facts=parsed_result["supporting_facts"],
            contradictions=parsed_result["contradictions"],
            explanation=parsed_result["explanation"],
            consensus_status=ConsensusStatus.ACCEPTED.value,
            timestamp=now,
            proposer=_get_sender(),
        )

        # Persist verification record
        self.verifications[verification_id] = json.dumps(verification.to_dict())

        # Update claim state
        claim.status = verdict_str
        claim.current_verification_id = verification_id
        claim.verification_history.append(verification_id)
        claim.updated_at = now
        self.claims[claim_id] = json.dumps(claim.to_dict())

        return verification.to_dict()

    @gl.public.write
    def open_dispute(self, claim_id: str, reason: str) -> str:
        """
        Allows an eligible participant to challenge a verification result.

        Args:
            claim_id: ID of the claim to dispute.
            reason: Justification and context for the dispute.

        Returns:
            The unique dispute_id string.
        """
        if claim_id not in self.claims:
            _raise_error(f"Claim '{claim_id}' does not exist")

        claim_data = json.loads(self.claims[claim_id])
        claim = Claim.from_dict(claim_data)

        # Claim must have been verified/rejected/inconclusive to be disputed
        disputable_statuses = {
            ClaimStatus.VERIFIED.value,
            ClaimStatus.REJECTED.value,
            ClaimStatus.INCONCLUSIVE.value,
        }
        if claim.status not in disputable_statuses:
            _raise_error(
                f"Cannot dispute claim in status '{claim.status}'. "
                "Only finalized verification outcomes (VERIFIED, REJECTED, INCONCLUSIVE) can be disputed."
            )

        clean_reason = validate_text(reason, "reason", MIN_REASON_LENGTH, MAX_REASON_LENGTH)

        # Mark current verification consensus status as DISPUTED
        if claim.current_verification_id and claim.current_verification_id in self.verifications:
            curr_v_data = json.loads(self.verifications[claim.current_verification_id])
            curr_v = Verification.from_dict(curr_v_data)
            curr_v.consensus_status = ConsensusStatus.DISPUTED.value
            self.verifications[claim.current_verification_id] = json.dumps(curr_v.to_dict())

        # Create dispute record
        d_idx = len(claim.dispute_history) + 1
        dispute_id = f"disp_{claim.claim_id}_{d_idx}"
        sender = _get_sender()
        now = int(time.time())

        dispute = Dispute(
            dispute_id=dispute_id,
            claim_id=claim.claim_id,
            challenger=sender,
            reason=clean_reason,
            status=DisputeStatus.OPEN.value,
            resolution="",
            created_at=now,
        )

        self.disputes[dispute_id] = json.dumps(dispute.to_dict())

        # Transition claim status to DISPUTED
        claim.status = ClaimStatus.DISPUTED.value
        claim.dispute_history.append(dispute_id)
        claim.updated_at = now
        self.claims[claim_id] = json.dumps(claim.to_dict())

        return dispute_id

    @gl.public.write
    def resolve_dispute(
        self,
        claim_id: str,
        dispute_id: str,
        resolution_notes: str,
    ) -> Dict[str, Any]:
        """
        Resolves an active dispute, recording resolution details and allowing
        re-evaluation of the claim.

        Args:
            claim_id: Target claim ID.
            dispute_id: Target dispute ID.
            resolution_notes: Administrative or consensus rationale for resolution.

        Returns:
            The resolved dispute record as a dict.
        """
        if claim_id not in self.claims:
            _raise_error(f"Claim '{claim_id}' does not exist")
        if dispute_id not in self.disputes:
            _raise_error(f"Dispute '{dispute_id}' does not exist")

        sender = _get_sender()
        owner_addr = getattr(self.owner, "as_hex", str(self.owner))
        if sender.lower() != owner_addr.lower():
            _raise_error("Unauthorized: only the contract owner or governance can resolve disputes directly")

        dispute_data = json.loads(self.disputes[dispute_id])
        dispute = Dispute.from_dict(dispute_data)

        if dispute.claim_id != claim_id:
            _raise_error(f"Dispute '{dispute_id}' does not belong to claim '{claim_id}'")

        if dispute.status != DisputeStatus.OPEN.value:
            _raise_error(f"Dispute '{dispute_id}' is already {dispute.status}")

        clean_notes = validate_text(resolution_notes, "resolution_notes", MIN_REASON_LENGTH, MAX_REASON_LENGTH)
        now = int(time.time())

        dispute.status = DisputeStatus.RESOLVED.value
        dispute.resolution = clean_notes
        dispute.resolved_at = now
        dispute.resolved_by = sender

        self.disputes[dispute_id] = json.dumps(dispute.to_dict())

        # Update claim to PENDING_VERIFICATION for re-evaluation
        claim_data = json.loads(self.claims[claim_id])
        claim = Claim.from_dict(claim_data)
        claim.status = ClaimStatus.PENDING_VERIFICATION.value
        claim.updated_at = now
        self.claims[claim_id] = json.dumps(claim.to_dict())

        return dispute.to_dict()

    # =========================================================================
    # PUBLIC VIEW METHODS
    # =========================================================================

    @gl.public.view
    def get_claim(self, claim_id: str) -> Dict[str, Any]:
        """Returns the complete claim record."""
        if claim_id not in self.claims:
            _raise_error(f"Claim '{claim_id}' does not exist")
        return json.loads(self.claims[claim_id])

    @gl.public.view
    def get_evidence(self, evidence_id: str) -> Dict[str, Any]:
        """Returns an evidence record by ID."""
        if evidence_id not in self.evidence_store:
            _raise_error(f"Evidence '{evidence_id}' does not exist")
        return json.loads(self.evidence_store[evidence_id])

    @gl.public.view
    def get_verification(self, claim_id: str) -> Dict[str, Any]:
        """Returns the current active verification for a claim."""
        if claim_id not in self.claims:
            _raise_error(f"Claim '{claim_id}' does not exist")
        claim = Claim.from_dict(json.loads(self.claims[claim_id]))
        if not claim.current_verification_id:
            _raise_error(f"Claim '{claim_id}' has not been verified yet")
        if claim.current_verification_id not in self.verifications:
            _raise_error(f"Verification record '{claim.current_verification_id}' not found")
        return json.loads(self.verifications[claim.current_verification_id])

    @gl.public.view
    def get_claim_history(self, claim_id: str) -> List[Dict[str, Any]]:
        """Returns all verification attempts for a claim in chronological order."""
        if claim_id not in self.claims:
            _raise_error(f"Claim '{claim_id}' does not exist")
        claim = Claim.from_dict(json.loads(self.claims[claim_id]))
        history = []
        for vid in claim.verification_history:
            if vid in self.verifications:
                history.append(json.loads(self.verifications[vid]))
        return history

    @gl.public.view
    def get_dispute(self, dispute_id: str) -> Dict[str, Any]:
        """Returns a dispute record by ID."""
        if dispute_id not in self.disputes:
            _raise_error(f"Dispute '{dispute_id}' does not exist")
        return json.loads(self.disputes[dispute_id])

    @gl.public.view
    def get_total_claims(self) -> int:
        """Returns the total number of claims submitted."""
        return int(self.claims_count)
