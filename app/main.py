from typing import Any
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse

from pydantic import BaseModel, AnyHttpUrl


class OriginalURLInput(BaseModel):
    original_url: AnyHttpUrl


def encode_url(url: str) -> str:
    """compute a unique hash of the given URL
    Parameters
    ----------
    url: str

    Return
    ------
    str
    """
    raise NotImplementedError()


class UrlStorage:
    async def get(self, key: str) -> Any:
        raise NotImplementedError()

    async def save(self, key: str, value: Any):
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

    async def get_original_url(self, unique_id: str) -> str:
        """Get original url from the storage if exists.

        Parameters
        ----------
        unique_id: str
            path parameter of the shortened url

        Return
        ------
        str
            original url of the given unique identifier
        """

        storage = UrlStorage()
        original_url = await storage.get(key=unique_id)
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


@app.get("/u/{unique_id}")
async def access_url(unique_id: str):
    service = URLShorteningService()
    original_url = await service.get_original_url(unique_id=unique_id)
    return RedirectResponse(original_url, status_code=302)
