# pyscrape_ops/scraper.py

from typing import List, Dict, Optional
import time
import requests
from bs4 import BeautifulSoup
from urllib import robotparser
from urllib.parse import urljoin, urlparse


DEFAULT_HEADERS = {
    "User-Agent": "PyScrape-Ops/0.1 (+https://github.com/Naveen-Kumar-m3/pyscrape-ops)"
}


class Scraper:
    def __init__(self, headers: Optional[Dict[str, str]] = None, timeout: int = 10):
        self.headers = headers or DEFAULT_HEADERS
        self.timeout = timeout

    def can_fetch(self, base_url: str, path: str = "/") -> bool:
        try:
            rp = robotparser.RobotFileParser()
            rp.set_url(urljoin(base_url, "/robots.txt"))
            rp.read()
            return rp.can_fetch(self.headers.get("User-Agent", "*"), path)
        except Exception:
            return True

    def fetch(self, url: str) -> str:
        parsed = urlparse(url)

        # Local file support
        if parsed.scheme == "file":
            path = parsed.path
            if path.startswith("/") and len(path) > 2 and path[2] == ":":
                path = path.lstrip("/")
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

        # HTTP / HTTPS request
        response = requests.get(
            url,
            headers=self.headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.text

    def parse_list(self, html: str, selectors: Dict[str, str]) -> List[Dict[str, str]]:
        soup = BeautifulSoup(html, "html.parser")
        items: List[Dict[str, str]] = []

        item_selector = selectors.get("item")
        if not item_selector:
            return items

        for element in soup.select(item_selector):
            record: Dict[str, str] = {}
            for key, selector in selectors.items():
                if key == "item":
                    continue
                found = element.select_one(selector)
                record[key] = found.get_text(strip=True) if found else ""
            items.append(record)

        return items

    def scrape_job(
        self,
        url: str,
        selectors: Dict[str, str],
        rate_limit_seconds: float = 1.0,
    ) -> List[Dict[str, str]]:

        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        if parsed.scheme in ("http", "https"):
            if not self.can_fetch(base, parsed.path):
                raise PermissionError(f"Robots.txt disallows scraping {url}")

        html = self.fetch(url)
        results = self.parse_list(html, selectors)

        if parsed.scheme in ("http", "https"):
            time.sleep(rate_limit_seconds)

        return results
