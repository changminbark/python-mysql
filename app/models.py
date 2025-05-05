from sqlalchemy import Column, Integer, String, Boolean, MetaData
from app.db import Base

# This task model inherits from the declarative_base class
# It defines a schema of how an entry in a table, which has a name of "tasks"
# should look like
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    completed = Column(Boolean, default=False)