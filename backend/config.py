from pydantic import BaseSettings


class Settings(BaseSettings):
    TESTING: bool = False
    IMMUDB_API_URL: str = ""
    KAFKA_SERVER_URL: str = ""
    DB_SRV: str = ""
    AWS_KEY: str = ""
    AWS_SECRET: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Settings()
