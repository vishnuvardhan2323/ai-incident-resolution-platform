from pydantic import BaseModel
from typing import Any


class InvestigationResult(BaseModel):
    service: str
    health: dict[str, Any]
    logs: list[str]
    asset: dict[str, Any]
    findings: list[str]