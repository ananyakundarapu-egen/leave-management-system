from google.cloud import bigquery
from datetime import datetime
import uuid
from google.api_core.exceptions import BadRequest
import time
from fastapi import HTTPException

PROJECT_ID = "project-45eaedf1-7f1d-433f-ab2"
DATASET = "leave_management"
TABLE = "leaves"

client = bigquery.Client(project=PROJECT_ID)
table_id = f"{PROJECT_ID}.{DATASET}.{TABLE}"
USERS_TABLE = f"{PROJECT_ID}.{DATASET}.users"

def insert_leave(data):

    if has_overlapping_leave(
        data["employee_id"],
        data["start_date"],
        data["end_date"]
    ):
        raise HTTPException(
            status_code=400,
            detail="Leave dates overlap with existing leave"
        )

    insert_query = f"""
    INSERT INTO `{table_id}`
    (leave_id, employee_id, leave_type, start_date, end_date, reason, status, created_at)
    VALUES
    (@leave_id, @employee_id, @leave_type, @start_date, @end_date, @reason, 'Pending', @created_at)
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("leave_id", "STRING", str(uuid.uuid4())[:8]),
            bigquery.ScalarQueryParameter("employee_id", "STRING", data["employee_id"]),
            bigquery.ScalarQueryParameter("leave_type", "STRING", data["leave_type"]),
            bigquery.ScalarQueryParameter("start_date", "DATE", data["start_date"]),
            bigquery.ScalarQueryParameter("end_date", "DATE", data["end_date"]),
            bigquery.ScalarQueryParameter("reason", "STRING", data["reason"]),
            bigquery.ScalarQueryParameter("created_at", "TIMESTAMP", datetime.utcnow()),
        ]
    )

    client.query(insert_query, job_config=job_config).result()

    return {"message": "Leave applied successfully"}

def get_all_leaves():
    query = f"""
    SELECT *
    FROM `{table_id}`
    ORDER BY created_at DESC
    """
    results = client.query(query).result()
    return [dict(row) for row in results]

def get_employee_leaves(employee_id):

    query = f"""
    SELECT *
    FROM `{table_id}`
    WHERE employee_id = @employee_id
    ORDER BY created_at DESC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("employee_id", "STRING", employee_id)
        ]
    )

    results = client.query(query, job_config=job_config).result()
    return [dict(row) for row in results]

