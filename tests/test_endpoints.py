import pytest
from httpx import AsyncClient
from unittest.mock import patch

from app.main import app


@pytest.mark.anyio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Project": "Short URL!"}


@pytest.mark.anyio
@patch("app.main.URLShorteningService.get_original_url")
async def test_access_url(mock_get_original_url):
    mock_get_original_url.side_effect = "https://test.com/long-url"

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/u/SHORT-ALIAS")

    assert response.status_code == 302


@pytest.mark.anyio
@patch("app.main.URLShorteningService.shorten")
async def test_shorten_url(mock_shorten):
    async def mock_return(*args, **kwargs):
        return "/u/SHORT-ALIAS"

    mock_shorten.side_effect = mock_return

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            url="/url",
            json={"original_url": "https://test.com/my-long-url"},
        )

    assert response.status_code == 201
    assert response.json() == {"ShortURL": "/u/SHORT-ALIAS"}
