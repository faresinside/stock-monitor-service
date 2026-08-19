import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from app.config import settings
from app.scrapers.base import BaseScraper, extract_price_float
from app.models import ScrapeResult, StockStatus, AvailabilityType

class DartyScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            name="Darty",
            url="https://www.darty.com/nav/recherche?text=midea+portasplit"
        )

    async def check(self, client: httpx.AsyncClient) -> ScrapeResult:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "fr-FR,fr;q=0.9",
                "Referer": "https://www.darty.com/"
            }
            res = await client.get(self.url, headers=headers, follow_redirects=True, timeout=12.0)
            
            if res.status_code == 403:
                return ScrapeResult(
                    store_name=self.name,
                    url=self.url,
                    status=StockStatus.ERROR,
                    details="Protégé par anti-bot (Akamai 403)",
                    error_message="HTTP 403 Forbidden",
                    last_check=datetime.now()
                )

            html = res.text
            text_lower = html.lower()

            price_match = re.search(r"(\d{3,4}(?:[\,\.]\d{2})?)\s*€", html)
            price_str = price_match.group(0) if price_match else None
            price_val = extract_price_float(price_str)

            # Règle clé : Le prix ne doit PAS dépasser 1000 €
            if price_val and price_val > self.max_price:
                return ScrapeResult(
                    store_name=self.name,
                    url=self.url,
                    status=StockStatus.OUT_OF_STOCK,
                    price=price_str,
                    details=f"En stock mais prix trop élevé ({price_val}€ > 1000€)",
                    last_check=datetime.now()
                )

            status = StockStatus.OUT_OF_STOCK
            avail_type = AvailabilityType.NONE
            store_loc = None
            details = "Rupture de stock chez Darty"

            has_add_cart = "ajouter au panier" in text_lower or "ajouter le produit au panier" in text_lower
            has_store = "retrait" in text_lower or "magasin" in text_lower

            if has_add_cart and "indisponible" not in text_lower:
                status = StockStatus.IN_STOCK
                avail_type = AvailabilityType.ONLINE_DELIVERY
                details = f"🌐 DISPONIBLE EN VENTE EN LIGNE chez Darty ! ({price_str or '<= 1000€'})"
            elif has_store and settings.is_idf_location(text_lower):
                status = StockStatus.IN_STOCK
                avail_type = AvailabilityType.IN_STORE_PICKUP
                store_loc = "Darty (Magasin Île-de-France)"
                details = "🏬 DISPONIBLE RETRAIT MAGASIN : Darty (Île-de-France) !"

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
                details="Erreur de connexion Darty",
                last_check=datetime.now()
            )
