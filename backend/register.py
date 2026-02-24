from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from firebase_admin import auth as firebase_auth
from firebase_admin_init import *
from bigquery_db import insert_user_if_not_exists
from security import create_access_token
import re

router = APIRouter()

class FirebaseRegister(BaseModel):
    id_token: str
    first_name: str
    last_name: str
    employee_id: str


@router.post("/register")
def register(data: FirebaseRegister, response: Response):

    try:
        decoded_token = firebase_auth.verify_id_token(data.id_token)
        email = decoded_token.get("email")

        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        employee_id = data.employee_id.strip().upper()

        if not re.match(r"^EMP\d+$", employee_id):
            raise HTTPException(
                status_code=400,
                detail="Employee ID must start with EMP followed by numbers (e.g., EMP001)"
            )

        result = insert_user_if_not_exists(
            email,
            data.first_name,
            data.last_name,
            employee_id
        )

        if isinstance(result, dict) and "error" in result:
            raise HTTPException(
                status_code=409,
                detail=result["error"]
            )

        role = "employee"

        access_token = create_access_token({
            "sub": email,
            "role": role
        })

        response.set_cookie(
            key="session",
            value=access_token,
            httponly=True,
            samesite="lax",
            secure=False,
            path="/"
        )

        return {
            "username": email,
            "role": role
        }

    except HTTPException:
        raise

    except Exception as e:
        print("REGISTER ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail="Registration failed due to server error"
        )