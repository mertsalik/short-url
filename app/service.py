from base64 import b64encode
from hashlib import md5

from .db import AbstractStorage


def encode_url(url: str, char_count: int = 6) -> str:
    """create N (default=6) digit alias string for the given URL string
    Its not unique, try changing the url parameter ( add more path parameters )
    in consecutive calls in order to achive uniqueness.

    first 6 characters of ( base64 ( md5( url ) )  )

    Parameters
    ----------
    url: str

    Return
    ------
    str
    """
    if not url:
        raise ValueError("Empty url string can't be encoded!") from None
    return b64encode(md5(url.encode("utf-8")).digest()).decode()[:char_count]


class URLShorteningService:
    def __init__(self, storage: AbstractStorage) -> None:
        self.storage = storage

    async def shorten(self, original_url: str) -> str:
        """Shorten a url.

        Parameters
        ----------
        original_url: str
            url to be shortened

        Return
        ------
        str
            Shortened url
        """
        unique_identifier = encode_url(url=original_url)
        data = {"url": original_url}
        try:
            await self.storage.save(key=unique_identifier, value=data)
        except Exception:
            # TODO: what if multiple users encodes the same URL ?
            raise

        return unique_identifier

    async def get_original_url(self, url_key: str) -> str:
        """Get original url from the storage if exists.

        raises: couchbase.exceptions.DocumentNotFoundException

        Parameters
        ----------
        url_key: str
            path parameter of the shortened url

        Return
        ------
        str
            original url of the given unique identifier
        """
        data = await self.storage.get(key=url_key)
        return data.get('url')

    async def delete_url(self, url_key: str):
        """Deactivate given short-url from the system.

        Parameters
        ----------
        url_key: str
            path parameter of the shortened url
        """
        original_url = await self.storage.remove(key=url_key)
        return original_url
