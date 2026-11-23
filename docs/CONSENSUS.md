# ProofGuard Intelligent Consensus & Equivalence Principle

This document details how ProofGuard achieves consensus over non-deterministic web retrieval and LLM reasoning on the GenLayer blockchain.

---

## 1. The Challenge of Non-Deterministic Smart Contracts

Traditional blockchains achieve consensus by requiring all nodes to execute identical machine instructions and arrive at identical byte states. This deterministic model breaks down when smart contracts need to:
- Scrape dynamic web pages (HTML headers, ad trackers, timestamps vary across requests).
- Prompt Large Language Models (generative token sampling can produce slightly different wording for the same prompt).

If two validators received slightly different HTML or if their LLM phrased its explanation differently, a traditional blockchain would fork.

---

## 2. GenLayer's Equivalence Principle

GenLayer solves this through the **Equivalence Principle** (`gl.eq_principle`). Instead of requiring exact string or byte matches, GenLayer validators reach consensus on **substantive decision fields and semantic meaning**.

In ProofGuard, the verification task is executed under `gl.eq_principle.prompt_comparative`:

```python
consensus_principle = (
    "Consensus Equivalence Policy: "
    "1. The 'verdict' ('VERIFIED', 'REJECTED', or 'INCONCLUSIVE') must match exactly. "
    "2. Relevant evidence identifiers must be compatible. "
    "3. Extracted supporting facts and identified contradictions must agree in substance. "
    "4. Natural language phrasing does not need to be word-for-word identical. "
    "5. If external sources fail across nodes, verdict must safely resolve to 'INCONCLUSIVE'."
)

consensus_result_json = gl.eq_principle.prompt_comparative(
    execute_verification_task,
    consensus_principle,
)
```

---

## 3. Consensus Lifecycle Step-by-Step

### Step 1: Leader Proposal
1. A randomly selected committee leader executes `execute_verification_task()`.
2. The leader independently fetches each registered evidence URL using `gl.nondet.web.render(url, mode="text")`.
3. The leader sanitizes the retrieved content, bounds it to 100 KB, and embeds it inside isolation delimiters `<<<UNTRUSTED_EXTERNAL_EVIDENCE_START>>>`.
4. The leader queries the local LLM using `gl.nondet.exec_prompt(prompt)`.
5. The leader parses and normalizes the output into strict JSON:
   ```json
   {
     "verdict": "VERIFIED",
     "relevant_evidence_ids": ["claim_1_ev_1"],
     "supporting_facts": ["Official release confirmed for October 15, 2026."],
     "contradictions": [],
     "explanation": "The primary documentation confirms the stated criteria."
   }
   ```
6. The leader proposes this receipt to the validator committee.

### Step 2: Independent Validator Re-Execution
1. Each committee validator independently executes `execute_verification_task()`.
2. Each validator makes their own network requests to the evidence URLs.
3. Each validator queries their own local LLM using the same prompt template.
4. Each validator produces an independent candidate structured result.

### Step 3: Substantive Equivalence Evaluation
The committee compares the leader's proposal against the validators' findings:
- **Verdict Match**: Does the leader say `VERIFIED` while the validator says `VERIFIED`? If one says `VERIFIED` and another says `REJECTED`, the proposal is rejected.
- **Evidence Overlap**: Did both validators cite compatible registered evidence IDs?
- **Fact Compatibility**: Did one validator find material contradictions that refute the other's supporting facts?
- **Phrasing Tolerance**: If the leader's explanation says *"Verified based on the blog announcement"* while the validator's explanation says *"The announcement confirms the stated release date"*, the equivalence check succeeds because their substantive findings agree.

### Step 4: Fallback & Failure Handling
- **All Sources Unreachable**: If external servers are down (HTTP 500, 503, DNS failure), the task returns verdict `INCONCLUSIVE` without halting the node.
- **Committee Disagreement**: If a leader attempts to push a false verdict (e.g., claiming a claim is verified when evidence refutes it), the independent validators fail the equivalence check, triggering leader rotation and preventing invalid state transitions.
