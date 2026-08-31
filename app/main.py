from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.internal import router as internal_router

app = FastAPI()
app.include_router(internal_router)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).resolve().parent / "static"),
    name="static",
)


@app.get("/health")
def health():
    return {"status": "ok"}
