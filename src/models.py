import re
import json

def GetFlightInfo(flight, api):
    return {
        # flight object data
        "flight_id":            flight.id,
        "callsign":             flight.callsign,
        "flight_number":        flight.number,
        "aircraft_code":        flight.aircraft_code,
        "airline_iata":         flight.airline_iata,
        "airline_icao":         flight.airline_icao,
        "altitude":             flight.altitude,
        "flight_level":         flight.get_flight_level(),
        "ground_speed":         flight.ground_speed,
        "vertical_speed":       flight.vertical_speed,
        "heading":              flight.heading,
        "latitude":             flight.latitude,
        "longitude":            flight.longitude,
        "on_ground":            flight.on_ground,
        "origin":               flight.origin_airport_iata,
        "destination":          flight.destination_airport_iata,
        "registration":         flight.registration,
        "icao_24bit":           flight.icao_24bit,
        "squawk":               flight.squawk,
        "timestamp":            flight.time,

        # api enriched data
        "airline_name":         SanitizeAirlineName((api.get("airline") or {}).get("name") or "N/A"),
        "airline_short":        (api.get("airline") or {}).get("short", "N/A"),
        "owner":                ((api.get("owner") or {}).get("name") or "N/A"),
        "status":               ((api.get("status") or {}).get("text") or "N/A"),
        "live":                 (api.get("status") or {}).get("live", False),
        "aircraft_model":       ((api.get("aircraft") or {}).get("model") or {}).get("text", "N/A"),
        "aircraft_age":         (api.get("aircraft") or {}).get("age", "N/A"),
        "images":               ((api.get("aircraft") or {}).get("images") or {}),
        "full_origin":          ((api.get("airport") or {}).get("origin") or {}).get("name", "N/A"),
        "full_destination":     ((api.get("airport") or {}).get("destination") or {}).get("name", "N/A"),
        "origin_city":          ((api.get("airport") or {}).get("origin") or {}).get("position", {}).get("region", {}).get("city", "N/A"),
        "destination_city":     ((api.get("airport") or {}).get("destination") or {}).get("position", {}).get("region", {}).get("city", "N/A"),
        "origin_terminal":      ((api.get("airport") or {}).get("origin") or {}).get("info", {}).get("terminal", "N/A"),
        "origin_gate":          ((api.get("airport") or {}).get("origin") or {}).get("info", {}).get("gate", "N/A"),
        "destination_terminal": ((api.get("airport") or {}).get("destination") or {}).get("info", {}).get("terminal", "N/A"),
        "destination_gate":     ((api.get("airport") or {}).get("destination") or {}).get("info", {}).get("gate", "N/A"),
        "scheduled_departure":  ((api.get("time") or {}).get("scheduled") or {}).get("departure", "N/A"),
        "scheduled_arrival":    ((api.get("time") or {}).get("scheduled") or {}).get("arrival", "N/A"),
        "real_departure":       ((api.get("time") or {}).get("real") or {}).get("departure", "N/A"),
        "estimated_arrival":    ((api.get("time") or {}).get("estimated") or {}).get("arrival", "N/A"),
        "eta":                  ((api.get("time") or {}).get("other") or {}).get("eta", "N/A"),
        "flight_time":          str(round(int(((api.get("time") or {}).get("historical") or {}).get("flighttime") or 0) / 60)) + " min",
        "delay": FormatDelay(round(int(((api.get("time") or {}).get("historical") or {}).get("delay") or 0) / 60)),
        "fr24_link":            f"https://www.flightradar24.com/{flight.callsign}/{flight.id}",
    }

def FindClosestFlight(current_flights, target_lat, target_lon):
    flights_with_distance  = {}
    print(f"Current flights to compare: {[f.callsign for f in current_flights]}")
    for flight in current_flights:
        flight_lat = flight.latitude
        flight_lon = flight.longitude
        distance = (target_lat - flight_lat)**2 + (target_lon - flight_lon)**2
        flights_with_distance[flight.id] = {"flight": flight, "distance": distance}
    closest_flight = min(flights_with_distance.values(), key=lambda x: x["distance"])
    print(f"Closest flight: {closest_flight['flight'].callsign} at distance {closest_flight['distance']}")
    return {closest_flight["flight"].id : closest_flight}

def NotificationTemplate(flight_data):
    msg = (
        f" Airline: {flight_data['airline_name']}\n"
        f" Callsign: {flight_data['callsign']}\n"
        f" Flight number: {flight_data['flight_number']}\n"
        f" Aircraft Type: {flight_data['aircraft_code']}\n"
        f" From: {flight_data['origin']}\n"
        f" To: {flight_data['destination']}\n"
        f" Altitude: {flight_data['altitude']}\n"
    )
    return msg
def SanitizeAirlineName(name):
    return re.sub(r'\s*\(.*?\)', '', name).strip()

def FormatDelay(delay_min):
    d = int(delay_min)
    if d <= -5:
        return f"{abs(d)} min early"
    elif -5 < d <= 5:
        return "on time"
    elif 5 < d <= 15:
        return f"{d} min late"
    elif 15 < d <= 30:
        return f"slightly delayed · {d} min"
    else:
        return f"delayed · {d} min"