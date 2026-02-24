from pydantic import BaseModel
from datetime import date

class LeaveCreate(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    
class Leave(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: str
