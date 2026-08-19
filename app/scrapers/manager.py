import asyncio
import httpx
from typing import List
from app.scrapers.base import BaseScraper
from app.scrapers.optimea import OptimeaScraper
from app.scrapers.boulanger import BoulangerScraper
from app.scrapers.castorama import CastoramaScraper
from app.scrapers.amazon import AmazonScraper
from app.scrapers.leroymerlin import LeroyMerlinScraper
from app.scrapers.darty import DartyScraper
from app.models import ScrapeResult

class ScraperManager:
    def __init__(self):
        self.scrapers: List[BaseScraper] = [
            OptimeaScraper(),      # Site officiel prioritaire
            BoulangerScraper(),
            CastoramaScraper(),
            AmazonScraper(),
            DartyScraper(),
            LeroyMerlinScraper()
        ]

    async def check_all(self) -> List[ScrapeResult]:
        async with httpx.AsyncClient(timeout=15.0) as client:
            tasks = [scraper.check(client) for scraper in self.scrapers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            clean_results = []
            for idx, res in enumerate(results):
                if isinstance(res, Exception):
                    clean_results.append(ScrapeResult(
                        store_name=self.scrapers[idx].name,
                        url=self.scrapers[idx].url,
                        status="ERROR",
                        error_message=str(res),
                        details="Erreur d'exécution du scraper"
                    ))
                else:
                    clean_results.append(res)
            return clean_results
