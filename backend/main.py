from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Technical Interview Platform API"}