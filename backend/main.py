from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from routes import router as leave_router
from register import router as register_router

app = FastAPI()
app.include_router(register_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(leave_router)

@app.get("/")
def home():
    return {"message": "Leave Management Backend Running"}
