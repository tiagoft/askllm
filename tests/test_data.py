import pytest
from pydantic import ValidationError

from askllm.models.data import Answer, normalize_question_id


@pytest.mark.parametrize("raw", ["Q1", "q1", "1", " Q 1 ", 1])
def test_normalize_variants(raw):
    assert normalize_question_id(raw) == "Q1"


@pytest.mark.parametrize("raw", ["FQ1", "model_type", "Q10", "0", ""])
def test_normalize_rejects(raw):
    assert normalize_question_id(raw) is None


def test_answer_normalizes_id():
    assert Answer(question_id="3", answer=True, excerpt="x").question_id == "Q3"


def test_answer_rejects_unknown_id():
    with pytest.raises(ValidationError):
        Answer(question_id="privacy", answer=True, excerpt="x")


def test_schema_exposes_enum():
    schema = Answer.model_json_schema()
    assert schema["properties"]["question_id"]["enum"] == [f"Q{i}" for i in range(1, 10)]
