# ProofGuard: Decentralized Evidence Verification Intelligent Contract

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GenLayer GenVM](https://img.shields.io/badge/GenLayer-Intelligent%20Contract-8A2BE2.svg)](https://docs.genlayer.com)
[![Tests Passing](https://img.shields.io/badge/pytest-56%20passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**ProofGuard** is a production-minded GenLayer Intelligent Contract that independently evaluates real-world assertions against external web evidence using GenLayer's non-deterministic execution environment, multi-validator committee consensus, and the **Equivalence Principle**.

---

## 1. Problem Statement & Why GenLayer is Required

Traditional blockchains (Ethereum, Solana, etc.) face the **Oracle Trilemma** and are fundamentally unable to read unstructured internet data or perform semantic reasoning. Existing oracle networks (Chainlink, Pyth) are restricted to rigid numeric price feeds or rely on trusted centralized signers.

When real-world assertions involve complex conditions—such as verifying scientific publications, regulatory disclosures, news reports, product milestones, or supply chain certifications—deterministic smart contracts fail:
1. **Unstructured Data**: Web evidence arrives as dynamic HTML, natural-language press releases, or research papers.
2. **Subjectivity & Variations**: Live websites change timestamps and HTML layout; different LLM nodes phrase explanations differently.
3. **Decentralized Trust**: Relying on a single AI model or a single server re-introduces a central point of failure.

### The GenLayer Solution
GenLayer provides an environment where smart contracts are written in **Python** and executed inside **GenVM**. ProofGuard utilizes GenLayer's unique features:
- **Native Web Retrieval** (`gl.nondet.web.render` / `gl.nondet.web.get`): Nodes independently fetch live HTTPS web pages.
- **Embedded LLM Inference** (`gl.nondet.exec_prompt`): Nodes evaluate unstructured evidence directly inside contract logic.
- **Consensus via the Equivalence Principle** (`gl.eq_principle.prompt_comparative`): Committee validators do not require byte-for-byte identical textual outputs; instead, they reach consensus on **substantive decision fields** (verdict, cited evidence, supporting facts, absence of material contradictions).

---

## 2. Key Features

- **Claim Registry**: Create unique claims with explicit verification criteria, creator tracking, and lifecycle status.
- **Multi-Source Evidence Registry**: Attach multiple HTTPS evidence URLs, track SHA-256 content hashes and source versions, and reject duplicates.
- **Intelligent Autonomous Verification**: Independent web retrieval, anti-prompt-injection isolation, and LLM evaluation producing `VERIFIED`, `REJECTED`, or `INCONCLUSIVE` outcomes.
- **Multi-Validator Equivalence Consensus**: Validates that leader and committee nodes agree on verdict and factual findings, tolerating natural-language phrasing variations while catching material discrepancies.
- **Dispute Resolution & Re-Evaluation**: Open challenges against finalized claims, transition consensus status, resolve via governance, and re-verify with updated evidence.
- **Immutable Audit History**: Preserve all historical verification and dispute records on-chain.
- **Enterprise-Grade Security**: Built-in SSRF protection (blocking internal/private IPs), prompt-injection containment, payload size limits (100 KB max), and state machine guards.

---

## 3. Project Structure

```
ProofGuard/
├── contracts/
│   ├── proof_guard.py              # Modular Intelligent Contract
│   ├── proof_guard_standalone.py   # Consolidated single-file contract for Studio/Testnet
│   ├── models.py                   # Data models (Claim, Evidence, Verification, Dispute)
│   └── validation.py               # Security, SSRF checks, prompt isolation, equivalence
├── tests/
│   ├── conftest.py                 # Mock GenVM simulator, test accounts, web & LLM shims
│   ├── test_claims.py              # Claim submission & validation tests (16 tests)
│   ├── test_evidence.py            # Evidence registry, deduplication, hash tests (16 tests)
│   ├── test_consensus.py           # Verification, equivalence & disagreement tests (7 tests)
│   ├── test_disputes.py            # Dispute lifecycle & re-verification tests (5 tests)
│   └── test_security.py            # SSRF, prompt injection, and size limits (12 tests)
├── examples/
│   └── sample_claims.json          # Example claims for VERIFIED, REJECTED, INCONCLUSIVE, DISPUTED
├── docs/
│   ├── README.md                   # Documentation index
│   ├── ARCHITECTURE.md             # Architecture, state models, lifecycle state machine
│   ├── CONSENSUS.md                # Equivalence Principle, committee execution, fail-safes
│   ├── SECURITY.md                 # Threat model, SSRF defense, prompt injection containment
│   └── DEPLOYMENT.md               # GenLayer Studio & CLI deployment guide
├── scripts/
│   └── deploy.py                   # Python deployment script using genlayer-py
├── pytest.ini                      # Pytest configuration
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore file
└── README.md                       # Main documentation
```

---

## 4. Contract State Machine

```
    [SUBMITTED]
         │
         │ (add_evidence)
         ▼
    [SUBMITTED / PENDING] 
         │
         │ (verify_claim) ───► [Committee Web Fetch & LLM Evaluation]
         ▼                                   │
    ┌────┴────┐                              │ (Equivalence Principle Consensus)
    │         │                              ▼
[VERIFIED] [REJECTED] [INCONCLUSIVE] ◄───────┘
    │         │         │
    └────┬────┴────┬────┘
         │
         │ (open_dispute)
         ▼
     [DISPUTED]
         │
         │ (resolve_dispute)
         ▼
[PENDING_VERIFICATION] ───► (Re-evaluate with new evidence, full audit trail preserved)
```

---

## 5. Consensus & Equivalence Policy

When `verify_claim()` is invoked, committee nodes execute the task under `gl.eq_principle.prompt_comparative`:

```python
consensus_principle = (
    "Consensus Equivalence Policy: "
    "1. The 'verdict' ('VERIFIED', 'REJECTED', or 'INCONCLUSIVE') must match exactly. "
    "2. Relevant evidence identifiers must be compatible. "
    "3. Extracted supporting facts and identified contradictions must agree in substance. "
    "4. Natural language phrasing does not need to be word-for-word identical. "
    "5. If external sources fail across nodes, verdict must safely resolve to 'INCONCLUSIVE'."
)
```

### Equivalence Validation Matrix

| Field | Requirement | Tolerated Divergence |
|---|---|---|
| **Verdict** | Exact match (`VERIFIED`, `REJECTED`, or `INCONCLUSIVE`) | None. Mismatch triggers consensus rejection. |
| **Evidence IDs** | Substantial overlap across cited evidence sources | Order or minor supplementary citations. |
| **Supporting Facts** | Mutual compatibility; no contradictory assertions | Phrasing and sentence structure. |
| **Contradictions** | Neither node asserts facts that the other refutes | Minor nuance differences. |
| **Explanation** | Valid semantic summary | Wording, terminology, and length. |

---

## 6. Security & Hardening

ProofGuard implements an enterprise-grade defense-in-depth security model specifically tailored for Web3 AI and Intelligent Contracts:

1. **Strict Input Validation**:
   - Title bounded to 3–200 characters; Description bounded to 10–4,000 characters; Verification criteria bounded to 10–2,000 characters.
   - Dispute reasons strictly validated (5–1,000 characters) to prevent empty or spam challenges.

2. **SSRF Mitigation & Network Restrictions**:
   - Rejects non-HTTPS schemes (`http://`, `ftp://`, `file://`, `data:`).
   - Rejects local and loopback addresses (`localhost`, `127.0.0.1`, `0.0.0.0`, `[::1]`).
   - Rejects cloud metadata services (e.g., `169.254.169.254`, `metadata.google.internal`).
   - Blocks private IPv4 address subnets (`10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12`).

3. **Prompt Injection Containment**:
   - All untrusted web content is sanitized to neutralize delimiter breakouts (converting `<<<` to `<< <` and `>>>` to `> >>`).
   - External evidence is wrapped inside strict structural isolation tags:
     ```text
     <<<UNTRUSTED_EXTERNAL_EVIDENCE_START evidence_id="..." source_url="...">>>
     ...raw web content...
     <<<UNTRUSTED_EXTERNAL_EVIDENCE_END>>>
     ```
   - System prompts explicitly command the LLM to treat all text within delimiters as passive, untrusted factual data, strictly forbidding instruction overrides.

4. **Resource Exhaustion & Payload Limits**:
   - Hard 100 KB limit per evidence source (`MAX_EVIDENCE_SIZE_BYTES`).
   - Oversized text is truncated safely with a clear audit warning tag to prevent memory exhaustion and out-of-gas conditions.

5. **Model Response Sanitization & Schema Enforcement**:
   - Automated code-fence stripping (removes ` ```json ` and ` ``` `).
   - Strict schema validation for required fields: `verdict`, `relevant_evidence_ids`, `supporting_facts`, `contradictions`, and `explanation`.
   - Verdicts are strictly constrained to the allowed enum set (`VERIFIED`, `REJECTED`, `INCONCLUSIVE`).

6. **Anti-Duplicate Evidence Protection**:
   - Rejects duplicate evidence URLs for the same claim.
   - Rejects identical SHA-256 content hashes to prevent evidence pollution and gas griefing.

7. **State Machine Integrity & Anti-Replay**:
   - Evidence can only be attached while a claim is in `SUBMITTED`, `PENDING_VERIFICATION`, or `DISPUTED` status.
   - Finalized claims (`VERIFIED`, `REJECTED`, `INCONCLUSIVE`) cannot be re-finalized or re-verified without a formal dispute.

8. **Dispute Authorization & Governance Guards**:
   - Only eligible claims with a finalized outcome can be disputed.
   - Dispute resolution is strictly restricted to the contract owner or authorized governance addresses (`_get_sender() == owner`).

9. **Stale Evidence & Immutability Tracking**:
   - Every evidence item records a cryptographic SHA-256 hash, submitter address, timestamp, and source version tag.

10. **Zero On-Chain Secrets Policy**:
    - No private API keys, bearer tokens, or sensitive credentials are ever stored in contract state or required on-chain.

11. **Consensus Over AI Autonomy**:
    - A claim is **never accepted solely because a single AI model outputs it**. Multi-validator committee execution and the Equivalence Principle require independent re-execution and substantive agreement across independent nodes.

---

## 7. Testing Suite

The project includes **56 unit, integration, consensus, and security tests** executed with `pytest`:

```bash
# Install dependencies
pip install -r requirements.txt

# Run complete test suite
pytest -v
```

### Test Coverage Highlights
- `tests/test_claims.py`: Valid claim creation, invalid title/description/criteria bounds, non-existent claims, multi-claim ID increments.
- `tests/test_evidence.py`: Evidence registration, multi-source tracking, duplicate URL rejection, duplicate hash rejection, scheme validation, finalized state immutability.
- `tests/test_consensus.py`: Positive consensus validation, conflicting evidence refutation (`REJECTED`), dead source handling (`INCONCLUSIVE`), committee disagreement equivalence failure, malformed JSON recovery, substantive equivalence logic.
- `tests/test_disputes.py`: Dispute opening, unverified claim dispute rejection, dispute resolution by owner, unauthorized attacker rejection, full audit history preservation across multiple verification rounds.
- `tests/test_security.py`: SSRF defenses across 7 private address variants, prompt injection delimiter neutralization, structural prompt containment, 100 KB evidence truncation, repeated finalization prevention, markdown code fence stripping.

---

## 8. Deployment

### Quickstart: GenLayer Studio
1. Open [GenLayer Studio](https://studio.genlayer.com).
2. Create a new contract file named `proof_guard.py`.
3. Copy the contents of `contracts/proof_guard_standalone.py` into the editor.
4. Click **Deploy** to launch the contract on the simulated network.

### CLI Deployment via `scripts/deploy.py`
```bash
# Dry-run validation
python scripts/deploy.py --network testnet_bradbury --dry-run

# Live Testnet Deployment (requires funded account)
export GENLAYER_PRIVATE_KEY="0xYOUR_HEX_PRIVATE_KEY"
python scripts/deploy.py --network testnet_bradbury
```

---

## 9. License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
