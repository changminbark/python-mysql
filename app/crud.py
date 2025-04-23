from app.models import Task

from sqlalchemy import select
from sqlalchemy.orm import Session

def get_tasks(db: Session):
    statement = select(Task)
    return db.scalars(statement).all()

def create_task(db: Session, title: str):
    task = Task(title=title)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task