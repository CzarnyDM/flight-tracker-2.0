from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from geopy.geocoders import Nominatim

import uvicorn
import json
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="utils/static"), name="static")
templates = Jinja2Templates(directory="templates")

STATE_FILE = "db/state.json"
SETTINGS = "db/settings.json"

def get_locaiton_name(lat, lon):
    geolocator = Nominatim(user_agent="flight_tracker")
    location = geolocator.reverse((lat, lon), exactly_one=True, addressdetails=True)
    address = location.raw.get("address", {}) if location else {}
    road = address.get('road', '')
    city = address.get('city') or address.get('town') or address.get('village') or ''
    return f"{road}, {city}".strip(', ')

def read_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def read_settings():
    with open("db/settings.json") as f:
        return json.load(f)
    

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {
        "settings": read_settings(),
        "flight": read_state(),
        "location" : get_locaiton_name(read_settings().get("lat", 0), read_settings().get("lon", 0))
    })

@app.get("/debug-state")
async def debug_state():
    return JSONResponse(read_state())

@app.post("/settings")
async def update_settings(
    lat: float = Form(...),
    lon: float = Form(...),
    radius: int = Form(...),
    max_fl: int = Form(...),
    limit: int = Form(...),
    discord_webhook: str = Form("")
):
    data = {"lat": lat, "lon": lon, "radius": radius, "max_fl": max_fl, "limit": limit, "discord_webhook": discord_webhook}
    with open(SETTINGS, "w") as f:
        json.dump(data, f, indent=4)
    return RedirectResponse(url="/settings-page", status_code=303)

@app.get("/settings-page", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse(request, "settings.html", {
        "settings": read_settings()
    })
    
@app.get("/api/latest")
async def latest_flight():
    return JSONResponse(read_state())

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)