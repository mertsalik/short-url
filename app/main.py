from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse

from pydantic import BaseModel, AnyHttpUrl

from .service import URLShorteningService
from .db import get_url_storage


class OriginalURLInput(BaseModel):
    original_url: AnyHttpUrl


app = FastAPI()


@app.get("/")
async def root():
    return {"Project": "Short URL!"}


@app.post("/url")
async def shorten_url(
    url_input: OriginalURLInput, storage=Depends(get_url_storage)
):  # NOQA
    service = URLShorteningService(storage=storage)
    shortened_url = await service.shorten(original_url=url_input.original_url)
    content = {"ShortURL": shortened_url}
    return JSONResponse(status_code=201, content=content)


@app.delete("/url/{url_key}")
async def delete_url(url_key: str, storage=Depends(get_url_storage)):
    service = URLShorteningService(storage=storage)
    original_url = await service.get_original_url(url_key=url_key)
    if not original_url:
        raise HTTPException(status_code=404, detail="Url not found!")
    await service.delete_url(url_key=url_key)
    return JSONResponse(status_code=204)


@app.get("/u/{url_key}")
async def access_url(url_key: str, storage=Depends(get_url_storage)):  # NOQA
    service = URLShorteningService(storage=storage)
    original_url = await service.get_original_url(url_key=url_key)
    return RedirectResponse(original_url, status_code=302)
