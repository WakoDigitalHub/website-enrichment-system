import asyncio

# Regex patterns
import re

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from tqdm import tqdm

from config.settings import SCRAPER_SETTINGS

email_pattern = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")

facebook_pattern = re.compile(r"(https?://[a-zA-Z0-9\-\.]*facebook\.com/[^\s\"']+)")

instagram_pattern = re.compile(r"(https?://[a-zA-Z0-9\-\.]*instagram\.com/[^\s\"']+)")

linkedin_pattern = re.compile(r"(https?://[a-zA-Z0-9\-\.]*linkedin\.com/[^\s\"']+)")

twitter_pattern = re.compile(
    r"(https?://[a-zA-Z0-9\-\.]*twitter\.com/[^\s\"']+|"
    r"https?://[a-zA-Z0-9\-\.]*x\.com/[^\s\"']+)"
)

whatsapp_pattern = re.compile(
    r"(https?://[a-zA-Z0-9\-\.]*whatsapp\.com/[^\s\"']+|" r"https?://wa\.me/\d+)"
)


# Pages to scrape
PAGES = [
    "/",
    "/contact",
    "/contact-us",
    "/get-in-touch",
    "/reach-us",
    "/connect",
    "/contact-form",
    "/contact.html",
    "/contact-us.html",
    "/get-in-touch.html",
    "/reach-us.html",
    "/connect.html",
    "/contact-form.html",
    "/about",
    "/about-us",
    "/who-we-are",
    "/our-story",
    "/company",
    "/organization",
    "/about.html",
    "/about-us.html",
    "/who-we-are.html",
    "/our-story.html",
    "/company.html",
    "/organization.html",
    "/team",
    "/our-team",
    "/staff",
    "/doctors",
    "/management",
    "/leadership",
    "/team.html",
    "/our-team.html",
    "/staff.html",
    "/doctors.html",
    "/management.html",
    "/leadership.html",
    "/locations",
    "/branches",
    "/offices",
    "/clinics",
    "/find-us",
    "/where-we-are",
    "/locations.html",
    "/branches.html",
    "/offices.html",
    "/clinics.html",
    "/find-us.html",
    "/where-we-are.html",
    "/support",
    "/help",
    "/faq",
    "/customer-care",
    "/assistance",
    "/contact-support",
    "/enquiry",
    "/support.html",
    "/help.html",
    "/faq.html",
    "/customer-care.html",
    "/assistance.html",
    "/contact-support.html",
    "/enquiry.html",
    "/privacy",
    "/privacy-policy",
    "/terms",
    "/terms-of-service",
    "/legal",
    "/disclaimer",
    "/privacy.html",
    "/privacy-policy.html",
    "/terms.html",
    "/terms-of-service.html",
    "/legal.html",
    "/disclaimer.html",
]

LOG_FILE = "log.txt"


def normalize_url(url):
    if not isinstance(url, str) or not url.strip():
        return None
    url = url.strip().lower()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    if url.endswith("/"):
        url = url[:-1]
    return url


async def fetch(session, url):
    retries = SCRAPER_SETTINGS["aiohttp_retries"]
    backoff = SCRAPER_SETTINGS["aiohttp_backoff"]
    timeout = SCRAPER_SETTINGS["aiohttp_timeout"]
    """Fetch page content with retries and backoff for slow servers."""
    for attempt in range(retries):
        try:
            async with session.get(url, ssl=False, timeout=timeout) as resp:
                if resp.status == 200:
                    return await resp.text()
        except (aiohttp.ClientError, asyncio.TimeoutError):
            if attempt < retries - 1:
                await asyncio.sleep(backoff**attempt)
    return None


def extract_emails(soup, text):
    """Extract emails from text and mailto: links."""
    emails = set(email_pattern.findall(text))
    for a in soup.find_all("a", href=True):
        if a["href"].lower().startswith("mailto:"):
            emails.add(a["href"][7:])
    return emails


