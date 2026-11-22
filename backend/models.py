from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Login(InputModel):
    person_id: str = Field(min_length=3, max_length=160)
    password: str = Field(min_length=1, max_length=200)


class Section(InputModel):
    heading: str = Field(min_length=2, max_length=120)
    body: str = Field(min_length=3, max_length=10000)


class Content(InputModel):
    summary: str = Field(min_length=10, max_length=2000)
    sections: list[Section] = Field(min_length=1, max_length=30)
    steps: list[dict[str, str]] | None = Field(default=None, max_length=50)
    endpoints: list[dict[str, str]] | None = Field(default=None, max_length=50)
    threats: list[dict[str, str]] | None = Field(default=None, max_length=50)


class VersionInput(InputModel):
    number: str = Field(min_length=1, max_length=30, pattern=r"^[0-9]+\.[0-9]+(?:\.[0-9]+)?$")
    expires_at: datetime
    content: Content

    @field_validator("expires_at")
    @classmethod
    def timezone_required(cls, value):
        if value.tzinfo is None:
            raise ValueError("La fecha debe incluir zona horaria.")
        return value


class DocumentInput(VersionInput):
    title: str = Field(min_length=3, max_length=160)
    kind: Literal["RUNBOOK", "API", "SEGURIDAD"]
    classification: Literal["INTERNO", "RESTRINGIDO"]
    owner_id: str = Field(min_length=3, max_length=80)
    project_id: str = Field(min_length=3, max_length=80)


class RenameDocument(InputModel):
    title: str = Field(min_length=3, max_length=160)
    expected_revision: int = Field(ge=1)


class ContentUpdate(InputModel):
    content: Content
    expected_revision: int = Field(ge=1)


class RequestInput(InputModel):
    version_id: str = Field(min_length=3, max_length=80)


class ApprovalInput(InputModel):
    kind: Literal["TECNICA", "SEGURIDAD", "PROPIETARIO"]
