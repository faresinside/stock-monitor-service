import httpx
from app.notifiers.base import BaseNotifier
from app.config import settings

class DiscordNotifier(BaseNotifier):
    def __init__(self):
        super().__init__("Discord")
        self.webhook_url = settings.DISCORD_WEBHOOK_URL

    def is_configured(self) -> bool:
        return bool(self.webhook_url and self.webhook_url.startswith("http"))

    async def send_notification(self, store_name: str, url: str, price: str = None, details: str = None, availability_type: str = None, store_location: str = None) -> bool:
        if not self.is_configured():
            return False

        if availability_type == "ONLINE_DELIVERY":
            header_title = "🌐 DISPONIBLE EN VENTE EN LIGNE (Livraison)"
            status_text = "🌐 EN STOCK EN LIGNE (Livraison à domicile)"
            color_code = 3066993  # Green
        elif availability_type == "IN_STORE_PICKUP":
            header_title = f"🏬 DISPONIBLE EN MAGASIN : {store_location or store_name}"
            status_text = f"🏬 EN STOCK EN RETRAIT MAGASIN ({store_location or store_name})"
            color_code = 15844367 # Gold
        else:
            header_title = "🚨 Midea PortaSplit DISPONIBLE !"
            status_text = "🟢 EN STOCK !"
            color_code = 3066993

        fields = [
            {"name": "🛒 Enseigne", "value": store_name, "inline": True},
            {"name": "⚡ Type de stock", "value": status_text, "inline": False}
        ]

        if store_location:
            fields.append({"name": "📍 Magasin local", "value": store_location, "inline": True})

        if price:
            fields.append({"name": "💰 Prix", "value": price, "inline": True})
        
        if details:
            fields.append({"name": "ℹ️ Détails", "value": details, "inline": False})
        
        fields.append({"name": "🔗 Commander / Réserver", "value": f"[Accéder à la fiche {store_name}]({url})", "inline": False})

        embed = {
            "title": f"🚨 {header_title}",
            "description": f"Le climatiseur Midea PortaSplit a été détecté **disponible** !",
            "url": url,
            "color": color_code,
            "fields": fields,
            "footer": {"text": f"PortaSplit Monitor • Secteur : {settings.PREFERRED_CITY}"}
        }

        mention_str = f"{settings.DISCORD_MENTION} " if settings.DISCORD_MENTION else ""
        payload = {
            "content": f"🚨 {mention_str}**MIDEA PORTASPLIT DISPONIBLE !** {header_title}",
            "embeds": [embed]
        }

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(self.webhook_url, json=payload, timeout=10.0)
                return res.status_code in [200, 204]
        except Exception as e:
            print(f"[Discord Notifier Error] {e}")
            return False

    async def send_test_notification(self) -> bool:
        if not self.is_configured():
            return False
        mention_str = f" adressée à {settings.DISCORD_MENTION}" if settings.DISCORD_MENTION else ""
        return await self.send_notification(
            store_name="Optimea (Test Discord)",
            url="https://www.optimea.fr/product/climatiseur-split-mobile-midea/",
            price="999,00 €",
            details=f"Test réussi ! Notification de test{mention_str}.",
            availability_type="ONLINE_DELIVERY"
        )
