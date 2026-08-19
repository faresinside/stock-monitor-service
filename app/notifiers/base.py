from abc import ABC, abstractmethod

class BaseNotifier(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def send_notification(self, store_name: str, url: str, price: str = None, details: str = None) -> bool:
        pass

    @abstractmethod
    async def send_test_notification(self) -> bool:
        pass
