from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from routes import router as leave_router
from register import router as register_router

app = FastAPI()

origins = [
    "http://localhost:4200",
    "https://leave-frontend-371946530630.us-central1.run.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(register_router)
app.include_router(auth_router)
app.include_router(leave_router)

@app.get("/")
def home():
    return {"message": "Leave Management Backend Running"}