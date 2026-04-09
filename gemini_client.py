from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.upload import router as upload_router
from app.api.interview import router as interview_router

app = FastAPI(
    title="InterviewAI API",
    version="0.1.0",
    description="Backend для AI-тренажёра собеседований",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(interview_router)


@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"},
    )


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
