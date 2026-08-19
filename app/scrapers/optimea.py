import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from app.scrapers.base import BaseScraper, extract_price_float
from app.models import ScrapeResult, StockStatus

class OptimeaScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            name="Optimea (Officiel)",
            url="https://www.optimea.fr/product/climatiseur-split-mobile-midea/"
        )

    async def check(self, client: httpx.AsyncClient) -> ScrapeResult:
        try:
            html = await self.fetch_html(client)
            soup = BeautifulSoup(html, "html.parser")
            
            meta_avail = soup.find("meta", property="product:availability")
            stock_p = soup.find("p", class_="stock")
            
            price_elem = soup.find("p", class_="price")
            price_str = None
            if price_elem:
                bdi = price_elem.find("bdi")
                if bdi:
                    price_str = bdi.text.strip().replace("\xa0", " ")
                else:
                    price_str = price_elem.text.strip().replace("\xa0", " ")

            price_val = extract_price_float(price_str)

            status = StockStatus.OUT_OF_STOCK
            details = "Rupture de stock chez le distributeur officiel Optimea"

            # Check stock condition
            is_in_stock = False
            if meta_avail and meta_avail.get("content") in ["in stock", "instock"]:
                is_in_stock = True
            elif stock_p and "in-stock" in stock_p.get("class", []):
                is_in_stock = True
            elif "Ajouter au panier" in html and "Rupture de stock" not in html:
                is_in_stock = True

            if is_in_stock:
                if price_val and price_val > self.max_price:
                    status = StockStatus.OUT_OF_STOCK
                    details = f"En stock mais prix trop élevé ({price_val}€ > {self.max_price}€)"
                else:
                    status = StockStatus.IN_STOCK
                    details = f"En stock chez le distributeur officiel Optimea ! ({price_str or '999,00 €'})"

            return ScrapeResult(
                store_name=self.name,
                url=self.url,
                status=status,
                price=price_str or "999,00 €",
                details=details,
                last_check=datetime.now()
            )
        except Exception as e:
            return ScrapeResult(
                store_name=self.name,
                url=self.url,
                status=StockStatus.ERROR,
                error_message=str(e),
                details="Erreur d'accès au site Optimea",
                last_check=datetime.now()
            )
