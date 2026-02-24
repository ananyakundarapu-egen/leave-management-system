from google.cloud import bigquery
import smtplib
from email.mime.text import MIMEText
import os

PROJECT_ID = "project-45eaedf1-7f1d-433f-ab2"
DATASET = "leave_management"
TABLE = "leaves"
USERS_TABLE = f"{PROJECT_ID}.{DATASET}.users"

client = bigquery.Client()


def send_email(to_email, leave_details):
    sender_email = os.environ.get("SENDER_EMAIL")
    app_password = os.environ.get("EMAIL_APP_PASSWORD")

    total_leaves = len(leave_details)

    subject = f"{total_leaves} Pending Leave Request(s) – Action Required"

    table_rows = ""
    display_limit = 10

    for leave in leave_details[:display_limit]:
        table_rows += f"""
        <tr>
            <td>{leave['leave_id']}</td>
            <td>{leave['employee_id']}</td>
            <td>{leave['leave_type']}</td>
            <td>{leave['start_date']}</td>
        </tr>
        """

    more_text = ""
    if total_leaves > display_limit:
        more_count = total_leaves - display_limit
        more_text = f"<p><b>...and {more_count} more pending request(s).</b></p>"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>Pending Leave Requests</h2>

        <p>Hello,</p>

        <p>
            You currently have <b>{total_leaves} pending leave request(s)</b>
            awaiting your review.
        </p>

        <table border="1" cellpadding="8" cellspacing="0"
               style="border-collapse: collapse; width: 100%;">
            <thead style="background-color: #f2f2f2;">
                <tr>
                    <th>Leave ID</th>
                    <th>Employee ID</th>
                    <th>Leave Type</th>
                    <th>Start Date</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>

        {more_text}

        <p style="margin-top:20px;">
            Please review and take necessary action in the Leave Management System.
        </p>

        <p style="color: gray; font-size: 12px;">
            This is an automated notification. Please do not reply to this email.
        </p>

        <p>
            Regards,<br>
            <b>Leave Management System</b>
        </p>
    </body>
    </html>
    """

    msg = MIMEText(html_body, "html")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print("Email sending failed:", str(e))


def notify_pending_leaves(request):

    query = f"""
    SELECT l.leave_id,
           l.employee_id,
           l.leave_type,
           l.start_date,
           u.manager_email
    FROM `{PROJECT_ID}.{DATASET}.{TABLE}` l
    JOIN `{USERS_TABLE}` u
    ON l.employee_id = u.employee_id
    WHERE l.status = 'Pending'
    """

    results = client.query(query).result()

    manager_map = {}

    for row in results:
        manager = row["manager_email"]

        if manager not in manager_map:
            manager_map[manager] = []

        manager_map[manager].append({
            "leave_id": row["leave_id"],
            "employee_id": row["employee_id"],
            "leave_type": row["leave_type"],
            "start_date": str(row["start_date"])
        })

    for manager_email, leaves in manager_map.items():
        send_email(manager_email, leaves)

    return "Notifications sent successfully"