#!/usr/bin/env python3
"""
Comprehensive unit tests for UltraThink CLI

Tests cover:
- Models (Assumption, Thought, ThoughtRequest, ThoughtResponse)
- ThinkingSession class
- Session storage functions
- UltraThinkService
- CLI integration
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest
from pydantic import ValidationError

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ultrathink import (
    Assumption,
    ThinkingSession,
    Thought,
    ThoughtRequest,
    ThoughtResponse,
    UltraThinkService,
    _parse_assumption_id,
    _parse_json_list,
    _session_file_path,
    _validate_session_id,
    _validate_thought_not_empty,
    load_session,
    save_session,
)

if TYPE_CHECKING:
    from collections.abc import Generator


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_sessions_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for session storage."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        sessions_dir = Path(tmp_dir) / "ultrathink" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        with patch("ultrathink._get_sessions_dir", return_value=sessions_dir):
            yield sessions_dir


@pytest.fixture
def sample_assumption() -> Assumption:
    """Create a sample assumption for testing."""
    return Assumption(
        id="A1",
        text="Sample assumption",
        confidence=0.8,
        critical=True,
        verifiable=True,
        evidence="Some evidence",
        verification_status="unverified",
    )


@pytest.fixture
def sample_thought() -> Thought:
    """Create a sample thought for testing."""
    return Thought(
        thought="This is a test thought",
        thought_number=1,
        total_thoughts=3,
        next_thought_needed=True,
    )


@pytest.fixture
def sample_request() -> ThoughtRequest:
    """Create a sample thought request for testing."""
    return ThoughtRequest(
        thought="Test thought",
        total_thoughts=3,
    )


@pytest.fixture
def thinking_session() -> ThinkingSession:
    """Create a fresh thinking session for testing."""
    return ThinkingSession()


@pytest.fixture
def service(temp_sessions_dir: Path) -> UltraThinkService:  # noqa: ARG001
    """Create an UltraThinkService with temp storage."""
    return UltraThinkService()


# =============================================================================
# Tests: Helper Functions
# =============================================================================


class TestValidateThoughtNotEmpty:
    """Tests for _validate_thought_not_empty helper."""

    def test_valid_thought(self) -> None:
        """Non-empty strings should pass validation."""
        assert _validate_thought_not_empty("valid thought") == "valid thought"

    def test_valid_thought_with_whitespace(self) -> None:
        """Strings with content and whitespace should pass."""
        assert _validate_thought_not_empty("  valid  ") == "  valid  "

    def test_empty_string_raises(self) -> None:
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError, match="must be a non-empty string"):
            _validate_thought_not_empty("")

    def test_whitespace_only_raises(self) -> None:
        """Whitespace-only string should raise ValueError."""
        with pytest.raises(ValueError, match="must be a non-empty string"):
            _validate_thought_not_empty("   ")

    def test_newline_only_raises(self) -> None:
        """Newline-only string should raise ValueError."""
        with pytest.raises(ValueError, match="must be a non-empty string"):
            _validate_thought_not_empty("\n\t")


class TestParseJsonList:
    """Tests for _parse_json_list helper."""

    def test_none_returns_none(self) -> None:
        """None input should return None."""
        assert _parse_json_list(None, "field") is None

    def test_empty_string_returns_none(self) -> None:
        """Empty string should return None."""
        assert _parse_json_list("", "field") is None

    def test_null_string_returns_none(self) -> None:
        """'null' string should return None."""
        assert _parse_json_list("null", "field") is None

    def test_list_returns_as_is(self) -> None:
        """List input should be returned unchanged."""
        input_list = ["a", "b", "c"]
        assert _parse_json_list(input_list, "field") == input_list

    def test_valid_json_string(self) -> None:
        """Valid JSON string list should be parsed."""
        assert _parse_json_list('["a", "b"]', "field") == ["a", "b"]

    def test_json_object_raises(self) -> None:
        """JSON object (not list) should raise ValueError."""
        with pytest.raises(ValueError, match="must be a list"):
            _parse_json_list('{"key": "value"}', "field")

    def test_invalid_json_raises(self) -> None:
        """Invalid JSON should raise ValueError."""
        with pytest.raises(ValueError, match="must be valid JSON"):
            _parse_json_list("[invalid", "field")

    def test_non_string_non_list_raises(self) -> None:
        """Non-string, non-list types should raise ValueError."""
        with pytest.raises(ValueError, match="must be a list or JSON string"):
            _parse_json_list(123, "field")


class TestParseAssumptionId:
    """Tests for _parse_assumption_id helper."""

    def test_local_id(self) -> None:
        """Local assumption ID should return (None, local_id)."""
        session_id, local_id = _parse_assumption_id("A1")
        assert session_id is None
        assert local_id == "A1"

    def test_scoped_id(self) -> None:
        """Scoped assumption ID should return (session_id, local_id)."""
        session_id, local_id = _parse_assumption_id("session-123:A1")
        assert session_id == "session-123"
        assert local_id == "A1"

    def test_multiple_colons(self) -> None:
        """Only first colon should split."""
        session_id, local_id = _parse_assumption_id("session:with:colons:A1")
        assert session_id == "session"
        assert local_id == "with:colons:A1"


# =============================================================================
# Tests: Assumption Model
# =============================================================================


class TestAssumptionModel:
    """Tests for the Assumption model."""

    def test_minimal_assumption(self) -> None:
        """Assumption with only required fields should be valid."""
        assumption = Assumption(id="A1", text="Test assumption")
        assert assumption.id == "A1"
        assert assumption.text == "Test assumption"
        assert assumption.confidence == 1.0
        assert assumption.critical is True
        assert assumption.verifiable is False
        assert assumption.evidence is None
        assert assumption.verification_status is None

    def test_full_assumption(self) -> None:
        """Assumption with all fields should be valid."""
        assumption = Assumption(
            id="A1",
            text="Test assumption",
            confidence=0.5,
            critical=False,
            verifiable=True,
            evidence="Some evidence",
            verification_status="verified_true",
        )
        assert assumption.confidence == 0.5
        assert assumption.critical is False
        assert assumption.verifiable is True
        assert assumption.evidence == "Some evidence"
        assert assumption.verification_status == "verified_true"

    def test_cross_session_id_format(self) -> None:
        """Cross-session assumption ID format should be valid."""
        assumption = Assumption(id="session-123:A1", text="Test")
        assert assumption.id == "session-123:A1"

    def test_invalid_id_format(self) -> None:
        """Invalid assumption ID format should raise."""
        with pytest.raises(ValidationError):
            Assumption(id="invalid!", text="Test")

    def test_invalid_id_missing_number(self) -> None:
        """Assumption ID without number should raise."""
        with pytest.raises(ValidationError):
            Assumption(id="A", text="Test")

    def test_empty_text_raises(self) -> None:
        """Empty text should raise validation error."""
        with pytest.raises(ValidationError):
            Assumption(id="A1", text="")

    def test_confidence_below_zero_raises(self) -> None:
        """Confidence below 0.0 should raise."""
        with pytest.raises(ValidationError):
            Assumption(id="A1", text="Test", confidence=-0.1)

    def test_confidence_above_one_raises(self) -> None:
        """Confidence above 1.0 should raise."""
        with pytest.raises(ValidationError):
            Assumption(id="A1", text="Test", confidence=1.1)

    def test_invalid_verification_status(self) -> None:
        """Invalid verification status should raise."""
        with pytest.raises(ValidationError):
            Assumption(id="A1", text="Test", verification_status="invalid")  # type: ignore[arg-type]

    def test_is_verified_property_unverified(self) -> None:
        """is_verified should return False when unverified."""
        assumption = Assumption(id="A1", text="Test", verification_status="unverified")
        assert assumption.is_verified is False

    def test_is_verified_property_verified_true(self) -> None:
        """is_verified should return True when verified_true."""
        assumption = Assumption(
            id="A1", text="Test", verification_status="verified_true"
        )
        assert assumption.is_verified is True

    def test_is_verified_property_verified_false(self) -> None:
        """is_verified should return True when verified_false."""
        assumption = Assumption(
            id="A1", text="Test", verification_status="verified_false"
        )
        assert assumption.is_verified is True

    def test_is_falsified_property(self) -> None:
        """is_falsified should return True only for verified_false."""
        unverified = Assumption(id="A1", text="Test", verification_status="unverified")
        verified_true = Assumption(
            id="A2", text="Test", verification_status="verified_true"
        )
        verified_false = Assumption(
            id="A3", text="Test", verification_status="verified_false"
        )

        assert unverified.is_falsified is False
        assert verified_true.is_falsified is False
        assert verified_false.is_falsified is True

    def test_is_risky_critical_low_confidence_unverified(self) -> None:
        """Risky: critical=True, confidence<0.7, not verified_true."""
        assumption = Assumption(
            id="A1",
            text="Test",
            critical=True,
            confidence=0.5,
            verification_status="unverified",
        )
        assert assumption.is_risky is True

    def test_is_risky_non_critical(self) -> None:
        """Non-critical assumptions are not risky."""
        assumption = Assumption(
            id="A1",
            text="Test",
            critical=False,
            confidence=0.5,
            verification_status="unverified",
        )
        assert assumption.is_risky is False

    def test_is_risky_high_confidence(self) -> None:
        """High confidence assumptions are not risky."""
        assumption = Assumption(
            id="A1",
            text="Test",
            critical=True,
            confidence=0.8,
            verification_status="unverified",
        )
        assert assumption.is_risky is False

    def test_is_risky_verified_true(self) -> None:
        """Verified true assumptions are not risky."""
        assumption = Assumption(
            id="A1",
            text="Test",
            critical=True,
            confidence=0.5,
            verification_status="verified_true",
        )
        assert assumption.is_risky is False

    def test_is_risky_boundary_confidence(self) -> None:
        """Test risky at confidence boundary (0.7)."""
        at_boundary = Assumption(id="A1", text="Test", critical=True, confidence=0.7)
        below_boundary = Assumption(
            id="A2", text="Test", critical=True, confidence=0.69
        )

        assert at_boundary.is_risky is False  # 0.7 is NOT < 0.7
        assert below_boundary.is_risky is True


# =============================================================================
# Tests: Thought Model
# =============================================================================


class TestThoughtModel:
    """Tests for the Thought model."""

    def test_minimal_thought(self) -> None:
        """Thought with only required fields should be valid."""
        thought = Thought(
            thought="Test thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )
        assert thought.thought == "Test thought"
        assert thought.thought_number == 1
        assert thought.total_thoughts == 3
        assert thought.next_thought_needed is True

    def test_full_thought(self) -> None:
        """Thought with all fields should be valid."""
        assumptions = [Assumption(id="A1", text="Test assumption")]
        thought = Thought(
            thought="Test thought",
            thought_number=2,
            total_thoughts=5,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=1,
            branch_from_thought=1,
            branch_id="alt-branch",
            needs_more_thoughts=True,
            confidence=0.8,
            uncertainty_notes="Some uncertainty",
            outcome="Expected outcome",
            assumptions=assumptions,
            depends_on_assumptions=["A1"],
            invalidates_assumptions=["A2"],
        )
        assert thought.is_revision is True
        assert thought.revises_thought == 1
        assert thought.branch_from_thought == 1
        assert thought.branch_id == "alt-branch"
        assert thought.confidence == 0.8
        assert thought.assumptions is not None
        assert len(thought.assumptions) == 1

    def test_empty_thought_raises(self) -> None:
        """Empty thought string should raise."""
        with pytest.raises(ValidationError):
            Thought(
                thought="",
                thought_number=1,
                total_thoughts=3,
                next_thought_needed=True,
            )

    def test_whitespace_thought_raises(self) -> None:
        """Whitespace-only thought should raise."""
        with pytest.raises(ValidationError):
            Thought(
                thought="   ",
                thought_number=1,
                total_thoughts=3,
                next_thought_needed=True,
            )

    def test_thought_number_zero_raises(self) -> None:
        """thought_number of 0 should raise."""
        with pytest.raises(ValidationError):
            Thought(
                thought="Test",
                thought_number=0,
                total_thoughts=3,
                next_thought_needed=True,
            )

    def test_thought_number_negative_raises(self) -> None:
        """Negative thought_number should raise."""
        with pytest.raises(ValidationError):
            Thought(
                thought="Test",
                thought_number=-1,
                total_thoughts=3,
                next_thought_needed=True,
            )

    def test_total_thoughts_zero_raises(self) -> None:
        """total_thoughts of 0 should raise."""
        with pytest.raises(ValidationError):
            Thought(
                thought="Test",
                thought_number=1,
                total_thoughts=0,
                next_thought_needed=True,
            )

    def test_confidence_bounds(self) -> None:
        """Confidence should be between 0.0 and 1.0."""
        # Valid bounds
        thought_low = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            confidence=0.0,
        )
        thought_high = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            confidence=1.0,
        )
        assert thought_low.confidence == 0.0
        assert thought_high.confidence == 1.0

        # Invalid bounds
        with pytest.raises(ValidationError):
            Thought(
                thought="Test",
                thought_number=1,
                total_thoughts=3,
                next_thought_needed=True,
                confidence=-0.1,
            )
        with pytest.raises(ValidationError):
            Thought(
                thought="Test",
                thought_number=1,
                total_thoughts=3,
                next_thought_needed=True,
                confidence=1.1,
            )

    def test_is_branch_property(self) -> None:
        """is_branch should return True only when both fields set."""
        not_branch = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )
        partial_branch_1 = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            branch_from_thought=1,
        )
        partial_branch_2 = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            branch_id="alt",
        )
        full_branch = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            branch_from_thought=1,
            branch_id="alt",
        )

        assert not_branch.is_branch is False
        assert partial_branch_1.is_branch is False
        assert partial_branch_2.is_branch is False
        assert full_branch.is_branch is True

    def test_is_final_property(self) -> None:
        """is_final should return True when next_thought_needed is False."""
        final = Thought(
            thought="Test",
            thought_number=3,
            total_thoughts=3,
            next_thought_needed=False,
        )
        not_final = Thought(
            thought="Test",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
        )

        assert final.is_final is True
        assert not_final.is_final is False

    def test_auto_adjust_total(self) -> None:
        """auto_adjust_total should increase total_thoughts if needed."""
        thought = Thought(
            thought="Test",
            thought_number=5,
            total_thoughts=3,
            next_thought_needed=True,
        )
        thought.auto_adjust_total()
        assert thought.total_thoughts == 5

        # Should not decrease
        thought2 = Thought(
            thought="Test",
            thought_number=2,
            total_thoughts=5,
            next_thought_needed=True,
        )
        thought2.auto_adjust_total()
        assert thought2.total_thoughts == 5

    def test_validate_references_no_revision(self) -> None:
        """Non-revision thoughts should pass reference validation."""
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )
        # Should not raise
        thought.validate_references(set())

    def test_validate_references_valid_revision(self) -> None:
        """Valid revision reference should pass."""
        thought = Thought(
            thought="Test",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=1,
        )
        thought.validate_references({1})

    def test_validate_references_invalid_revision(self) -> None:
        """Invalid revision reference should raise."""
        thought = Thought(
            thought="Test",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=5,
        )
        with pytest.raises(ValueError, match="Cannot revise thought 5"):
            thought.validate_references({1, 2})

    def test_validate_references_revision_empty_session(self) -> None:
        """Revision with empty session should give helpful error."""
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=1,
        )
        with pytest.raises(ValueError, match="no thoughts exist"):
            thought.validate_references(set())

    def test_validate_references_valid_branch(self) -> None:
        """Valid branch reference should pass."""
        thought = Thought(
            thought="Test",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            branch_from_thought=1,
            branch_id="alt",
        )
        thought.validate_references({1})

    def test_validate_references_invalid_branch(self) -> None:
        """Invalid branch reference should raise."""
        thought = Thought(
            thought="Test",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            branch_from_thought=5,
            branch_id="alt",
        )
        with pytest.raises(ValueError, match="Cannot branch from thought 5"):
            thought.validate_references({1, 2})

    def test_assumptions_from_json_string(self) -> None:
        """Assumptions should parse from JSON string."""
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            assumptions='[{"id": "A1", "text": "Test assumption"}]',  # type: ignore[arg-type]
        )
        assert thought.assumptions is not None
        assert len(thought.assumptions) == 1
        assert thought.assumptions[0].id == "A1"

    def test_depends_on_from_json_string(self) -> None:
        """depends_on_assumptions should parse from JSON string."""
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            depends_on_assumptions='["A1", "A2"]',  # type: ignore[arg-type]
        )
        assert thought.depends_on_assumptions == ["A1", "A2"]


# =============================================================================
# Tests: ThoughtRequest Model
# =============================================================================


class TestThoughtRequestModel:
    """Tests for the ThoughtRequest model."""

    def test_minimal_request(self) -> None:
        """Request with only required fields should be valid."""
        request = ThoughtRequest(thought="Test", total_thoughts=3)
        assert request.thought == "Test"
        assert request.total_thoughts == 3
        assert request.session_id is None
        assert request.thought_number is None

    def test_full_request(self) -> None:
        """Request with all fields should be valid."""
        request = ThoughtRequest(
            thought="Test thought",
            total_thoughts=5,
            next_thought_needed=True,
            thought_number=2,
            session_id="session-123",
            is_revision=True,
            revises_thought=1,
            branch_from_thought=1,
            branch_id="alt",
            needs_more_thoughts=True,
            confidence=0.8,
            uncertainty_notes="Notes",
            outcome="Outcome",
            assumptions=[Assumption(id="A1", text="Test")],
            depends_on_assumptions=["A1"],
            invalidates_assumptions=["A2"],
        )
        assert request.session_id == "session-123"
        assert request.thought_number == 2

    def test_empty_thought_raises(self) -> None:
        """Empty thought should raise."""
        with pytest.raises(ValidationError):
            ThoughtRequest(thought="", total_thoughts=3)

    def test_invalid_total_thoughts(self) -> None:
        """total_thoughts < 1 should raise."""
        with pytest.raises(ValidationError):
            ThoughtRequest(thought="Test", total_thoughts=0)

    def test_assumptions_json_parsing(self) -> None:
        """Assumptions should parse from JSON string."""
        request = ThoughtRequest(
            thought="Test",
            total_thoughts=3,
            assumptions='[{"id": "A1", "text": "Test"}]',  # type: ignore[arg-type]
        )
        assert request.assumptions is not None
        assert len(request.assumptions) == 1


# =============================================================================
# Tests: ThoughtResponse Model
# =============================================================================


class TestThoughtResponseModel:
    """Tests for the ThoughtResponse model."""

    def test_minimal_response(self) -> None:
        """Response with only required fields should be valid."""
        response = ThoughtResponse(
            session_id="session-123",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            branches=[],
            thought_history_length=1,
        )
        assert response.session_id == "session-123"
        assert response.branches == []
        assert response.all_assumptions == {}

    def test_full_response(self) -> None:
        """Response with all fields should be valid."""
        assumption = Assumption(id="A1", text="Test")
        response = ThoughtResponse(
            session_id="session-123",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            branches=["alt", "exp"],
            thought_history_length=5,
            confidence=0.8,
            uncertainty_notes="Notes",
            outcome="Outcome",
            all_assumptions={"A1": assumption},
            risky_assumptions=["A2"],
            falsified_assumptions=["A3"],
            unresolved_references=["other:A1"],
            cross_session_warnings=["Warning message"],
        )
        assert response.branches == ["alt", "exp"]
        assert "A1" in response.all_assumptions

    def test_json_serialization(self) -> None:
        """Response should serialize to JSON correctly."""
        response = ThoughtResponse(
            session_id="session-123",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            branches=[],
            thought_history_length=1,
        )
        json_str = response.model_dump_json()
        data = json.loads(json_str)
        assert data["session_id"] == "session-123"


# =============================================================================
# Tests: ThinkingSession
# =============================================================================


class TestThinkingSession:
    """Tests for the ThinkingSession class."""

    def test_initial_state(self, thinking_session: ThinkingSession) -> None:
        """New session should have empty state."""
        assert thinking_session.thought_count == 0
        assert thinking_session.branch_ids == []
        assert thinking_session.all_assumptions == {}
        assert thinking_session.risky_assumptions == []
        assert thinking_session.falsified_assumptions == []
        assert thinking_session.unresolved_references == []
        assert thinking_session.cross_session_warnings == []

    def test_add_simple_thought(self, thinking_session: ThinkingSession) -> None:
        """Adding a simple thought should increase count."""
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )
        thinking_session.add_thought(thought)
        assert thinking_session.thought_count == 1

    def test_add_multiple_thoughts(self, thinking_session: ThinkingSession) -> None:
        """Adding multiple thoughts should track all."""
        for i in range(1, 4):
            thought = Thought(
                thought=f"Thought {i}",
                thought_number=i,
                total_thoughts=3,
                next_thought_needed=i < 3,
            )
            thinking_session.add_thought(thought)

        assert thinking_session.thought_count == 3

    def test_add_thought_with_assumption(
        self, thinking_session: ThinkingSession
    ) -> None:
        """Adding thought with assumption should track assumption."""
        assumption = Assumption(id="A1", text="Test assumption")
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            assumptions=[assumption],
        )
        thinking_session.add_thought(thought)

        assert "A1" in thinking_session.all_assumptions
        assert thinking_session.all_assumptions["A1"].text == "Test assumption"

    def test_add_thought_with_branch(self, thinking_session: ThinkingSession) -> None:
        """Adding branched thought should track branch."""
        # First add a base thought
        base_thought = Thought(
            thought="Base",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )
        thinking_session.add_thought(base_thought)

        # Then add a branched thought
        branch_thought = Thought(
            thought="Branch",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            branch_from_thought=1,
            branch_id="alt",
        )
        thinking_session.add_thought(branch_thought)

        assert "alt" in thinking_session.branch_ids

    def test_depends_on_nonexistent_assumption_raises(
        self, thinking_session: ThinkingSession
    ) -> None:
        """Depending on non-existent local assumption should raise."""
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            depends_on_assumptions=["A999"],
        )
        with pytest.raises(ValueError, match="Cannot depend on assumption A999"):
            thinking_session.add_thought(thought)

    def test_depends_on_existing_assumption(
        self, thinking_session: ThinkingSession
    ) -> None:
        """Depending on existing assumption should work."""
        # First add assumption
        thought1 = Thought(
            thought="Define assumption",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            assumptions=[Assumption(id="A1", text="Test")],
        )
        thinking_session.add_thought(thought1)

        # Then depend on it
        thought2 = Thought(
            thought="Use assumption",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            depends_on_assumptions=["A1"],
        )
        thinking_session.add_thought(thought2)  # Should not raise

    def test_depends_on_cross_session_assumption(
        self, thinking_session: ThinkingSession
    ) -> None:
        """Cross-session references should be tracked as unresolved."""
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            depends_on_assumptions=["other-session:A1"],
        )
        thinking_session.add_thought(thought)
        assert "other-session:A1" in thinking_session.unresolved_references

    def test_invalidate_local_assumption(
        self, thinking_session: ThinkingSession
    ) -> None:
        """Invalidating local assumption should mark as falsified."""
        # Add assumption
        thought1 = Thought(
            thought="Define",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            assumptions=[Assumption(id="A1", text="Test")],
        )
        thinking_session.add_thought(thought1)

        # Invalidate it
        thought2 = Thought(
            thought="Invalidate",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=False,
            invalidates_assumptions=["A1"],
        )
        thinking_session.add_thought(thought2)

        assert "A1" in thinking_session.falsified_assumptions
        assumption = thinking_session.all_assumptions["A1"]
        assert assumption.verification_status == "verified_false"

    def test_invalidate_nonexistent_assumption_raises(
        self, thinking_session: ThinkingSession
    ) -> None:
        """Invalidating non-existent assumption should raise."""
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            invalidates_assumptions=["A999"],
        )
        with pytest.raises(ValueError, match="Cannot invalidate assumption A999"):
            thinking_session.add_thought(thought)

    def test_invalidate_cross_session_assumption_warns(
        self, thinking_session: ThinkingSession
    ) -> None:
        """Invalidating cross-session assumption should add warning."""
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            invalidates_assumptions=["other:A1"],
        )
        thinking_session.add_thought(thought)

        warnings = thinking_session.cross_session_warnings
        assert len(warnings) == 1
        assert "cross-session invalidation not supported" in warnings[0]

    def test_update_assumption_mutable_fields(
        self, thinking_session: ThinkingSession
    ) -> None:
        """Updating mutable fields of existing assumption should work."""
        # Add assumption
        thought1 = Thought(
            thought="Define",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            assumptions=[
                Assumption(
                    id="A1",
                    text="Test",
                    confidence=0.5,
                    verification_status="unverified",
                )
            ],
        )
        thinking_session.add_thought(thought1)

        # Update mutable fields
        thought2 = Thought(
            thought="Update",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=False,
            assumptions=[
                Assumption(
                    id="A1",
                    text="Test",  # Same text
                    confidence=0.9,  # Updated
                    verification_status="verified_true",  # Updated
                )
            ],
        )
        thinking_session.add_thought(thought2)

        assumption = thinking_session.all_assumptions["A1"]
        assert assumption.confidence == 0.9
        assert assumption.verification_status == "verified_true"

    def test_update_assumption_immutable_text_raises(
        self, thinking_session: ThinkingSession
    ) -> None:
        """Changing assumption text should raise."""
        thought1 = Thought(
            thought="Define",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            assumptions=[Assumption(id="A1", text="Original text")],
        )
        thinking_session.add_thought(thought1)

        thought2 = Thought(
            thought="Update",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=False,
            assumptions=[Assumption(id="A1", text="Different text")],
        )
        with pytest.raises(ValueError, match="text mismatch"):
            thinking_session.add_thought(thought2)

    def test_update_assumption_immutable_critical_raises(
        self, thinking_session: ThinkingSession
    ) -> None:
        """Changing assumption critical flag should raise."""
        thought1 = Thought(
            thought="Define",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            assumptions=[Assumption(id="A1", text="Test", critical=True)],
        )
        thinking_session.add_thought(thought1)

        thought2 = Thought(
            thought="Update",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=False,
            assumptions=[Assumption(id="A1", text="Test", critical=False)],
        )
        with pytest.raises(ValueError, match="critical flag mismatch"):
            thinking_session.add_thought(thought2)

    def test_risky_assumptions_tracking(
        self, thinking_session: ThinkingSession
    ) -> None:
        """Risky assumptions should be tracked."""
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            assumptions=[
                Assumption(id="A1", text="Risky", critical=True, confidence=0.5),
                Assumption(id="A2", text="Safe", critical=True, confidence=0.9),
            ],
        )
        thinking_session.add_thought(thought)

        assert "A1" in thinking_session.risky_assumptions
        assert "A2" not in thinking_session.risky_assumptions


# =============================================================================
# Tests: Session Storage
# =============================================================================


class TestSessionIdValidation:
    """Tests for session ID validation."""

    def test_valid_alphanumeric(self) -> None:
        """Alphanumeric IDs should be valid."""
        _validate_session_id("abc123")

    def test_valid_with_hyphens(self) -> None:
        """IDs with hyphens should be valid."""
        _validate_session_id("session-123")

    def test_valid_with_underscores(self) -> None:
        """IDs with underscores should be valid."""
        _validate_session_id("session_123")

    def test_valid_uuid(self) -> None:
        """UUID-style IDs should be valid."""
        _validate_session_id("550e8400-e29b-41d4-a716-446655440000")

    def test_empty_raises(self) -> None:
        """Empty ID should raise."""
        with pytest.raises(ValueError, match="cannot be empty"):
            _validate_session_id("")

    def test_too_long_raises(self) -> None:
        """ID > 128 chars should raise."""
        with pytest.raises(ValueError, match="too long"):
            _validate_session_id("a" * 129)

    def test_path_traversal_raises(self) -> None:
        """Path traversal attempts should raise."""
        with pytest.raises(ValueError, match="Invalid session ID"):
            _validate_session_id("../../../etc/passwd")

    def test_special_chars_raises(self) -> None:
        """Special characters should raise."""
        for char in ["!", "@", "#", "$", "%", "^", "&", "*", "/", "\\"]:
            with pytest.raises(ValueError, match="Invalid session ID"):
                _validate_session_id(f"session{char}id")


class TestSessionStorage:
    """Tests for session save/load functions."""

    def test_save_and_load_simple_session(
        self,
        temp_sessions_dir: Path,  # noqa: ARG002
        thinking_session: ThinkingSession,
    ) -> None:
        """Save and load should preserve simple session state."""
        thought = Thought(
            thought="Test thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )
        thinking_session.add_thought(thought)

        save_session("test-session", thinking_session)
        loaded = load_session("test-session")

        assert loaded is not None
        assert loaded.thought_count == 1

    def test_save_and_load_with_assumptions(
        self,
        temp_sessions_dir: Path,  # noqa: ARG002
        thinking_session: ThinkingSession,
    ) -> None:
        """Save and load should preserve assumptions."""
        thought = Thought(
            thought="Test",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
            assumptions=[
                Assumption(
                    id="A1",
                    text="Test assumption",
                    confidence=0.8,
                    verification_status="verified_true",
                )
            ],
        )
        thinking_session.add_thought(thought)

        save_session("test-session", thinking_session)
        loaded = load_session("test-session")

        assert loaded is not None
        assert "A1" in loaded.all_assumptions
        assert loaded.all_assumptions["A1"].confidence == 0.8
        assert loaded.all_assumptions["A1"].verification_status == "verified_true"

    def test_save_and_load_with_branches(
        self,
        temp_sessions_dir: Path,  # noqa: ARG002
        thinking_session: ThinkingSession,
    ) -> None:
        """Save and load should preserve branch structure."""
        thought1 = Thought(
            thought="Base",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )
        thought2 = Thought(
            thought="Branch",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            branch_from_thought=1,
            branch_id="alt",
        )
        thinking_session.add_thought(thought1)
        thinking_session.add_thought(thought2)

        save_session("test-session", thinking_session)
        loaded = load_session("test-session")

        assert loaded is not None
        assert "alt" in loaded.branch_ids

    def test_load_nonexistent_session(
        self,
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """Loading non-existent session should return None."""
        loaded = load_session("nonexistent-session")
        assert loaded is None

    def test_load_corrupted_session(self, temp_sessions_dir: Path) -> None:
        """Loading corrupted session file should return None."""
        session_file = temp_sessions_dir / "corrupted.json"
        session_file.write_text("{ invalid json }")

        loaded = load_session("corrupted")
        assert loaded is None

    def test_load_invalid_structure(self, temp_sessions_dir: Path) -> None:
        """Loading file with invalid structure should return None."""
        session_file = temp_sessions_dir / "invalid.json"
        session_file.write_text('{"thoughts": "not_a_list"}')

        loaded = load_session("invalid")
        assert loaded is None

    def test_session_file_path(self, temp_sessions_dir: Path) -> None:
        """Session file path should be correct."""
        path = _session_file_path("my-session")
        assert path.name == "my-session.json"
        assert path.parent == temp_sessions_dir


# =============================================================================
# Tests: UltraThinkService
# =============================================================================


class TestUltraThinkService:
    """Tests for the UltraThinkService class."""

    def test_process_new_session(
        self, service: UltraThinkService, sample_request: ThoughtRequest
    ) -> None:
        """Processing request without session ID should create new session."""
        response = service.process_thought(sample_request)

        assert response.session_id is not None
        assert len(response.session_id) == 36  # UUID format
        assert response.thought_number == 1
        assert response.thought_history_length == 1

    def test_process_continue_session(self, service: UltraThinkService) -> None:
        """Processing with session ID should continue session."""
        # First thought
        request1 = ThoughtRequest(thought="First", total_thoughts=3)
        response1 = service.process_thought(request1)
        session_id = response1.session_id

        # Second thought in same session
        request2 = ThoughtRequest(
            thought="Second", total_thoughts=3, session_id=session_id
        )
        response2 = service.process_thought(request2)

        assert response2.session_id == session_id
        assert response2.thought_number == 2
        assert response2.thought_history_length == 2

    def test_process_auto_thought_number(self, service: UltraThinkService) -> None:
        """thought_number should auto-increment if not provided."""
        request1 = ThoughtRequest(thought="First", total_thoughts=5)
        response1 = service.process_thought(request1)

        request2 = ThoughtRequest(
            thought="Second", total_thoughts=5, session_id=response1.session_id
        )
        response2 = service.process_thought(request2)

        request3 = ThoughtRequest(
            thought="Third", total_thoughts=5, session_id=response1.session_id
        )
        response3 = service.process_thought(request3)

        assert response1.thought_number == 1
        assert response2.thought_number == 2
        assert response3.thought_number == 3

    def test_process_explicit_thought_number(self, service: UltraThinkService) -> None:
        """Explicit thought_number should override auto-increment."""
        request = ThoughtRequest(thought="Test", total_thoughts=5, thought_number=3)
        response = service.process_thought(request)

        assert response.thought_number == 3

    def test_process_auto_next_thought_needed(self, service: UltraThinkService) -> None:
        """next_thought_needed should auto-calculate if not provided."""
        request1 = ThoughtRequest(thought="First", total_thoughts=2, thought_number=1)
        response1 = service.process_thought(request1)

        request2 = ThoughtRequest(
            thought="Second",
            total_thoughts=2,
            thought_number=2,
            session_id=response1.session_id,
        )
        response2 = service.process_thought(request2)

        assert response1.next_thought_needed is True  # 1 < 2
        assert response2.next_thought_needed is False  # 2 >= 2

    def test_process_explicit_next_thought_needed(
        self, service: UltraThinkService
    ) -> None:
        """Explicit next_thought_needed should override auto-calculation."""
        request = ThoughtRequest(
            thought="Test",
            total_thoughts=5,
            thought_number=3,
            next_thought_needed=False,  # Override
        )
        response = service.process_thought(request)

        assert response.next_thought_needed is False  # Explicit value, not auto

    def test_process_with_assumptions(self, service: UltraThinkService) -> None:
        """Processing with assumptions should track them."""
        request = ThoughtRequest(
            thought="Test",
            total_thoughts=3,
            assumptions=[Assumption(id="A1", text="Test assumption", confidence=0.8)],
        )
        response = service.process_thought(request)

        assert "A1" in response.all_assumptions
        assert response.all_assumptions["A1"].text == "Test assumption"

    def test_process_with_risky_assumption(self, service: UltraThinkService) -> None:
        """Risky assumptions should be reported."""
        request = ThoughtRequest(
            thought="Test",
            total_thoughts=3,
            assumptions=[
                Assumption(id="A1", text="Risky", critical=True, confidence=0.5)
            ],
        )
        response = service.process_thought(request)

        assert "A1" in response.risky_assumptions

    def test_process_with_confidence(self, service: UltraThinkService) -> None:
        """Confidence should be passed through."""
        request = ThoughtRequest(thought="Test", total_thoughts=3, confidence=0.85)
        response = service.process_thought(request)

        assert response.confidence == 0.85

    def test_process_with_outcome(self, service: UltraThinkService) -> None:
        """Outcome should be passed through."""
        request = ThoughtRequest(
            thought="Test", total_thoughts=3, outcome="Expected result"
        )
        response = service.process_thought(request)

        assert response.outcome == "Expected result"

    def test_process_creates_new_session_for_custom_id(
        self, service: UltraThinkService
    ) -> None:
        """Custom session ID should create new session if not found."""
        request = ThoughtRequest(
            thought="Test", total_thoughts=3, session_id="custom-session-id"
        )
        response = service.process_thought(request)

        assert response.session_id == "custom-session-id"
        assert response.thought_number == 1

    def test_process_cross_session_dependency_unresolved(
        self, service: UltraThinkService
    ) -> None:
        """Unresolved cross-session refs should be tracked."""
        request = ThoughtRequest(
            thought="Test",
            total_thoughts=3,
            depends_on_assumptions=["nonexistent-session:A1"],
        )
        response = service.process_thought(request)

        assert "nonexistent-session:A1" in response.unresolved_references

    def test_process_cross_session_dependency_resolved(
        self,
        service: UltraThinkService,
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """Resolved cross-session refs should not be in unresolved."""
        # Create another session with an assumption
        other_session = ThinkingSession()
        other_thought = Thought(
            thought="Other",
            thought_number=1,
            total_thoughts=1,
            next_thought_needed=False,
            assumptions=[Assumption(id="A1", text="Other assumption")],
        )
        other_session.add_thought(other_thought)
        save_session("other-session", other_session)

        # Reference that assumption
        request = ThoughtRequest(
            thought="Test",
            total_thoughts=3,
            depends_on_assumptions=["other-session:A1"],
        )
        response = service.process_thought(request)

        # Should NOT be in unresolved since it was found
        assert "other-session:A1" not in response.unresolved_references

    def test_service_caches_sessions(self, service: UltraThinkService) -> None:
        """Service should cache loaded sessions."""
        request1 = ThoughtRequest(thought="First", total_thoughts=3)
        response1 = service.process_thought(request1)

        # Access internal cache
        assert response1.session_id in service._sessions

    def test_auto_adjust_total_thoughts(self, service: UltraThinkService) -> None:
        """total_thoughts should auto-adjust if thought_number exceeds it."""
        request = ThoughtRequest(
            thought="Test",
            total_thoughts=3,
            thought_number=5,  # Greater than total
        )
        response = service.process_thought(request)

        assert response.total_thoughts == 5  # Adjusted up


# =============================================================================
# Tests: CLI Integration
# =============================================================================


class TestCLIIntegration:
    """Integration tests for CLI using typer.testing."""

    @pytest.fixture
    def runner(self) -> Any:
        """Create CLI test runner."""
        from typer.testing import CliRunner
        from ultrathink import app

        return CliRunner(), app

    def test_help_output(self, runner: tuple[Any, Any]) -> None:
        """--help should show usage."""
        cli_runner, app = runner
        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "thought" in result.stdout.lower()

    def test_version_output(self, runner: tuple[Any, Any]) -> None:
        """--version should show version JSON."""
        cli_runner, app = runner
        result = cli_runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "version" in data

    def test_basic_invocation(
        self,
        runner: tuple[Any, Any],
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """Basic invocation should return valid JSON."""
        cli_runner, app = runner
        result = cli_runner.invoke(app, ["-t", "Test thought", "-n", "3"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "session_id" in data
        assert data["thought_number"] == 1
        assert data["total_thoughts"] == 3

    def test_session_continuation(
        self,
        runner: tuple[Any, Any],
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """Session continuation should work."""
        cli_runner, app = runner

        # First thought
        result1 = cli_runner.invoke(app, ["-t", "First", "-n", "3"])
        assert result1.exit_code == 0
        data1 = json.loads(result1.stdout)
        session_id = data1["session_id"]

        # Second thought
        result2 = cli_runner.invoke(app, ["-t", "Second", "-n", "3", "-s", session_id])
        assert result2.exit_code == 0
        data2 = json.loads(result2.stdout)
        assert data2["thought_number"] == 2
        assert data2["session_id"] == session_id

    def test_with_confidence(
        self,
        runner: tuple[Any, Any],
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """--confidence option should work."""
        cli_runner, app = runner
        result = cli_runner.invoke(app, ["-t", "Test", "-n", "3", "-c", "0.8"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["confidence"] == 0.8

    def test_with_assumptions_json(
        self,
        runner: tuple[Any, Any],
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """--assumptions with JSON should work."""
        cli_runner, app = runner
        assumptions_json = '[{"id":"A1","text":"Test assumption"}]'
        result = cli_runner.invoke(
            app, ["-t", "Test", "-n", "3", "--assumptions", assumptions_json]
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "A1" in data["all_assumptions"]

    def test_with_revision(
        self,
        runner: tuple[Any, Any],
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """Revision options should work."""
        cli_runner, app = runner

        # First thought
        result1 = cli_runner.invoke(app, ["-t", "First", "-n", "3"])
        data1 = json.loads(result1.stdout)
        session_id = data1["session_id"]

        # Revision
        result2 = cli_runner.invoke(
            app,
            [
                "-t",
                "Revised",
                "-n",
                "3",
                "-s",
                session_id,
                "--is-revision",
                "--revises",
                "1",
            ],
        )

        assert result2.exit_code == 0

    def test_with_branch(
        self,
        runner: tuple[Any, Any],
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """Branch options should work."""
        cli_runner, app = runner

        # First thought
        result1 = cli_runner.invoke(app, ["-t", "First", "-n", "3"])
        data1 = json.loads(result1.stdout)
        session_id = data1["session_id"]

        # Branch
        result2 = cli_runner.invoke(
            app,
            [
                "-t",
                "Branch",
                "-n",
                "3",
                "-s",
                session_id,
                "--branch-from",
                "1",
                "--branch-id",
                "alt",
            ],
        )

        assert result2.exit_code == 0
        data2 = json.loads(result2.stdout)
        assert "alt" in data2["branches"]

    def test_empty_thought_error(
        self,
        runner: tuple[Any, Any],
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """Empty thought should return error."""
        cli_runner, app = runner
        result = cli_runner.invoke(app, ["-t", "", "-n", "3"])

        assert result.exit_code == 1
        # Error goes to output (CliRunner doesn't separate stderr by default)
        assert "validation_error" in result.output or "value_error" in result.output

    def test_invalid_session_id_error(
        self,
        runner: tuple[Any, Any],
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """Invalid session ID should return error."""
        cli_runner, app = runner
        result = cli_runner.invoke(
            app, ["-t", "Test", "-n", "3", "-s", "../../../etc/passwd"]
        )

        assert result.exit_code == 1
        assert "error" in result.output.lower()

    def test_missing_required_args(self, runner: tuple[Any, Any]) -> None:
        """Missing required args should show help."""
        cli_runner, app = runner
        result = cli_runner.invoke(app, ["-t", "Test"])  # Missing -n

        # Should exit (either with help or error)
        # When thought is provided but total is missing, it shows help
        assert result.exit_code == 0 or "Error" in result.output

    def test_depends_on_option(
        self,
        runner: tuple[Any, Any],
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """--depends-on option should work."""
        cli_runner, app = runner

        # Create assumption first
        result1 = cli_runner.invoke(
            app,
            ["-t", "Create", "-n", "3", "--assumptions", '[{"id":"A1","text":"Test"}]'],
        )
        data1 = json.loads(result1.stdout)
        session_id = data1["session_id"]

        # Depend on it
        result2 = cli_runner.invoke(
            app,
            [
                "-t",
                "Depend",
                "-n",
                "3",
                "-s",
                session_id,
                "--depends-on",
                '["A1"]',
            ],
        )

        assert result2.exit_code == 0

    def test_invalidates_option(
        self,
        runner: tuple[Any, Any],
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """--invalidates option should work."""
        cli_runner, app = runner

        # Create assumption first
        result1 = cli_runner.invoke(
            app,
            ["-t", "Create", "-n", "3", "--assumptions", '[{"id":"A1","text":"Test"}]'],
        )
        data1 = json.loads(result1.stdout)
        session_id = data1["session_id"]

        # Invalidate it
        result2 = cli_runner.invoke(
            app,
            [
                "-t",
                "Invalidate",
                "-n",
                "3",
                "-s",
                session_id,
                "--invalidates",
                '["A1"]',
            ],
        )

        assert result2.exit_code == 0
        data2 = json.loads(result2.stdout)
        assert "A1" in data2["falsified_assumptions"]

    def test_uncertainty_notes_option(
        self,
        runner: tuple[Any, Any],
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """--uncertainty-notes option should work."""
        cli_runner, app = runner
        result = cli_runner.invoke(
            app,
            ["-t", "Test", "-n", "3", "--uncertainty-notes", "Some uncertainty"],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["uncertainty_notes"] == "Some uncertainty"

    def test_outcome_option(
        self,
        runner: tuple[Any, Any],
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """--outcome option should work."""
        cli_runner, app = runner
        result = cli_runner.invoke(
            app, ["-t", "Test", "-n", "3", "--outcome", "Expected result"]
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["outcome"] == "Expected result"

    def test_needs_more_option(
        self,
        runner: tuple[Any, Any],
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """--needs-more option should work."""
        cli_runner, app = runner
        result = cli_runner.invoke(app, ["-t", "Test", "-n", "3", "--needs-more"])

        assert result.exit_code == 0

    def test_next_needed_override(
        self,
        runner: tuple[Any, Any],
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """--next-needed option should override auto-calculation."""
        cli_runner, app = runner
        result = cli_runner.invoke(
            app,
            ["-t", "Test", "-n", "3", "--thought-number", "1", "--no-next-needed"],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["next_thought_needed"] is False  # Overridden


# =============================================================================
# Tests: Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_long_thought(
        self,
        service: UltraThinkService,
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """Very long thought text should be accepted."""
        long_thought = "A" * 10000
        request = ThoughtRequest(thought=long_thought, total_thoughts=1)
        response = service.process_thought(request)

        assert response.thought_number == 1

    def test_unicode_in_thought(
        self,
        service: UltraThinkService,
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """Unicode characters in thought should work."""
        request = ThoughtRequest(
            thought="Test with unicode: 日本語, emoji: 🎉, symbols: ±∞≠",
            total_thoughts=1,
        )
        response = service.process_thought(request)

        assert response.thought_number == 1

    def test_max_session_id_length(
        self,
        service: UltraThinkService,
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """Session ID at max length (128) should work."""
        max_id = "a" * 128
        request = ThoughtRequest(thought="Test", total_thoughts=1, session_id=max_id)
        response = service.process_thought(request)

        assert response.session_id == max_id

    def test_many_assumptions(
        self,
        service: UltraThinkService,
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """Many assumptions should be handled."""
        assumptions = [
            Assumption(id=f"A{i}", text=f"Assumption {i}") for i in range(1, 51)
        ]
        request = ThoughtRequest(
            thought="Test", total_thoughts=1, assumptions=assumptions
        )
        response = service.process_thought(request)

        assert len(response.all_assumptions) == 50

    def test_many_thoughts_in_session(
        self,
        service: UltraThinkService,
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """Many thoughts in single session should work."""
        request1 = ThoughtRequest(thought="First", total_thoughts=100)
        response1 = service.process_thought(request1)
        session_id = response1.session_id

        for i in range(2, 51):
            request = ThoughtRequest(
                thought=f"Thought {i}", total_thoughts=100, session_id=session_id
            )
            response = service.process_thought(request)

        assert response.thought_history_length == 50

    def test_boundary_confidence_values(
        self,
        service: UltraThinkService,
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """Boundary confidence values (0.0, 1.0) should work."""
        request_zero = ThoughtRequest(thought="Zero", total_thoughts=1, confidence=0.0)
        response_zero = service.process_thought(request_zero)
        assert response_zero.confidence == 0.0

        request_one = ThoughtRequest(thought="One", total_thoughts=1, confidence=1.0)
        response_one = service.process_thought(request_one)
        assert response_one.confidence == 1.0

    def test_session_persistence_across_service_instances(
        self,
        temp_sessions_dir: Path,  # noqa: ARG002
    ) -> None:
        """Sessions should persist across service instances."""
        # Create thought with first service
        service1 = UltraThinkService()
        request1 = ThoughtRequest(thought="First", total_thoughts=3)
        response1 = service1.process_thought(request1)
        session_id = response1.session_id

        # Continue with new service instance
        service2 = UltraThinkService()
        request2 = ThoughtRequest(
            thought="Second", total_thoughts=3, session_id=session_id
        )
        response2 = service2.process_thought(request2)

        assert response2.thought_number == 2
        assert response2.thought_history_length == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
