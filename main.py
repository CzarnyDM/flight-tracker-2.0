import logging
import threading
import time
import json
import uvicorn
from geopy.geocoders import Nominatim
from app import app as fastapi_app
from src.models import FindClosestFlight, NotificationTemplate
from src.notification import SendDiscordWebhook
from src.settings import LIMIT_FLIGHTS, LAT, LON, RAD
from src.radar import FindAirlineLogo, GetLocalFlights, GetFlightDetails

seen_flights = set()

def start_api():
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)

def read_settings():
    with open("db/settings.json") as f:
        return json.load(f)
    

def main():
    while True:
        s = read_settings()
        local_flight = GetLocalFlights(s["lat"], s["lon"], s["radius"], s["max_fl"], s["limit"])

        if local_flight is not False:
            closest_flight = FindClosestFlight(local_flight, s["lat"], s["lon"])
            flight_id = list(closest_flight.keys())[0]
            
            if flight_id not in seen_flights:
                seen_flights.add(flight_id)
                print(f"New flight detected: {closest_flight[flight_id]['flight'].callsign} at altitude {closest_flight[flight_id]['flight'].altitude} ft")
                flight_details = GetFlightDetails(closest_flight[flight_id]["flight"])
                logo = FindAirlineLogo(flight_details["airline_iata"], flight_details["airline_icao"])
                with open("db/state.json", "w") as f:
                    json.dump(flight_details, f, default=str, indent=4)
                SendDiscordWebhook(NotificationTemplate(flight_details), logo, flight_details["airline_name"])
            else:
                print("Flight already seen, updating info:")
            time.sleep(15)



t = threading.Thread(target=start_api, daemon=True)
t.start()

if __name__ == "__main__":
    main()