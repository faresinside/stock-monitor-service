import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from app.config import settings
from app.scrapers.base import BaseScraper, extract_price_float
from app.models import ScrapeResult, StockStatus, AvailabilityType

class LeroyMerlinScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            name="Leroy Merlin",
            url="https://www.leroymerlin.fr/produits/climatiseur-split-mobile-reversible-portasplit-midea-par-optimea-93857579.html"
        )

    async def check(self, client: httpx.AsyncClient) -> ScrapeResult:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "fr-FR,fr;q=0.9",
                "Referer": "https://www.leroymerlin.fr/"
            }
            res = await client.get(self.url, headers=headers, follow_redirects=True, timeout=12.0)
            
            if res.status_code == 403 or "datadome" in res.text.lower():
                return ScrapeResult(
                    store_name=self.name,
                    url=self.url,
                    status=StockStatus.ERROR,
                    details="Protégé par anti-bot (DataDome 403)",
                    error_message="HTTP 403 DataDome Protection",
                    last_check=datetime.now()
                )

            html = res.text
            text_lower = html.lower()

            price_match = re.search(r"(\d{3,4}(?:[\,\.]\d{2})?)\s*€", html)
            price_str = price_match.group(0) if price_match else None
            price_val = extract_price_float(price_str)

            status = StockStatus.OUT_OF_STOCK
            avail_type = AvailabilityType.NONE
            store_loc = None
            details = "Indisponible chez Leroy Merlin"

            is_valid_price = (not price_val or price_val <= self.max_price)
            has_online = ("livraison" in text_lower or "en ligne" in text_lower) and ("en stock" in text_lower or "ajouter au panier" in text_lower)
            has_store = "retrait" in text_lower or "magasin" in text_lower or "2h" in text_lower

            if has_online and is_valid_price:
                status = StockStatus.IN_STOCK
                avail_type = AvailabilityType.ONLINE_DELIVERY
                details = f"🌐 DISPONIBLE EN VENTE EN LIGNE chez Leroy Merlin ! ({price_str or '999,00 €'})"
            elif has_store and is_valid_price:
                if settings.is_idf_location(text_lower):
                    status = StockStatus.IN_STOCK
                    avail_type = AvailabilityType.IN_STORE_PICKUP
                    store_loc = "Leroy Merlin (Magasin Île-de-France)"
                    details = "🏬 DISPONIBLE RETRAIT MAGASIN : Leroy Merlin (Île-de-France) !"
                else:
                    details = "Stock magasin disponible hors Île-de-France (Ignoré)"

            return ScrapeResult(
                store_name=self.name,
                url=self.url,
                status=status,
                availability_type=avail_type,
                store_location=store_loc,
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
                details="Erreur de connexion Leroy Merlin",
                last_check=datetime.now()
            )
