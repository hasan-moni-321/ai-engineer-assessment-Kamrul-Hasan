import pytest
from pydantic import ValidationError

from backend.app.schemas.ask import AskRequest
from backend.app.schemas.router import RouterDecision


def test_question_is_normalized():
    request = AskRequest(question="  What   is   Docker?  ")
    assert request.question == "What is Docker?"


def test_blank_question_is_rejected():
    with pytest.raises(ValidationError):
        AskRequest(question="   ")


def test_router_decision_requires_valid_route():
    with pytest.raises(ValidationError):
        RouterDecision(
            route="unknown",
            confidence=0.9,
            reason="invalid",
        )
