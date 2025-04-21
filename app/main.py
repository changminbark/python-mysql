from app import models, crud
from app.db import engine, SessionLocal

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# Create all tables in database for all models that inherit from Base
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/tasks")
def read_tasks(db: Session = Depends(get_db)):
    return crud.get_tasks(db)

@app.post("/tasks")
def add_task(title: str, db: Session = Depends(get_db)):
    return crud.create_task(db, title)

