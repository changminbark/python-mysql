import os
from pydantic_settings import BaseSettings

# Load in .env 
from dotenv import load_dotenv
dotenv_path = os.path.join("../.env")
load_dotenv(dotenv_path)

class Settings(BaseSettings):
    db_host: str
    db_name: str
    mysql_user: str
    mysql_password: str
    db_port: str

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"

settings = Settings()
