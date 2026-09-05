from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend is running"}

@app.get("/api/test")
def test():
    return {"status": "success"}

@app.get("/api/confirm")
def confirm():
    return {
        "success": True,
        "message": "Frontend successfully connected to FastAPI!"
    }