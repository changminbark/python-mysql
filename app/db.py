from app.config import settings

import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

SQL_ALCHEMY_DB_URL = f"mysql+pymysql://{settings.mysql_user}:{settings.mysql_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

# Retry loop
for i in range(10):
    try:
        engine = create_engine(SQL_ALCHEMY_DB_URL)
        engine.connect()
        print("Database connection successful")
        break
    except OperationalError as e:
        print(f"Waiting for database... ({i+1}/10)")
        time.sleep(2)
else:
    raise Exception("Could not connect to the database after 10 tries")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()