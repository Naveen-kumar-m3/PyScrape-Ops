# pyscrape_ops/scraper.py
from typing import List, Dict, Optional
import time
import requests
from bs4 import BeautifulSoup
from urllib import robotparser
from urllib.parse import urljoin, urlparse

DEFAULT_HEADERS = {
    "User-Agent": "PyScrape-Ops/0.1 (+https://github.com/yourname/pyscrape-ops)"
}

class Scraper:
    def __init__(self, headers: Optional[Dict[str,str]] = None, timeout: int = 10):
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
        if parsed.scheme == "file":
            path = parsed.path
            if path.startswith("/") and len(path) > 2 and path[2] == ":":
                path = path.lstrip("/")
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text

    def parse_list(self, html: str, selectors: Dict[str,str]) -> List[Dict[str,str]]:
        soup = BeautifulSoup(html, "html.parser")
        items = []
        item_sel = selectors.get("item", "")
        if not item_sel:
            return items
        for el in soup.select(item_sel):
            record = {}
            for key, sel in selectors.items():
                if key == "item":
                    continue
                sub = el.select_one(sel)
                record[key] = sub.get_text(strip=True) if sub else ""
            items.append(record)
        return items

    def scrape_job(self, url: str, selectors: Dict[str,str], rate_limit_seconds: float = 1.0):
        base = "{0.scheme}://{0.netloc}".format(urlparse(url))
        if urlparse(url).scheme in ("http","https"):
            if not self.can_fetch(base, urlparse(url).path):
                raise PermissionError(f"Robots.txt disallows scraping {url}")
        html = self.fetch(url)
        items = self.parse_list(html, selectors)
        if urlparse(url).scheme in ("http","https"):
            time.sleep(rate_limit_seconds)
        return items
