from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "BizzyText SaaS is alive!"}
