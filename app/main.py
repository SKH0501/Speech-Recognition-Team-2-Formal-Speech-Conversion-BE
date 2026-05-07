from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.sessions import router as sessions_router


app = FastAPI(title="Honorific Speech Trainer Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 데모용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router)


@app.get("/api/health")
def health():
    return {"success": True, "data": {"status": "ok"}}


@app.get("/api/categories")
def categories():
    return {
        "success": True,
        "data": [
            {"id": "food", "name": "밥"},
            {"id": "name", "name": "이름"},
            {"id": "home", "name": "집"},
        ]
    }