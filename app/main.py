from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static") # put back when it's ready

@app.get("/")
async def read_root():
    return {"Hello": "World"}
