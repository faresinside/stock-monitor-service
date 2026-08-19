import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from app.config import settings
from app.scrapers.base import BaseScraper, extract_price_float
from app.models import ScrapeResult, StockStatus, AvailabilityType

class AmazonScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            name="Amazon.fr",
            url="https://www.amazon.fr/s?k=Midea+PortaSplit"
        )

    async def check(self, client: httpx.AsyncClient) -> ScrapeResult:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "fr-FR,fr;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await client.get(self.url, headers=headers, follow_redirects=True, timeout=12.0)
            
            if res.status_code == 503 or "captcha" in res.text.lower():
                return ScrapeResult(
                    store_name=self.name,
                    url=self.url,
                    status=StockStatus.UNKNOWN,
                    details="Blocage Captcha Amazon",
                    error_message="Amazon Captcha",
                    last_check=datetime.now()
                )

            html = res.text
            soup = BeautifulSoup(html, "html.parser")
            text_lower = html.lower()

            price_match = re.search(r"(\d{3,4}(?:[\,\.]\d{2})?)\s*€", html)
            price_str = price_match.group(0) if price_match else None
            price_val = extract_price_float(price_str)

            # Règle clé : Le prix ne doit PAS dépasser 1000 € (ex: 999€ OK, 1200€ KO)
            if price_val and price_val > self.max_price:
                return ScrapeResult(
                    store_name=self.name,
                    url=self.url,
                    status=StockStatus.OUT_OF_STOCK,
                    price=price_str,
                    details=f"En stock mais prix vendeur > 1000€ ({price_val}€)",
                    last_check=datetime.now()
                )

            status = StockStatus.OUT_OF_STOCK
            avail_type = AvailabilityType.NONE
            details = "Non disponible sur Amazon (<= 1000€)"

            if ("en stock" in text_lower or "ajouter au panier" in text_lower) and (not price_val or price_val <= self.max_price):
                status = StockStatus.IN_STOCK
                avail_type = AvailabilityType.ONLINE_DELIVERY
                details = f"🌐 DISPONIBLE SUR AMAZON ! ({price_str or '<= 1000€'})"

            return ScrapeResult(
                store_name=self.name,
                url=self.url,
                status=status,
                availability_type=avail_type,
                price=price_str,
                details=details,
                last_check=datetime.now()
            )
        except Exception as e:
            return ScrapeResult(
                store_name=self.name,
                url=self.url,
                status=StockStatus.ERROR,
                error_message=str(e),
                details="Erreur de connexion Amazon",
                last_check=datetime.now()
            )
