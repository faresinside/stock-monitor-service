import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from app.config import settings
from app.scrapers.base import BaseScraper, extract_price_float
from app.models import ScrapeResult, StockStatus, AvailabilityType

class CastoramaScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            name="Castorama",
            url="https://www.castorama.fr/climatiseur-portasplit-midea-reversible-3500w/8431312260509_CAFR.prd"
        )

    async def check(self, client: httpx.AsyncClient) -> ScrapeResult:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "fr-FR,fr;q=0.9",
                "Referer": "https://www.castorama.fr/"
            }
            res = await client.get(self.url, headers=headers, follow_redirects=True, timeout=12.0)
            
            if res.status_code != 200:
                return ScrapeResult(
                    store_name=self.name,
                    url=self.url,
                    status=StockStatus.ERROR,
                    details=f"Code HTTP {res.status_code}",
                    error_message=f"HTTP {res.status_code}",
                    last_check=datetime.now()
                )

            html = res.text
            soup = BeautifulSoup(html, "html.parser")
            text_lower = html.lower()

            price_match = re.search(r"(\d{3,4}(?:[\,\.]\d{2})?)\s*€", text_lower)
            price_str = price_match.group(0) if price_match else "999 €"
            price_val = extract_price_float(price_str)

            # Recherche du bouton Ajouter au panier officiel (product-cta-button)
            cta_button = soup.find('button', attrs={'data-testid': 'product-cta-button'})
            if not cta_button:
                cta_button = soup.find(lambda e: e.name == 'button' and 'ajouter au panier' in e.text.lower())

            # Le bouton est-il désactivé ?
            is_disabled = False
            if cta_button:
                is_disabled = 'disabled' in cta_button.attrs or cta_button.get('aria-disabled') == 'true'
            else:
                is_disabled = True

            is_grand_succes = "grand succès" in text_lower or "vérifiez sa disponibilité" in text_lower
            is_valid_price = (not price_val or price_val <= self.max_price)

            # Si le bouton panier existe, n'est pas désactivé et le prix <= 1000€
            if cta_button and not is_disabled and not is_grand_succes and is_valid_price:
                return ScrapeResult(
                    store_name=self.name,
                    url=self.url,
                    status=StockStatus.IN_STOCK,
                    availability_type=AvailabilityType.ONLINE_DELIVERY,
                    price=price_str,
                    details=f"🌐 DISPONIBLE EN VENTE EN LIGNE chez Castorama ! ({price_str})",
                    last_check=datetime.now()
                )

            # Sinon, vérification retrait magasin IDF
            if "disponible au magasin" in text_lower and settings.is_idf_location(text_lower) and is_valid_price:
                return ScrapeResult(
                    store_name=self.name,
                    url=self.url,
                    status=StockStatus.IN_STOCK,
                    availability_type=AvailabilityType.IN_STORE_PICKUP,
                    store_location="Castorama (Magasin Île-de-France)",
                    price=price_str,
                    details="🏬 DISPONIBLE RETRAIT MAGASIN : Castorama (Île-de-France) !",
                    last_check=datetime.now()
                )

            return ScrapeResult(
                store_name=self.name,
                url=self.url,
                status=StockStatus.OUT_OF_STOCK,
                price=price_str,
                details="Rupture de stock chez Castorama (Bouton d'achat désactivé)",
                last_check=datetime.now()
            )
        except Exception as e:
            return ScrapeResult(
                store_name=self.name,
                url=self.url,
                status=StockStatus.ERROR,
                error_message=str(e),
                details="Erreur de connexion Castorama",
                last_check=datetime.now()
            )
