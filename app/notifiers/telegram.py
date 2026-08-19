import httpx
from app.notifiers.base import BaseNotifier
from app.config import settings

class TelegramNotifier(BaseNotifier):
    def __init__(self):
        super().__init__("Telegram")
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

    def is_configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    async def send_notification(self, store_name: str, url: str, price: str = None, details: str = None) -> bool:
        if not self.is_configured():
            return False

        price_str = f"\n💰 **Prix :** {price}" if price else ""
        details_str = f"\nℹ️ **Détails :** {details}" if details else ""

        message = (
            f"🚨 **ALERTE DISPONIBILITÉ MIDEA PORTASPLIT** 🚨\n\n"
            f"🛒 **Boutique :** {store_name}\n"
            f"✅ **Statut :** DISPONIBLE !"
            f"{price_str}"
            f"{details_str}\n\n"
            f"🔗 [Acheter / Voir sur le site]({url})"
        )

        api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(api_url, json=payload, timeout=10.0)
                return res.status_code == 200
        except Exception as e:
            print(f"[Telegram Notifier Error] {e}")
            return False

    async def send_test_notification(self) -> bool:
        if not self.is_configured():
            return False
        return await self.send_notification(
            store_name="Optimea (Test)",
            url="https://www.optimea.fr/product/climatiseur-split-mobile-midea/",
            price="999,00 €",
            details="Ceci est un message de test du système de notification Telegram."
        )
