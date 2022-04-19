import pytest
from app.service import encode_url


def test_encode_url():
    sample_url = "https://github.com/mertsalik/short-url"
    assert len(encode_url(sample_url)) == 6


def test_encode_url_digit_count():
    sample_url = "https://github.com/mertsalik/short-url"
    digits = 8
    assert len(encode_url(url=sample_url, char_count=digits)) == digits


def test_encode_url_invalid_input():
    sample_url = None
    with pytest.raises(ValueError):
        encode_url(url=sample_url) is None


def test_encode_multiple_urls():
    sample_urls = [
        "https://github.com/mertsalik/short-url",
        "https://github.com/mertsalik/",
        "https://github.com/",
        "https://www.github.com/",
    ]
    outputs = []
    for url in sample_urls:
        outputs.append(encode_url(url))

    assert len(outputs) == len(sample_urls)
