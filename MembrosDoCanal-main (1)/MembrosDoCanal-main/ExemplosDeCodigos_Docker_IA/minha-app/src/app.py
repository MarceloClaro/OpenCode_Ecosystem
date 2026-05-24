from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok", "msg": "Hello from Docker!"}


@app.get("/health")
def health():
    return {"status": "healthy"}
