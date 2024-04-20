"""OdaTrade frontend API client."""
import requests

class OdaTradeClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base = base_url

    def status(self):
        return requests.get(f"{self.base}/status", timeout=5).json()

    def start(self):
        return requests.post(f"{self.base}/start", timeout=5).json()

    def stop(self):
        return requests.post(f"{self.base}/stop", timeout=5).json()

    def portfolio(self):
        return requests.get(f"{self.base}/api/v1/portfolio/summary", timeout=5).json()
