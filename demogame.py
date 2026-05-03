from pick_country_airport import *
from location_playerRegistration import *
from luggage_spawner import *
from distance_direction import *
from flight_emissions import FlightEmissions
from save_to_JSON import *

connection = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='game_project',
    user='boris',
    password='Bubalar60',
    autocommit=True,
    charset='utf8mb4',
    use_unicode=True
)

cursor = connection.cursor()


def choose_aircraft_type(distance_km):
    if distance_km < 1200:
        return "small"
    elif distance_km <= 2500:
        return "medium"
    return "large"

welcome_screen()

name = input("Enter your name: ").strip()
is_existing = player_exists(name)

if is_existing:
    print(f"Welcome back, {name}!")
else:
    print(f"Hello, {name}! Let's register you as a new player. Your adventure begins at difficulty level 1.")

all_eu_countries()

fly_last_time = input("\nWhere did you fly from last time? \n").strip()

while True:
    country_name = input("Where did you fly to last time? \n").strip()
    airport_result = airport_exists(country_name)
    if airport_result:
        current_location = airport_result[0]
        print(f"\n\nCurrent location: {airport_result[1]} in {airport_result[2]}")
        break
    else:
        print("Country not found!")

if not is_existing:
    register_new_player(name, current_location)
else:
    update_player_location(name, current_location)

luggage = spawn_baggage_between_countries(cursor, fly_last_time, country_name)
if not luggage:
    print("Luggage spawn failed")
    exit()

visited_airports = []
current_airport_name = get_airport_name(current_location)
current_country_name = get_airport_country(current_location)
visited_airports.append((current_location, current_airport_name, current_country_name))

emissions = FlightEmissions("medium")

coords_current = get_airport_coordinates(current_location)
coords_luggage = get_airport_coordinates(luggage)

direction_to_luggage = Directions(coords_current, coords_luggage)
distance_to_luggage = direction_to_luggage.distance_km()

save_current_location(
    coords_current,
    current_location,
    direction_to_luggage.direction_degrees(),
    direction_to_luggage.direction_degrees(),
    distance_to_luggage,
    0,
    "medium",
    "Waiting for flight",
    0,
    0
)

save_visited_airports(visited_airports)

while current_location != luggage:
    iso_country = kysy_seuraava_maa(connection)
    next_location = valitse_lentokentta(connection, iso_country)

    if not next_location:
        print("No airport selected, try again.")
        continue

    next_airport_name = get_airport_name(next_location)
    next_country_name = get_airport_country(next_location)
    visited_airports.append((next_location, next_airport_name, next_country_name))

    coords_next = get_airport_coordinates(next_location)

    movement_direction = Directions(coords_current, coords_next)
    flight_distance = movement_direction.distance_km()

    aircraft_type = choose_aircraft_type(flight_distance)
    emissions.change_aircraft_type(aircraft_type)

    flight_data = emissions.record_flight(
        flight_distance,
        current_location,
        next_location
    )

    current_location = next_location
    coords_current = coords_next
    coords_luggage = get_airport_coordinates(luggage)

    direction_to_luggage = Directions(coords_current, coords_luggage)
    distance_to_luggage = direction_to_luggage.distance_km()

    save_current_location(
        coords_current,
        current_location,
        direction_to_luggage.direction_degrees(),
        movement_direction.direction_degrees(),
        distance_to_luggage,
        flight_distance,
        aircraft_type,
        flight_data["aircraft_name"],
        flight_data["co2_kg"],
        emissions.total_co2
    )

    save_visited_airports(visited_airports)

    if current_location == luggage:
        break

save_visited_airports(visited_airports)
emissions.display_flight_history()
emissions.display_cumulative_stats()
final_screen(luggage, visited_airports)