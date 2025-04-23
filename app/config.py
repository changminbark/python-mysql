import os
from pydantic_settings import BaseSettings

# Load in .env (for local testing)
from dotenv import load_dotenv
dotenv_path = os.path.join("../.env")
load_dotenv(dotenv_path)

# This saves the environment variables in this class
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

