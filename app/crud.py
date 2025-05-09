from app.models import Task
from app.config import settings

from pint import UnitRegistry

from fastapi import HTTPException

from sqlalchemy import select, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

import mysql.connector

ureg = UnitRegistry()

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

        # Rows are already sorted by descending total latency by default
        query = """
        SELECT query, exec_count, avg_latency, digest
        FROM statement_analysis
        LIMIT 5;
        """

        cursor.execute(query)
        results = cursor.fetchall()
        # TODO: Maybe process data and print to a CSV file

        return results
    
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_top_slow_tables(db: Session):
    query = text("""
    SELECT table_schema, table_name, fetch_latency, insert_latency, update_latency, delete_latency, io_read_latency, io_write_latency, io_misc_latency
    FROM sys.schema_table_statistics_with_buffer
    LIMIT 5;
    """)

    # Already sorted by total wait time
    result = db.execute(query)
    result = [dict(row._mapping) for row in result]

    for row in result:
        fetch_t = ureg(row["fetch_latency"] if row["fetch_latency"] is not None else "0 ps")
        insert_t = ureg(row["insert_latency"] if row["insert_latency"] is not None else "0 ps")
        update_t = ureg(row["update_latency"] if row["update_latency"] is not None else "0 ps")
        delete_t = ureg(row["delete_latency"] if row["delete_latency"] is not None else "0 ps")
        io_read_t = ureg(row["io_read_latency"] if row["io_read_latency"] is not None else "0 ps")
        io_write_t = ureg(row["io_write_latency"] if row["io_write_latency"] is not None else "0 ps")
        io_misc_t = ureg(row["io_misc_latency"] if row["io_misc_latency"] is not None else "0 ps")

        total_latency = (
            fetch_t +
            insert_t +
            update_t +
            delete_t +
            io_read_t +
            io_write_t +
            io_misc_t
        )

        # Convert to milliseconds
        row["total_latency_ms"] = f"{total_latency.to('microseconds').magnitude:.2f} us"
    
    return result