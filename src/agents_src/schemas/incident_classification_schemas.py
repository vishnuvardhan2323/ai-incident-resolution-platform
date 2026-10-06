from pydantic import BaseModel


class IncidentClassification(BaseModel):
    service: str
    category: str
    severity: str
    intent: str