from app import models, crud
from app.db import engine, SessionLocal

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# Create all tables in database for all models that inherit from Base
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# This provides a db session to whatever function needs it and then closes it afterwards (when it returns to get_db())
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

@app.get("/users")
def read_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

@app.get("/processlist")
def read_processlist(db: Session = Depends(get_db)):
    return crud.get_processlist(db)

@app.get("/top_queries")
def read_top_queries(db: Session = Depends(get_db)):
    return crud.get_top_queries(db)

@app.get("/replication_members")
def read_replication_members(db: Session = Depends(get_db)):
    return crud.get_replication_members(db)

@app.get("/top_slow_queries")
def read_top_slow_queries():
    return crud.get_top_slow_queries()