def update_leave_status(leave_id, new_status):

    update_query = f"""
    UPDATE `{table_id}`
    SET status = @status
    WHERE leave_id = @leave_id
    AND status = 'Pending'
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("status", "STRING", new_status),
            bigquery.ScalarQueryParameter("leave_id", "STRING", leave_id),
        ]
    )

    result = client.query(update_query, job_config=job_config).result()

    if result.num_dml_affected_rows == 0:
        raise HTTPException(
            status_code=400,
            detail="Only pending leaves can be modified"
        )

    return {"message": f"Leave {new_status.lower()} successfully"}


def has_overlapping_leave(employee_id, new_start, new_end, leave_id=None):

    query = f"""
    SELECT COUNT(*) as count
    FROM `{table_id}`
    WHERE employee_id = @employee_id
    AND status IN ('Pending', 'Approved')
    AND (@new_start <= end_date AND @new_end >= start_date)
    """

    params = [
        bigquery.ScalarQueryParameter("employee_id", "STRING", employee_id),
        bigquery.ScalarQueryParameter("new_start", "DATE", new_start),
        bigquery.ScalarQueryParameter("new_end", "DATE", new_end),
    ]

    if leave_id:
        query += " AND leave_id != @leave_id"
        params.append(
            bigquery.ScalarQueryParameter("leave_id", "STRING", leave_id)
        )

    job_config = bigquery.QueryJobConfig(query_parameters=params)

    result = list(client.query(query, job_config=job_config).result())[0]
    return result["count"] > 0


def insert_user_if_not_exists(email, first_name, last_name, employee_id):

    MANAGER_EMAIL = "ananyakundarapu@gmail.com"

    check_email_query = f"""
    SELECT COUNT(*) as count
    FROM `{USERS_TABLE}`
    WHERE email = @email
    """

    job_config_email = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("email", "STRING", email)
        ]
    )

    email_result = list(
        client.query(check_email_query, job_config=job_config_email).result()
    )[0]

    if email_result["count"] > 0:
        return {"error": "Email already exists"}

    check_emp_query = f"""
    SELECT COUNT(*) as count
    FROM `{USERS_TABLE}`
    WHERE employee_id = @employee_id
    """

    job_config_emp = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("employee_id", "STRING", employee_id)
        ]
    )

    emp_result = list(
        client.query(check_emp_query, job_config=job_config_emp).result()
    )[0]

    if emp_result["count"] > 0:
        return {"error": "Employee ID already exists"}

    row = [{
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "employee_id": employee_id,
        "role": "employee",
        "manager_email": MANAGER_EMAIL,
        "created_at": datetime.utcnow().isoformat()
    }]

    errors = client.insert_rows_json(USERS_TABLE, row)

    if errors:
        print("USER INSERT ERROR:", errors)
        raise Exception("Database insert failed")

    return {"message": "User created successfully"}

def get_user(email):
    query = f"""
    SELECT *
    FROM `{USERS_TABLE}`
    WHERE email = @email
    LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("email", "STRING", email)
        ]
    )

    results = list(client.query(query, job_config=job_config).result())

    if len(results) == 0:
        return None

    return dict(results[0])

def get_user_role(email):
    query = f"""
    SELECT role
    FROM `{USERS_TABLE}`
    WHERE email = @email
    LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("email", "STRING", email)
        ]
    )

    results = list(client.query(query, job_config=job_config).result())

    if not results:
        return None

    return results[0]["role"]

def get_leave_by_id(leave_id):
    query = f"""
    SELECT *
    FROM `{table_id}`
    WHERE leave_id = @leave_id
    ORDER BY created_at DESC
    LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("leave_id", "STRING", leave_id)
        ]
    )

    results = list(client.query(query, job_config=job_config).result())

    return dict(results[0]) if results else None

def cancel_leave_db(leave_id):

    delete_query = f"""
    DELETE FROM `{table_id}`
    WHERE leave_id = @leave_id
    AND status = 'Pending'
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("leave_id", "STRING", leave_id),
        ]
    )

    result = client.query(delete_query, job_config=job_config).result()

    if result.num_dml_affected_rows == 0:
        raise HTTPException(
            status_code=400,
            detail="Only pending leaves can be withdrawn"
        )

    return {"message": "Leave withdrawn and deleted successfully"}

def update_leave(leave_id, data):

    if has_overlapping_leave(
        data["employee_id"],
        data["start_date"],
        data["end_date"],
        leave_id 
    ):
        raise HTTPException(
            status_code=400,
            detail="Leave dates overlap with existing leave"
        )

    update_query = f"""
    UPDATE `{table_id}`
    SET leave_type = @leave_type,
        start_date = @start_date,
        end_date = @end_date,
        reason = @reason
    WHERE leave_id = @leave_id
    AND status = 'Pending'
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("leave_id", "STRING", leave_id),
            bigquery.ScalarQueryParameter("leave_type", "STRING", data["leave_type"]),
            bigquery.ScalarQueryParameter("start_date", "DATE", data["start_date"]),
            bigquery.ScalarQueryParameter("end_date", "DATE", data["end_date"]),
            bigquery.ScalarQueryParameter("reason", "STRING", data["reason"]),
        ]
    )

    result = client.query(update_query, job_config=job_config).result()

    if result.num_dml_affected_rows == 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot edit this leave"
        )

    return {"message": "Leave updated successfully"}