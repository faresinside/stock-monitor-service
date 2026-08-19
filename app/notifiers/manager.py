import asyncio
from typing import List, Dict
from app.notifiers.telegram import TelegramNotifier
from app.notifiers.ntfy import NtfyNotifier
from app.notifiers.discord import DiscordNotifier

class NotificationManager:
    def __init__(self):
        self.notifiers = [
            DiscordNotifier(),
            TelegramNotifier(),
            NtfyNotifier()
        ]

    async def notify_all(self, store_name: str, url: str, price: str = None, details: str = None, availability_type: str = None, store_location: str = None) -> Dict[str, bool]:
        results = {}
        for notifier in self.notifiers:
            if notifier.is_configured():
                if isinstance(notifier, DiscordNotifier):
                    success = await notifier.send_notification(store_name, url, price, details, availability_type, store_location)
                else:
                    success = await notifier.send_notification(store_name, url, price, details)
                results[notifier.name] = success
        return results

    async def send_test_all(self) -> Dict[str, bool]:
        results = {}
        for notifier in self.notifiers:
            if notifier.is_configured():
                success = await notifier.send_test_notification()
                results[notifier.name] = success
            else:
                results[notifier.name] = False
        return results
