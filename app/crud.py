from app.models import Task

from sqlalchemy import select, text
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

# This queries all of the users and host from the user table in the mysql db
def get_users(db: Session):
    query = text("""
        SELECT User, Host FROM mysql.user;
    """)
    result = db.execute(query)

    # This is to convert row objects into serializable dictionaries
    return [dict(row._mapping) for row in result]

# This queries all of the process metadata from the PROCESSLIST table in the information_schema db
def get_processlist(db: Session):
    query = text("""
        SELECT ID, USER, HOST, DB, COMMAND, TIME, STATE, INFO
        FROM information_schema.PROCESSLIST;
    """)
    result = db.execute(query)

    return [dict(row._mapping) for row in result]

# This queries all of the top queries from the events_statements_summary_by_digest table in the performance_schema db
def get_top_queries(db: Session):
    db.execute(text("USE performance_schema;"))
    query = text("""
        SELECT DIGEST_TEXT, COUNT_STAR, SUM_TIMER_WAIT
        FROM events_statements_summary_by_digest
        ORDER BY SUM_TIMER_WAIT DESC
        LIMIT 5;
    """)
    result = db.execute(query)

    return [dict(row._mapping) for row in result]