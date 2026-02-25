from unittest import result
from fastapi import APIRouter, Depends, HTTPException
from models import LeaveCreate, Leave
from security import get_current_user
from datetime import datetime

from bigquery_db import (
    insert_leave,
    get_all_leaves,
    get_employee_leaves,
    update_leave_status,
    cancel_leave_db,
    get_leave_by_id,
    get_user,
    insert_user_if_not_exists,
    update_leave
)

router = APIRouter()

@router.post("/apply-leave")
def apply_leave(leave: LeaveCreate, user=Depends(get_current_user)):
    if user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Employees only")

    leave_dict = leave.dict()
    user_record = get_user(user["username"])

    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    leave_dict["employee_id"] = user_record["employee_id"]
    return insert_leave(leave_dict)


@router.get("/my-leaves")
def get_my_leaves(user=Depends(get_current_user)):

    if user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Employees only")

    user_record = get_user(user["username"])
    print("Logged in employee_id:", user_record["employee_id"])

    leaves = get_employee_leaves(user_record["employee_id"])

    return leaves

@router.delete("/cancel/{leave_id}")
def cancel_leave(leave_id: str, user=Depends(get_current_user)):
    if user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Employees only")
    leave = get_leave_by_id(leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave not found")
    leave_start = leave["start_date"]
    if isinstance(leave_start, str):
        leave_start = datetime.strptime(leave_start, "%Y-%m-%d").date()

    if leave_start < datetime.utcnow().date():
        raise HTTPException(
            status_code=400,
            detail="Cannot withdraw leave that has already started"
        )
    return cancel_leave_db(leave_id)

@router.get("/all-leaves")
def get_leaves(user=Depends(get_current_user)):

    if user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Managers only")

    return get_all_leaves()

@router.put("/approve/{leave_id}")
def approve_leave(leave_id: str, user=Depends(get_current_user)):

    if user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Managers only")

    return update_leave_status(leave_id, "Approved")

@router.put("/reject/{leave_id}")
def reject_leave(leave_id: str, user=Depends(get_current_user)):

    if user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Managers only")

    return update_leave_status(leave_id, "Rejected")

@router.get("/user/{email}")
def get_user_details(email: str):
    from bigquery_db import get_user
    user = get_user(email)

    if not user:
        return {"first_name": "", "last_name": ""}

    return user

@router.post("/check-employee-id")
def check_employee_id(data: dict):
    employee_id = data.get("employee_id")

    if not employee_id:
        raise HTTPException(status_code=400, detail="Employee ID required")

    from bigquery_db import get_user_by_employee_id

    user = get_user_by_employee_id(employee_id)

    if user:
        return {"exists": True}

    return {"exists": False}

@router.put("/update/{leave_id}")
def update_leave_route(leave_id: str, leave: LeaveCreate, user=Depends(get_current_user)):

    if user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Employees only")

    existing_leave = get_leave_by_id(leave_id)

    if not existing_leave:
        raise HTTPException(status_code=404, detail="Leave not found")

    leave_start = existing_leave["start_date"]
    if isinstance(leave_start, str):
        leave_start = datetime.strptime(leave_start, "%Y-%m-%d").date()

    if leave_start < datetime.utcnow().date():
        raise HTTPException(
            status_code=400,
            detail="Cannot edit leave that has already started"
        )

    leave_dict = leave.dict()
    user_record = get_user(user["username"])
    leave_dict["employee_id"] = user_record["employee_id"]

    return update_leave(leave_id, leave_dict)

@router.get("/user-session")
def user_session(user=Depends(get_current_user)):
    return {
        "username": user["username"],
        "role": user["role"]
    }