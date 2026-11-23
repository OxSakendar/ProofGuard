# ProofGuard Documentation Index

Welcome to the technical documentation for **ProofGuard**, the Decentralized Evidence Verification Intelligent Contract built on GenLayer.

## Documentation Directory

1. [**Architecture Specification**](ARCHITECTURE.md)
   - Core entities: Claim, Evidence, Verification, Dispute.
   - Lifecycle state machine and state transitions.
   - GenVM storage model and serialization.

2. [**Intelligent Consensus & Equivalence Principle**](CONSENSUS.md)
   - The oracle problem and why GenLayer is required.
   - Leader execution vs. committee validator execution.
   - Substantive equivalence policy vs. strict byte equality.
   - Handling node disagreement and unavailable evidence.

3. [**Security & Threat Model**](SECURITY.md)
   - SSRF defenses and internal network blocking.
   - Prompt injection containment and structural delimiter neutralization.
   - Resource exhaustion boundaries (100 KB payload limits).
   - Authorization, governance, and dispute security.

4. [**Deployment Guide**](DEPLOYMENT.md)
   - Step-by-step GenLayer Studio deployment.
   - CLI deployment with `scripts/deploy.py`.
   - Interaction examples using `genlayer-py`.
