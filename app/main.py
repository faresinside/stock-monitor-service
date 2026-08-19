import os
import asyncio
from datetime import datetime
from typing import List, Dict
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.models import ScrapeResult, StockStatus, LogEntry
from app.scrapers.manager import ScraperManager
from app.notifiers.manager import NotificationManager

app = FastAPI(title="Midea PortaSplit Monitor", version="1.2.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

scraper_manager = ScraperManager()
notifier_manager = NotificationManager()
scheduler = AsyncIOScheduler()

store_results: Dict[str, ScrapeResult] = {}
previous_statuses: Dict[str, StockStatus] = {}
activity_logs: List[LogEntry] = []

def add_log(store_name: str, status: StockStatus, message: str, is_alert: bool = False):
    entry = LogEntry(
        timestamp=datetime.now(),
        store_name=store_name,
        status=status,
        message=message,
        is_alert=is_alert
    )
    activity_logs.insert(0, entry)
    if len(activity_logs) > 100:
        activity_logs.pop()

async def run_check_cycle():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Vérification rapide des stocks (Toutes les {settings.CHECK_INTERVAL_SECONDS}s)...")
    results = await scraper_manager.check_all()
    
    for res in results:
        store_name = res.store_name
        prev_status = previous_statuses.get(store_name, StockStatus.UNKNOWN)
        current_status = res.status
        
        store_results[store_name] = res

        if current_status == StockStatus.IN_STOCK:
            add_log(store_name, current_status, res.details or "EN STOCK !", is_alert=True)
        elif current_status == StockStatus.OUT_OF_STOCK:
            add_log(store_name, current_status, f"Rupture de stock ({res.details or ''})")
        else:
            add_log(store_name, current_status, f"Statut: {res.details or res.error_message or 'Indéterminé'}")

        if current_status == StockStatus.IN_STOCK and prev_status != StockStatus.IN_STOCK:
            print(f"🚨 ALERTE DISPONIBILITÉ : {store_name} ({res.details})")
            add_log(store_name, current_status, f"🚨 ALERTE ENVOYÉE ! {res.details}", is_alert=True)
            await notifier_manager.notify_all(
                store_name=store_name,
                url=res.url,
                price=res.price,
                details=res.details,
                availability_type=res.availability_type,
                store_location=res.store_location
            )

        previous_statuses[store_name] = current_status

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_check_cycle())
    # Ordonnancement toutes les 30 secondes
    scheduler.add_job(
        run_check_cycle,
        'interval',
        seconds=settings.CHECK_INTERVAL_SECONDS,
        id="stock_check_job"
    )
    scheduler.start()
    print(f"✅ Monitor initialisé. Fréquence : {settings.CHECK_INTERVAL_SECONDS}s. Secteur : {settings.PREFERRED_CITY} ({settings.POSTAL_CODE}).")

@app.get("/")
async def render_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "check_interval_seconds": settings.CHECK_INTERVAL_SECONDS,
            "postal_code": settings.POSTAL_CODE,
            "preferred_city": settings.PREFERRED_CITY,
            "has_discord": bool(settings.DISCORD_WEBHOOK_URL)
        }
    )

@app.get("/api/status")
async def get_status():
    return {
        "last_updated": datetime.now().isoformat(),
        "stores": [res.model_dump() for res in store_results.values()],
        "logs": [log.model_dump() for log in activity_logs[:30]]
    }

@app.post("/api/check")
async def trigger_manual_check():
    asyncio.create_task(run_check_cycle())
    return {"message": "Vérification manuelle lancée"}

@app.post("/api/test-notification")
async def trigger_test_notification():
    results = await notifier_manager.send_test_all()
    add_log("Système", StockStatus.IN_STOCK, f"Test de notification envoyé : {results}", is_alert=True)
    return {"status": "ok", "results": results}
