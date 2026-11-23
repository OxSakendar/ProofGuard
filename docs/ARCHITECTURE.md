# ProofGuard Architecture Specification

ProofGuard is a decentralized evidence verification Intelligent Contract built on the **GenLayer blockchain**. It enables trustless, automated, and dispute-resilient verification of real-world claims against external web evidence using GenLayer's GenVM, multi-validator committee execution, and the Equivalence Principle.

---

## 1. System Overview

Traditional smart contracts (e.g. EVM) are strictly deterministic and isolated from external internet data. They rely on centralized oracles, multi-sig bridges, or rigid API feeds that cannot interpret subjective language, unstructured HTML, scientific papers, or regulatory filings.

ProofGuard leverages GenLayer's native **GenVM (Python-based WebAssembly virtual machine)**, which natively supports:
- **Non-deterministic web data retrieval** (`gl.nondet.web.render` / `gl.nondet.web.get`).
- **Decentralized LLM inference** (`gl.nondet.exec_prompt`).
- **Optimistic Democracy & Equivalence Principle** (`gl.eq_principle.prompt_comparative`), allowing independent validator nodes to reach consensus on semantic intent rather than superficial byte matches.

```
+-----------------------------------------------------------------------------------+
|                                 PROOFGUARD SYSTEM                                 |
+-----------------------------------------------------------------------------------+
                                          |
                +-------------------------+-------------------------+
                |                                                   |
                v                                                   v
      [ Deterministic Layer ]                             [ Non-Deterministic Layer ]
   - State Storage (TreeMap)                            - External Web Retrieval (gl.nondet.web)
   - Lifecycle State Machine                            - Adversarial Sanitization & Framing
   - Access Control & Authorization                     - Local LLM Evaluation (gl.nondet.exec_prompt)
   - Dispute Management & Audit Trails                  - Equivalence Principle (gl.eq_principle)
```

---

## 2. Core Entities & State Models

### 2.1 Claim
Represents an assertion submitted to the registry.
- `claim_id` (`str`): Unique identifier (`claim_1`, `claim_2`, ...).
- `creator` (`str`): Sender address who registered the claim.
- `title` (`str`): Summary title (3 to 200 characters).
- `description` (`str`): Complete factual assertion (10 to 4000 characters).
- `criteria` (`str`): Explicit objective verification requirements (10 to 2000 characters).
- `evidence_sources` (`List[str]`): List of registered evidence IDs.
- `status` (`ClaimStatus`): Current lifecycle state.
- `current_verification_id` (`Optional[str]`): Pointer to active verification.
- `verification_history` (`List[str]`): Chronological record of all verification attempts.
- `dispute_history` (`List[str]`): Chronological record of all disputes.

### 2.2 Evidence
Represents an external evidence source registered for a specific claim.
- `evidence_id` (`str`): Unique identifier (`claim_1_ev_1`).
- `claim_id` (`str`): Associated claim ID.
- `source_url` (`str`): Verified HTTPS URL.
- `content_hash` (`str`): SHA-256 hash of expected or fetched evidence content.
- `source_version` (`str`): Version or date tag of the source.
- `submitter` (`str`): Address registering the evidence.

### 2.3 Verification
Represents the result of an intelligent verification attempt validated by consensus.
- `verification_id` (`str`): Unique identifier (`verif_claim_1_1`).
- `claim_id` (`str`): Associated claim ID.
- `verdict` (`str`): `VERIFIED`, `REJECTED`, or `INCONCLUSIVE`.
- `evidence_ids` (`List[str]`): Evidence sources cited in the decision.
- `supporting_facts` (`List[str]`): Key factual propositions supporting the verdict.
- `contradictions` (`List[str]`): Inconsistencies or counter-evidence found.
- `explanation` (`str`): Concise natural-language justification.
- `consensus_status` (`ConsensusStatus`): `ACCEPTED`, `DISPUTED`, or `SUPERSEDED`.
- `proposer` (`str`): Leader node or submitter.

### 2.4 Dispute
Represents a formal challenge to a verification result.
- `dispute_id` (`str`): Unique identifier (`disp_claim_1_1`).
- `claim_id` (`str`): Associated claim ID.
- `challenger` (`str`): Address submitting the dispute.
- `reason` (`str`): Factual or methodological reason for challenging the verdict.
- `status` (`DisputeStatus`): `OPEN`, `RESOLVED`, or `DISMISSED`.
- `resolution` (`str`): Administrative or consensus resolution statement.

---

## 3. State Machine & Lifecycle

```
    [SUBMITTED]
         |
         | (add_evidence)
         v
    [SUBMITTED / PENDING] 
         |
         | (verify_claim) ---> [Non-deterministic Committee Execution]
         v                                       |
    +----+----+                                  | (Consensus Reached)
    |         |                                  v
[VERIFIED] [REJECTED] [INCONCLUSIVE] <-----------+
    |         |         |
    +----+----+----+----+
         |
         | (open_dispute)
         v
     [DISPUTED]
         |
         | (resolve_dispute)
         v
[PENDING_VERIFICATION] ---> (Re-verify with new/updated evidence)
```

1. **Submission**: A user submits a claim with explicit criteria. Initial status is `SUBMITTED`.
2. **Evidence Attachment**: One or more HTTPS evidence sources are attached with SHA-256 content hashes. Duplicate URLs and duplicate hashes are rejected.
3. **Intelligent Verification**: Invoking `verify_claim()` initiates non-deterministic consensus. The leader and validator committee independently fetch web evidence, prompt their LLMs, and validate substantive equivalence.
4. **Finalization**: The consensus verdict updates the claim status to `VERIFIED`, `REJECTED`, or `INCONCLUSIVE`. The verification record is stored immutably.
5. **Dispute**: Any eligible user can challenge the outcome by calling `open_dispute()`. The previous verification's `consensus_status` transitions to `DISPUTED`, and the claim transitions to `DISPUTED`.
6. **Resolution & Re-verification**: The governance/owner resolves the dispute via `resolve_dispute()`, shifting the claim back to `PENDING_VERIFICATION` so that updated evidence can be added and a new verification round executed, preserving the complete audit history.
