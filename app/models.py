from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StockStatus(str, Enum):
    IN_STOCK = "IN_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"

class AvailabilityType(str, Enum):
    ONLINE_DELIVERY = "ONLINE_DELIVERY"  # Vente en ligne / livraison (Priorité 1)
    IN_STORE_PICKUP = "IN_STORE_PICKUP"  # Retrait magasin local (Priorité 2)
    NONE = "NONE"

class ScrapeResult(BaseModel):
    store_name: str
    url: str
    status: StockStatus
    availability_type: AvailabilityType = AvailabilityType.NONE
    store_location: Optional[str] = None  # Ex: "Leroy Merlin Nanterre"
    price: Optional[str] = None
    details: Optional[str] = None
    last_check: datetime = datetime.now()
    error_message: Optional[str] = None

class LogEntry(BaseModel):
    timestamp: datetime = datetime.now()
    store_name: str
    status: StockStatus
    message: str
    is_alert: bool = False
