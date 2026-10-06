# ============================================================
# STEP 1: IMPORTS
# ============================================================

from pydantic import BaseModel


# ============================================================
# STEP 2: RESOLUTION RESULT SCHEMA
# ============================================================

class ResolutionResult(BaseModel):
    root_cause: str
    recommended_actions: list[str]
    requires_human_approval: bool
    escalation_required: bool
    escalation_team: str