from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.exceptions import global_exception_handler
from app.api.routes import router


app = FastAPI(
    title="Main Core AI Engineer",
    version="1.0.0"
)


app.exception_handler(Exception)(global_exception_handler)  

# CORS untuk Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/")
async def root():
    return {
        "message": "Welcome Main Core AI Engineer"
    }