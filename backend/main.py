from fastapi import FastAPI

app = FastAPI(title="Adelaide Travel Agent")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}