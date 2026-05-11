
from pydantic import create_model, BaseModel
from typing import Any

class Answer(BaseModel):
    question_id: str
    answer: bool
    excerpt: str

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

