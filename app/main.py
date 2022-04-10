from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse

from pydantic import BaseModel


class OriginalURLInput(BaseModel):
    original_url: str


class URLShorteningService:
    async def shorten(self, original_url: str) -> str:
        raise NotImplementedError()

    async def get_original_url(self, unique_id: str) -> str:
        raise NotImplementedError()


app = FastAPI()


@app.get("/")
async def root():
    return {"Project": "Short URL!"}


@app.post("/url")
async def shorten_url(url_input: OriginalURLInput):
    service = URLShorteningService()
    shortened_url = await service.shorten(original_url=url_input.original_url)
    print(shortened_url)
    content = {"ShortURL": shortened_url}
    return JSONResponse(status_code=201, content=content)


@app.get("/u/{unique_id}")
async def access_url(unique_id: str):
    service = URLShorteningService()
    original_url = await service.get_original_url(unique_id=unique_id)
    return RedirectResponse(original_url, status_code=302)