def extract_links(base_url, content):
    """Extract internal links from a page to crawl deeper."""
    links = set()
    try:
        soup = BeautifulSoup(content, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/") and not href.startswith("//"):
                links.add(base_url + href.lstrip("/"))
            elif href.startswith(base_url):
                links.add(href)
    except Exception:
        pass
    return list(links)


async def scrape_site_async(base_url, session):
    results = {
        k: set()
        for k in ["email", "facebook", "instagram", "linkedin", "twitter", "whatsapp"]
    }
    base_url = normalize_url(base_url)
    if not base_url:
        return {k: None for k in results}

    # Start with fixed pages
    tasks = [fetch(session, base_url + page) for page in PAGES]
    pages_content = await asyncio.gather(*tasks)

    # Crawl internal links from homepage
    if pages_content and pages_content[0]:
        extra_links = extract_links(base_url, pages_content[0])
        extra_tasks = [
            fetch(session, link)
            for link in extra_links[: SCRAPER_SETTINGS["limit_depth"]]
        ]  # limit depth
        pages_content += await asyncio.gather(*extra_tasks)

    for content in pages_content:
        if not content:
            continue
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text(" ", strip=True)
        results["email"].update(extract_emails(soup, text))
        results["facebook"].update(facebook_pattern.findall(content))
        results["instagram"].update(instagram_pattern.findall(content))
        results["linkedin"].update(linkedin_pattern.findall(content))
        results["twitter"].update(twitter_pattern.findall(content))
        results["whatsapp"].update(whatsapp_pattern.findall(content))

    return {k: ", ".join(sorted(v)) if v else None for k, v in results.items()}


async def scrape_with_playwright(url):
    results = {
        k: set()
        for k in ["email", "facebook", "instagram", "linkedin", "twitter", "whatsapp"]
    }
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(ignore_https_errors=True)
            await page.goto(
                url, timeout=SCRAPER_SETTINGS["playwright_timeout"]
            )  # longer timeout for slow servers
            content = await page.content()
            await browser.close()

            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text(" ", strip=True)
            results["email"].update(extract_emails(soup, text))
            results["facebook"].update(facebook_pattern.findall(content))
            results["instagram"].update(instagram_pattern.findall(content))
            results["linkedin"].update(linkedin_pattern.findall(content))
            results["twitter"].update(twitter_pattern.findall(content))
            results["whatsapp"].update(whatsapp_pattern.findall(content))
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"Playwright error scraping {url}: {e}\n")

    return {k: ", ".join(sorted(v)) if v else None for k, v in results.items()}


async def scrape_with_fallback(base_url, session):
    results = await scrape_site_async(base_url, session)
    # If aiohttp found little, retry with Playwright
    if not any(results.values()):
        playwright_results = await scrape_with_playwright(base_url)
        for key in results:
            if not results[key] and playwright_results.get(key):
                results[key] = playwright_results[key]
    return results


async def scrape_all(df):
    async with aiohttp.ClientSession() as session:
        cache = {}
        results = [None] * len(df)
        tasks = []
        indices = []

        for idx, row in df.iterrows():
            url = row.get("website")
            if not url or not isinstance(url, str) or not url.strip():
                results[idx] = {
                    k: None
                    for k in [
                        "email",
                        "facebook",
                        "instagram",
                        "linkedin",
                        "twitter",
                        "whatsapp",
                    ]
                }
                continue

            norm_url = normalize_url(url)
            if norm_url in cache:
                results[idx] = cache[norm_url]
            else:
                tasks.append(scrape_with_fallback(norm_url, session))
                indices.append((idx, norm_url))

        # Progress bar with enriched count
        done_results = []
        enriched_so_far = 0
        progress = tqdm(total=len(tasks), desc="Websites processed", unit="site")

        for fut in asyncio.as_completed(tasks):
            res = await fut
            done_results.append(res)
            progress.update(1)
            if any(res.values()):
                enriched_so_far += 1
                progress.set_description(f"Enriched {enriched_so_far}/{len(tasks)}")

        progress.close()

        for (idx, norm_url), res in zip(indices, done_results):
            cache[norm_url] = res
            results[idx] = res

        return {idx: results[idx] for idx in range(len(df))}, enriched_so_far


def run_combined(df):
    open(LOG_FILE, "w").close()
    results, enriched_count = asyncio.run(scrape_all(df))  # unpack both
    scraped_df = pd.DataFrame.from_dict(results, orient="index")
    scraped_df = scraped_df.reindex(df.index)
    return scraped_df, enriched_count
