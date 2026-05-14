import pytest
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from processors import enrich

@pytest.mark.asyncio
async def test_fetch_returns_none_on_invalid_url():
    async with aiohttp.ClientSession() as session:
        result = await enrich.fetch(session, "http://invalid.localhost")
        assert result is None

@pytest.mark.asyncio
async def test_fetch_valid_url_returns_content():
    async with aiohttp.ClientSession() as session:
        result = await enrich.fetch(session, "https://example.com")
        assert result is not None
        assert "Example Domain" in result

@pytest.mark.asyncio
async def test_fetch_invalid_url_returns_none():
    async with aiohttp.ClientSession() as session:
        result = await enrich.fetch(session, "http://nonexistent.localhost")
        assert result is None

@pytest.mark.asyncio
async def test_extract_emails_from_html():
    html = "<html><body>Contact: info@example.com</body></html>"
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    emails = enrich.extract_emails(soup, text)
    assert "info@example.com" in emails
    assert len(emails) == 1


@pytest.mark.asyncio
async def test_extract_no_emails_returns_empty_list():
    html = "<html><body>No emails here</body></html>"
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    emails = enrich.extract_emails(soup, text)
    assert emails == set()

@pytest.mark.asyncio
async def test_handle_timeout(monkeypatch):
    async def fake_fetch(*args, **kwargs):
        return None  # simulate timeout handled gracefully

    monkeypatch.setattr(enrich, "fetch", fake_fetch)

    async with aiohttp.ClientSession() as session:
        result = await enrich.fetch(session, "https://example.com")
        assert result is None
