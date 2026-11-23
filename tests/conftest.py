"""
ProofGuard Test Configuration & GenVM Simulator
================================================
Provides mock GenVM environment fixtures, test accounts, web responses,
LLM simulation, and consensus verification hooks.
"""

import json
import pytest
from contextlib import contextmanager
from typing import Dict, Any, Callable, Optional, List

from contracts.proof_guard import ProofGuard, gl
from contracts.validation import compute_sha256, check_substantive_equivalence


ALICE = "0x1111111111111111111111111111111111111111"  # Owner / Deployer
BOB = "0x2222222222222222222222222222222222222222"    # Submitter
CHARLIE = "0x3333333333333333333333333333333333333333"  # Challenger
ATTACKER = "0x9999999999999999999999999999999999999999"  # Unauthorized


class MockGenVM:
    """
    Simulates GenLayer GenVM runtime features including message context,
    nondet web fetching, nondet LLM prompting, and Equivalence Principle consensus.
    """

    def __init__(self):
        self.sender = ALICE
        self.web_responses: Dict[str, str] = {}
        self.llm_handler: Optional[Callable[[str], str]] = None
        self.consensus_disagreement: bool = False
        self.consensus_validator_override: Optional[Dict[str, Any]] = None
        self.installed = False
        self.install()

    def install(self):
        """Installs shims onto the gl module."""
        gl.message.sender_address = self.sender
        gl.nondet.web.render = self._mock_web_render
        gl.nondet.web.get = self._mock_web_render
        gl.nondet.exec_prompt = self._mock_exec_prompt
        gl.eq_principle.prompt_comparative = self._mock_prompt_comparative
        gl.eq_principle.strict_eq = self._mock_strict_eq
        self.installed = True

    @contextmanager
    def prank(self, sender: str):
        """Context manager to execute calls from a specific address."""
        old_sender = self.sender
        self.sender = sender
        gl.message.sender_address = sender
        try:
            yield
        finally:
            self.sender = old_sender
            gl.message.sender_address = old_sender

    def register_web(self, url: str, content: str):
        """Registers canned web response for a URL."""
        self.web_responses[url] = content

    def set_llm_handler(self, handler: Callable[[str], str]):
        """Sets a custom handler for LLM prompt execution."""
        self.llm_handler = handler

    def _mock_web_render(self, url: str, mode: str = "text") -> str:
        if url in self.web_responses:
            resp = self.web_responses[url]
            if isinstance(resp, Exception):
                raise resp
            return resp
        return f"Default mock page content for {url}"

    def _mock_exec_prompt(self, prompt: str) -> str:
        if self.llm_handler:
            return self.llm_handler(prompt)
        # Default structured LLM response
        return json.dumps({
            "verdict": "VERIFIED",
            "relevant_evidence_ids": ["claim_1_ev_1"],
            "supporting_facts": ["The official report confirms all criteria."],
            "contradictions": [],
            "explanation": "Claim successfully verified against registered evidence.",
        })

    def _mock_prompt_comparative(self, task: Callable[[], str], criteria: str) -> str:
        """
        Simulates multi-validator consensus under the Equivalence Principle:
        1. Leader runs task() and produces a proposal.
        2. Validators independently run task() or evaluate against criteria.
        3. Checks equivalence policy between leader and validator.
        """
        leader_output_str = task()
        leader_output = json.loads(leader_output_str)

        # Check for simulated validator disagreement
        if self.consensus_disagreement:
            validator_output = self.consensus_validator_override or {
                "verdict": "REJECTED",
                "relevant_evidence_ids": ["claim_1_ev_1"],
                "supporting_facts": [],
                "contradictions": ["Validators independently identified contradictory data."],
                "explanation": "Validator committee rejected leader conclusion.",
            }
            is_equiv, reason = check_substantive_equivalence(leader_output, validator_output)
            if not is_equiv:
                raise ValueError(f"GenLayer Consensus Failure: Equivalence check failed: {reason}")

        return leader_output_str

    def _mock_strict_eq(self, task: Callable[[], str]) -> str:
        return task()


@pytest.fixture(scope="function")
def vm():
    """Provides a fresh MockGenVM context for each test."""
    sim = MockGenVM()
    yield sim


@pytest.fixture(scope="function")
def proof_guard(vm):
    """Deploys a fresh ProofGuard contract with ALICE as owner."""
    with vm.prank(ALICE):
        contract = ProofGuard()
    return contract


@pytest.fixture
def alice():
    return ALICE


@pytest.fixture
def bob():
    return BOB


@pytest.fixture
def charlie():
    return CHARLIE


@pytest.fixture
def attacker():
    return ATTACKER


@pytest.fixture
def sample_claim_data():
    return {
        "title": "AlphaGenome v2 Release Announcement",
        "description": "DeepMind released AlphaGenome v2 on October 15, 2026, supporting genome-wide variant prediction.",
        "criteria": "Official press release or scientific publication confirming AlphaGenome v2 release date and genome-wide capability.",
    }


@pytest.fixture
def sample_evidence_url():
    return "https://deepmind.google/discover/blog/alphagenome-v2"


@pytest.fixture
def sample_evidence_content():
    return "DeepMind is proud to announce AlphaGenome v2, released October 15, 2026, featuring comprehensive genome-wide variant impact scoring."
