"""
tests/test_agent.py
Unit tests for core agent components.
"""

import pytest
from memory.bank import MemoryBank
from agent.policy import Policy


class TestMemoryBank:
    def test_store_and_retrieve(self, tmp_path):
        bank = MemoryBank(path=str(tmp_path / "bank.json"))
        bank.store("foo bar baz", "spec1", "Inv1 == TRUE")
        bank.store("hello world", "spec2", "Inv2 == TRUE")

        results = bank.retrieve("foo bar", k=1)
        assert len(results) == 1
        assert results[0]["invariant"] == "Inv1 == TRUE"

    def test_empty_bank_returns_empty(self, tmp_path):
        bank = MemoryBank(path=str(tmp_path / "bank.json"))
        assert bank.retrieve("anything", k=3) == []

    def test_len(self, tmp_path):
        bank = MemoryBank(path=str(tmp_path / "bank.json"))
        bank.store("d1", "s1", "i1")
        bank.store("d2", "s2", "i2")
        assert len(bank) == 2


class TestPolicy:
    def test_format_feedback_contains_trace(self, tmp_path):
        bank = MemoryBank(path=str(tmp_path / "bank.json"))
        policy = Policy(bank)
        counterexample = {
            "property": "MutualExclusion",
            "trace": ["State 1: pc1=critical, pc2=critical"],
        }
        feedback = policy.format_feedback(counterexample)
        assert "MutualExclusion" in feedback
        assert "State 1" in feedback

    def test_build_prompt_structure(self, tmp_path):
        bank = MemoryBank(path=str(tmp_path / "bank.json"))
        policy = Policy(bank)
        messages = policy.build_prompt("prog", "spec", [], [])
        assert messages[0]["role"] == "system"
        assert any(m["role"] == "user" for m in messages)
