
import re
from pydantic import create_model, BaseModel, field_validator
from typing import Any, Literal

QuestionId = Literal["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9"]
QUESTION_IDS: tuple[str, ...] = QuestionId.__args__

_QID_PATTERN = re.compile(r"^\s*q?\s*([1-9])\s*$", re.IGNORECASE)


def normalize_question_id(qid: str) -> str | None:
    """Map the variants LLMs produce ('1', 'q1', 'Q 1') to 'Q1'; None if unrecognizable."""
    match = _QID_PATTERN.match(str(qid))
    return f"Q{match.group(1)}" if match else None


class Answer(BaseModel):
    question_id: QuestionId
    answer: bool
    excerpt: str

    @field_validator("question_id", mode="before")
    @classmethod
    def _normalize_question_id(cls, value: Any) -> Any:
        # Unrecognizable ids are passed through so the Literal check rejects them
        # (which makes pydantic-ai ask the model to retry).
        return normalize_question_id(value) or value


class AllAnswers(BaseModel):
    answers: list[Answer]

def make_model(name: str, fields: dict[str, Any]):
    """
    fields: { "field_name": (type, default) }
    or just { "field_name": type }  — default becomes ...  (required)
    """
    field_definitions = {}
    for key, value in fields.items():
        if isinstance(value, tuple):
            field_definitions[key] = value          # (type, default)
        else:
            field_definitions[key] = (value, ...)   # required field

    return create_model(name, **field_definitions)
