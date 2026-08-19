import os
import re
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        # Fréquence de vérification : 30 secondes
        self.CHECK_INTERVAL_SECONDS: int = int(os.getenv("CHECK_INTERVAL_SECONDS", "30"))
        self.POSTAL_CODE: str = os.getenv("POSTAL_CODE", "75000").strip()
        self.PREFERRED_CITY: str = os.getenv("PREFERRED_CITY", "Île-de-France").strip()
        
        # Filtre strict région Île-de-France (IDF)
        self.IDF_POSTAL_PREFIXES: List[str] = ["75", "77", "78", "91", "92", "93", "94", "95"]
        self.IDF_KEYWORDS: List[str] = [
            "paris", "la défense", "gennevilliers", "créteil", "velizy", 
            "vélizy", "evry", "évry", "rosny", "aubervilliers", "boulogne", "versailles", 
            "cergy", "corbeil", "massy", "sartrouville", "saint-denis", "idf", "ile-de-france", "île-de-france"
        ]
        
        self.DISCORD_WEBHOOK_URL: Optional[str] = os.getenv("DISCORD_WEBHOOK_URL", "").strip() or None
        
        # Gestion intelligente du tag / ID utilisateur Discord
        raw_mention = os.getenv("DISCORD_MENTION", "").strip() or os.getenv("DISCORD_USER_ID", "").strip()
        if raw_mention:
            if raw_mention.startswith("<@") and raw_mention.endswith(">"):
                self.DISCORD_MENTION = raw_mention
            elif raw_mention.isdigit():
                self.DISCORD_MENTION = f"<@{raw_mention}>"
            else:
                self.DISCORD_MENTION = raw_mention
        else:
            self.DISCORD_MENTION = ""

        self.NTFY_TOPIC: Optional[str] = os.getenv("NTFY_TOPIC", "").strip() or None
        self.TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN", "").strip() or None
        self.TELEGRAM_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_CHAT_ID", "").strip() or None
        
        self.PORT: int = int(os.getenv("PORT", "8000"))
        self.HOST: str = os.getenv("HOST", "0.0.0.0")

    def is_idf_location(self, text: str) -> bool:
        if not text:
            return False
        text_lower = text.lower()
        for prefix in self.IDF_POSTAL_PREFIXES:
            if f"({prefix}" in text_lower or f" {prefix}" in text_lower or text_lower.startswith(prefix):
                return True
        for kw in self.IDF_KEYWORDS:
            if kw in text_lower:
                return True
        return False

settings = Settings()
