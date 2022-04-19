from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    db_host = ""
    db_username = ""
    db_password = ""
    db_bucket_name = ""
    db_scope_name = ""
    db_collection_name = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
