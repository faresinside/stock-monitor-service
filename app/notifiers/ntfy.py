import httpx
from app.notifiers.base import BaseNotifier
from app.config import settings

class NtfyNotifier(BaseNotifier):
    def __init__(self):
        super().__init__("Ntfy.sh")
        self.topic = settings.NTFY_TOPIC

    def is_configured(self) -> bool:
        return bool(self.topic)

    async def send_notification(self, store_name: str, url: str, price: str = None, details: str = None) -> bool:
        if not self.is_configured():
            return False

        price_str = f" - Prix: {price}" if price else ""
        message = f"Le Midea PortaSplit est DISPONIBLE sur {store_name} !{price_str}\nCliquez pour commander."

        api_url = f"https://ntfy.sh/{self.topic}"
        headers = {
            "Title": f"Midea PortaSplit disponible sur {store_name} !",
            "Priority": "high",
            "Tags": "snowflake,air_conditioning,rotating_light",
            "Click": url
        }

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(api_url, content=message, headers=headers, timeout=10.0)
                return res.status_code == 200
        except Exception as e:
            print(f"[Ntfy Notifier Error] {e}")
            return False

    async def send_test_notification(self) -> bool:
        if not self.is_configured():
            return False
        return await self.send_notification(
            store_name="Optimea (Test Ntfy)",
            url="https://www.optimea.fr/product/climatiseur-split-mobile-midea/",
            price="999,00 €",
            details="Test d'envoi de notification Ntfy.sh"
        )
