from app.models import Task
from app.config import settings

from fastapi import HTTPException

from sqlalchemy import select, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

import mysql.connector

# These functions know which database table to work on because the Task class is an SQLAlchemy ORM model that defines:
# __tablename__ = "tasks"
# This tells SQLAlchemy that instances of Task map to rows in the tasks table.
def get_tasks(db: Session):
    try:
        statement = select(Task)
        return db.scalars(statement).all()
    except SQLAlchemyError as e:
        # Log
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def create_task(db: Session, title: str):
    try:
        task = Task(title=title)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


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

# This queries group members in the replication groups
def get_replication_members(db: Session):
    query = text("""
        SELECT * 
        FROM performance_schema.replication_group_members;
    """)
    result = db.execute(query)

    return [dict(row._mapping) for row in result]

# TODO: Create a function that queries certain metrics in system tables after reading what they contain

# An example that queries the sys schema using mysql.connector
def get_top_slow_queries():
    try:
        connection = mysql.connector.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            database="sys"
        )
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT query, exec_count, avg_latency, digest
        FROM statement_analysis
        ORDER BY avg_latency DESC
        LIMIT 5;
        """

        cursor.execute(query)
        results = cursor.fetchall()

        return results
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()