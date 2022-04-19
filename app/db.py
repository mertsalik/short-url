from abc import ABC, abstractmethod
from typing import Any

from fastapi import Depends

from .config import Settings, get_settings


class AbstractStorage(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any:
        raise NotImplementedError()

    @abstractmethod
    async def save(self, key: str, value: Any):
        raise NotImplementedError()

    @abstractmethod
    async def remove(self, key: str):
        raise NotImplementedError()


class UrlStorage(AbstractStorage):
    def __init__(
        self,
        host: str,
        bucket_name: str,
        collection_name: str,
        scope_name: str,
        username: str,
        password: str,
    ):
        self.host = host
        self.bucket_name = bucket_name
        self.collection_name = collection_name
        self.scope_name = scope_name
        self.username = username
        self.password = password

    async def get(self, key: str) -> Any:
        raise NotImplementedError()

    async def save(self, key: str, value: Any):
        raise NotImplementedError()

    async def remove(self, key: str):
        raise NotImplementedError()


def get_url_storage(
    settings: Settings = Depends(get_settings),
) -> AbstractStorage:
    return UrlStorage(
        host=settings.db_host,
        bucket_name=settings.db_bucket_name,
        collection_name=settings.db_collection_name,
        scope_name=settings.db_scope_name,
        username=settings.db_username,
        password=settings.db_password,
    )
