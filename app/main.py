from fastapi import FastAPI

from app.routes.internal import router as internal_router

app = FastAPI()
app.include_router(internal_router)


@app.get("/health")
def health():
    return {"status": "ok"}


