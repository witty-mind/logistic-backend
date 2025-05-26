from fastapi import FastAPI

from app.api.v1.api import api_router

app = FastAPI(title="My FastAPI App", version="0.1.0")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to My FastAPI App"}
