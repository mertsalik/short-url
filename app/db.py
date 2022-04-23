from abc import ABC, abstractmethod
from typing import Any

from couchbase.bucket import Bucket
from couchbase.cluster import (
    Cluster,
    Authenticator,
    PasswordAuthenticator,
    ClusterOptions,
    LockMode,
)

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
        port: str,
        bucket_name: str,
        collection_name: str,
        scope_name: str,
        username: str,
        password: str,
    ):
        self.host = host
        self.port = port
        self.bucket_name = bucket_name
        self.collection_name = collection_name
        self.scope_name = scope_name
        self.username = username
        self.password = password

    def get_connection_string(self) -> str:
        """build connection string from configurations (environment)"""
        return f"couchbase://{self.host}:{self.port}"

    def get_authenticator(self) -> Authenticator:
        """create a Couchbase authenticator using configuration settings"""
        return PasswordAuthenticator(self.username, self.password)

    def get_bucket(self) -> Bucket:
        """initialize and return a Couchbase bucket"""
        cluster = Cluster(
            connection_string=self.get_connection_string(),
            options=ClusterOptions(
                authenticator=self.get_authenticator(), lockmode=LockMode.EXC
            ),
        )
        return cluster.bucket(self.bucket_name)

    async def get(self, key: str) -> Any:
        bucket = self.get_bucket()
        collection = bucket.default_collection()
        return collection.get(key)

    async def save(self, key: str, value: Any):
        bucket = self.get_bucket()
        collection = bucket.default_collection()
        collection.insert(key, value)

    async def remove(self, key: str):
        bucket = self.get_bucket()
        collection = bucket.default_collection()
        collection.remove(key)


def get_url_storage(
    settings: Settings = Depends(get_settings),
) -> AbstractStorage:
    return UrlStorage(
        host=settings.db_host,
        port=settings.db_port,
        bucket_name=settings.db_bucket_name,
        collection_name=settings.db_collection_name,
        scope_name=settings.db_scope_name,
        username=settings.db_username,
        password=settings.db_password,
    )
