import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from app.config import settings
from app.scrapers.base import BaseScraper, extract_price_float
from app.models import ScrapeResult, StockStatus, AvailabilityType

class BoulangerScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            name="Boulanger",
            url="https://www.boulanger.com/resultats?tr=midea+portasplit"
        )

    async def check(self, client: httpx.AsyncClient) -> ScrapeResult:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "fr-FR,fr;q=0.9",
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
            
            card = soup.find(lambda e: e.name in ['div', 'article', 'a'] and e.get('data-analytics_product_name') == 'climatiseur_reversible_midea_portasplit_mobile')
            
            if not card:
                for el in soup.find_all(['div', 'article'], class_=lambda c: c and 'product' in c):
                    if 'portasplit' in el.text.lower():
                        card = el
                        break

            if not card:
                return ScrapeResult(
                    store_name=self.name,
                    url=self.url,
                    status=StockStatus.OUT_OF_STOCK,
                    details="Produit non trouvé sur la page de recherche",
                    last_check=datetime.now()
                )

            avail_attr = card.get('data-analytics_product_availability')
            seller_attr = card.get('data-analytics_product_seller', 'boulanger')
            price_attr = card.get('data-analytics_product_unitprice_ati')

            price_str = f"{price_attr} €" if price_attr else "999,00 €"
            price_val = extract_price_float(price_str)

            if seller_attr and seller_attr.lower() != 'boulanger':
                return ScrapeResult(
                    store_name=self.name,
                    url=self.url,
                    status=StockStatus.OUT_OF_STOCK,
                    price=price_str,
                    details="Uniquement vendeur tiers marketplace (Ignoré)",
                    last_check=datetime.now()
                )

            if avail_attr == 'false' or 'indisponible' in card.text.lower() or 'épuisé' in card.text.lower():
                return ScrapeResult(
                    store_name=self.name,
                    url=self.url,
                    status=StockStatus.OUT_OF_STOCK,
                    price=price_str,
                    details="Rupture de stock (En ligne & Magasins)",
                    last_check=datetime.now()
                )

            if avail_attr == 'true' and (not price_val or price_val <= self.max_price):
                card_text = card.text.lower()
                if 'retrait' in card_text:
                    return ScrapeResult(
                        store_name=self.name,
                        url=self.url,
                        status=StockStatus.IN_STOCK,
                        availability_type=AvailabilityType.IN_STORE_PICKUP,
                        store_location="Boulanger (Magasin Île-de-France)",
                        price=price_str,
                        details="🏬 DISPONIBLE RETRAIT MAGASIN : Boulanger (Île-de-France) !",
                        last_check=datetime.now()
                    )
                else:
                    return ScrapeResult(
                        store_name=self.name,
                        url=self.url,
                        status=StockStatus.IN_STOCK,
                        availability_type=AvailabilityType.ONLINE_DELIVERY,
                        price=price_str,
                        details=f"🌐 DISPONIBLE EN VENTE EN LIGNE (Livraison) ! ({price_str})",
                        last_check=datetime.now()
                    )

            return ScrapeResult(
                store_name=self.name,
                url=self.url,
                status=StockStatus.OUT_OF_STOCK,
                price=price_str,
                details="Indisponible",
                last_check=datetime.now()
            )
        except Exception as e:
            return ScrapeResult(
                store_name=self.name,
                url=self.url,
                status=StockStatus.ERROR,
                error_message=str(e),
                details="Erreur de connexion Boulanger",
                last_check=datetime.now()
            )
