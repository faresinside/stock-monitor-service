import re
import httpx
from abc import ABC, abstractmethod
from app.models import ScrapeResult, StockStatus

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

def extract_price_float(price_str: str) -> float | None:
    """ Extrait la valeur numérique d'un prix en euros (ex: '999,00 €' -> 999.0) """
    if not price_str:
        return None
    cleaned = price_str.replace(" ", "").replace("\xa0", "").replace(",", ".")
    match = re.search(r"(\d+(?:\.\d+)?)", cleaned)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None

class BaseScraper(ABC):
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.max_price = 1000.0  # Filtrage strict : max 1000 €

    async def fetch_html(self, client: httpx.AsyncClient) -> str:
        response = await client.get(
            self.url,
            headers=DEFAULT_HEADERS,
            follow_redirects=True,
            timeout=15.0
        )
        response.raise_for_status()
        return response.text

    @abstractmethod
    async def check(self, client: httpx.AsyncClient) -> ScrapeResult:
        pass
