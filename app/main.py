from fastapi import FastAPI
from app.config import APP_NAME
from app.api.routes import router

app = FastAPI(title=APP_NAME)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "YATI operativo",
        "docs": "/docs"
    }
