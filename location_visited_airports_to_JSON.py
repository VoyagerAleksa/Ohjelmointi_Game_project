import json

from location_playerRegistration import get_airport_name, get_airport_coordinates


def save_current_location(
    coords,
    location_icao,
    heading_to_luggage,
    movement_heading,
    distance_to_luggage,
    flight_distance,
    aircraft_type,
    aircraft_name,
    flight_co2,
    session_co2,
    filename="map_weather/current_location.json"
):
    data = {
        "name": get_airport_name(location_icao),
        "lat": coords[0],
        "lng": coords[1],
        "heading": round(heading_to_luggage, 2),
        "m_direction": round(movement_heading, 2),
        "distance_to_luggage": round(distance_to_luggage, 2),
        "flight_distance": round(flight_distance, 2),
        "aircraft_type": aircraft_type,
        "aircraft_name": aircraft_name,
        "flight_co2": round(flight_co2, 2),
        "session_co2": round(session_co2, 2)
    }

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def save_visited_airports(airports, filename="show_route_js/visited_route.json"):
    data = []

    for icao, airport_name, country_name in airports:
        coords = get_airport_coordinates(icao)
        if coords and coords[0] is not None:
            data.append({
                "name": airport_name,
                "lat": coords[0],
                "lng": coords[1]
            })

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)