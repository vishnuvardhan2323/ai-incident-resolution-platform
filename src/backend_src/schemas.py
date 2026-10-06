# ============================================================
# STEP 1: IMPORTS
# ============================================================

from typing import Any
from pydantic import BaseModel


# ============================================================
# STEP 2: INCIDENT REQUEST
# ============================================================

class IncidentRequest(BaseModel):
    incident: str


# ============================================================
# STEP 3: INCIDENT RESPONSE
# ============================================================

class IncidentResponse(BaseModel):
    route: str
    classification: dict[str, Any]
    knowledge: dict[str, Any]
    investigation: dict[str, Any] | None = None
    resolution: dict[str, Any] | None = None
    requires_human_approval: bool


# ============================================================
# STEP 4: APPROVED ACTION REQUEST
# ============================================================

class ApprovedActionRequest(BaseModel):
    service_name: str
    action: str
    approved: bool


# ============================================================
# STEP 5: ACTION RESPONSE
# ============================================================

class ActionResponse(BaseModel):
    service_name: str
    action: str
    approval_status: str
    execution_status: str
    message: str