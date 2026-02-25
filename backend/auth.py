from fastapi import APIRouter, HTTPException, status, Body, Response, Depends
from pydantic import BaseModel
from firebase_admin import auth as firebase_auth
from firebase_admin_init import *   
from security import create_access_token, get_current_user
from google.cloud import bigquery
from bigquery_db import get_user

router = APIRouter()

PROJECT_ID = "project-45eaedf1-7f1d-433f-ab2"
DATASET = "leave_management"
USERS_TABLE = f"{PROJECT_ID}.{DATASET}.users"

bq_client = bigquery.Client()

class FirebaseLogin(BaseModel):
    id_token: str

@router.post("/login")
def login(data: FirebaseLogin, response: Response):
    try:
        decoded_token = firebase_auth.verify_id_token(data.id_token)

        email = decoded_token.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid Firebase token")

        query = f"""
        SELECT role FROM `{USERS_TABLE}`
        WHERE email = @email
        LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("email", "STRING", email)
            ]
        )

        results = list(bq_client.query(query, job_config=job_config).result())

        if len(results) == 0:
            raise HTTPException(status_code=404, detail="User not registered")

        role = results[0]["role"]

        access_token = create_access_token({
            "sub": email,
            "role": role
        })

        response.set_cookie(
            key="session",
            value=access_token,
            httponly=True,
            samesite="none",
            secure=True,
            path="/"
        )

        return {
            "username": email,
            "role": role
        }

    except Exception as e:
        print("FIREBASE LOGIN ERROR:", e)
        raise HTTPException(status_code=401, detail="Token verification failed")

@router.post("/signup")
def signup(data = Body(...)):
    try:
        id_token = data.get("id_token")
        first_name = data.get("first_name")
        last_name = data.get("last_name")

        if not id_token:
            raise HTTPException(status_code=400, detail="Token missing")

        decoded_token = firebase_auth.verify_id_token(id_token)
        email = decoded_token.get("email")

        if not email:
            raise HTTPException(status_code=401, detail="Invalid Firebase token")

        check_query = f"""
        SELECT email FROM `{USERS_TABLE}`
        WHERE email = @email
        LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("email", "STRING", email)
            ]
        )

        existing = list(bq_client.query(check_query, job_config=job_config).result())

        if len(existing) > 0:
            return {"message": "User already exists"}

        insert_query = f"""
        INSERT INTO `{USERS_TABLE}` (email, first_name, last_name, role)
        VALUES (@email, @first_name, @last_name, 'employee')
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("email", "STRING", email),
                bigquery.ScalarQueryParameter("first_name", "STRING", first_name),
                bigquery.ScalarQueryParameter("last_name", "STRING", last_name),
            ]
        )

        bq_client.query(insert_query, job_config=job_config).result()

        return {"message": "Signup successful"}

    except Exception as e:
        print("FIREBASE SIGNUP ERROR:", e)
        raise HTTPException(status_code=401, detail="Signup failed")
    
@router.get("/user-session")
def user_session(user = Depends(get_current_user)):
    return {
        "username": user["username"],
        "role": user["role"]
    }