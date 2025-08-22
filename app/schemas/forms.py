from pydantic import BaseModel, conint
from typing import Literal

class SecurityExceptionRequest(BaseModel):
    employee_id: str
    department: str
    device_type: Literal["Mac","Windows","Linux"]
    justification: str
    duration_days: conint(ge=1, le=90)
    data_sensitivity: Literal["Low","Medium","High"]

class PTORequest(BaseModel):
    employee_id: str
    manager_email: str
    days: conint(ge=1, le=30)
    reason: str
