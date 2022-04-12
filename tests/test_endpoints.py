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


@pytest.mark.anyio
async def test_shorten_invalid_url():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            url="/url",
            json={"original_url": "invalid-url-foo"},
        )

    assert response.status_code == 422


@pytest.mark.anyio
@patch("app.main.URLShorteningService.delete_url")
@patch("app.main.URLShorteningService.get_original_url")
async def test_delete_url_success(mock_get_original_url, mock_delete_url):
    async def mock_return_none(*args, **kwargs):
        return None

    async def mock_return_something(*args, **kwargs):
        return "http://test.com/some-long-url/foo"

    mock_delete_url.side_effect = mock_return_none
    mock_get_original_url.side_effect = mock_return_something
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(url="/url/FOO-BAR")
    assert response.status_code == 204


@pytest.mark.anyio
@patch("app.main.URLShorteningService.get_original_url")
async def test_delete_url_not_found(mock_get_original_url):
    async def mock_return(*args, **kwargs):
        return None

    mock_get_original_url.side_effect = mock_return

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(url="/url/FOO-BAR")
    assert response.status_code == 404
