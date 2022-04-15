from typing import Any

from hashlib import md5
from base64 import b64encode

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse

from pydantic import BaseModel, AnyHttpUrl


class OriginalURLInput(BaseModel):
    original_url: AnyHttpUrl


def encode_url(url: str, char_count: int = 6) -> str:
    """create N (default=6) digit alias string for the given URL string
    Its not unique, try changing the url parameter ( add more path parameters ) in consecutive
    calls in order to achive uniqueness.

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


class UrlStorage:
    async def get(self, key: str) -> Any:
        raise NotImplementedError()

    async def save(self, key: str, value: Any):
        raise NotImplementedError()

    async def remove(self, key: str):
        raise NotImplementedError()


class URLShorteningService:
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
        storage = UrlStorage()
        try:
            await storage.save(key=unique_identifier, value=original_url)
        except Exception:
            # TODO: what if multiple users encodes the same URL ?
            raise

        return unique_identifier

    async def get_original_url(self, url_key: str) -> str:
        """Get original url from the storage if exists.

        Parameters
        ----------
        url_key: str
            path parameter of the shortened url

        Return
        ------
        str
            original url of the given unique identifier
        """

        storage = UrlStorage()
        original_url = await storage.get(key=url_key)
        return original_url

    async def delete_url(self, url_key: str):
        """Deactivate given short-url from the system.

        Parameters
        ----------
        url_key: str
            path parameter of the shortened url
        """
        storage = UrlStorage()
        original_url = await storage.remove(key=url_key)
        return original_url


app = FastAPI()


@app.get("/")
async def root():
    return {"Project": "Short URL!"}


@app.post("/url")
async def shorten_url(url_input: OriginalURLInput):
    service = URLShorteningService()
    shortened_url = await service.shorten(original_url=url_input.original_url)
    content = {"ShortURL": shortened_url}
    return JSONResponse(status_code=201, content=content)


@app.delete("/url/{url_key}")
async def delete_url(url_key: str):
    service = URLShorteningService()
    original_url = await service.get_original_url(url_key=url_key)
    if not original_url:
        raise HTTPException(status_code=404, detail="Url not found!")
    await service.delete_url(url_key=url_key)
    return JSONResponse(status_code=204)


@app.get("/u/{url_key}")
async def access_url(url_key: str):
    service = URLShorteningService()
    original_url = await service.get_original_url(url_key=url_key)
    return RedirectResponse(original_url, status_code=302)
