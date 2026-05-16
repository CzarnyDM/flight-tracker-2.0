import json

from FlightRadarAPI import FlightRadar24API
from src.models import GetFlightInfo, FindClosestFlight
from src.settings import LIMIT_FLIGHTS, LAT, LON, MAX_FL, RAD

fr_api = FlightRadar24API()

def GetLocalFlights(lat, lon, rad, max_fl, limit):
    bounds = fr_api.get_bounds_by_point(lat, lon, rad)
    flights = fr_api.get_flights(bounds=bounds)
    current_found_flights = []

    for flight in flights [:limit]: # Limit to first X flights for demonstration
        if int(flight.altitude) < int(MAX_FL) and int(flight.altitude) > 0 and flight.callsign is not "GRND":  # Filter out ground flights and those above max flight level
            current_found_flights.append(flight)
            print(f"Found flight: {flight.id} at altitude {flight.altitude} ft")

    if len(current_found_flights) == 0:
        return False
    
    return current_found_flights

def GetFlightDetails(flight):
    details = fr_api.get_flight_details(flight)
    with open("db/details.json", "w") as f:
        json.dump(details, f, default=str, indent=4)
    return GetFlightInfo(flight, details)

def FindAirlineLogo(airline_iata, airline_icao):
    try:
        logo = fr_api.get_airline_logo(airline_iata, airline_icao)
        filename = f'.//utils/static/images/airline_logo.jpg'
        if logo is None:
            return None, False
        
        with open(filename, 'wb') as f:
            image = f.write(logo[0])
        return filename, True
    except Exception as e:
        return None, False

