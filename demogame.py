import mysql.connector
import random
import json

from distance_direction import *
from flight_emissions import FlightEmissions

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


def get_airport_coordinates(icao):
    query = "SELECT latitude_deg, longitude_deg FROM airport WHERE ident LIKE %s LIMIT 1"
    cursor.execute(query, (icao,))
    coords = cursor.fetchone()
    cursor.fetchall()

    if coords:
        return coords[0], coords[1]
    return None, None


def get_airport_name(icao):
    query = "SELECT name FROM airport WHERE ident = %s"
    cursor.execute(query, (icao,))
    result = cursor.fetchone()
    return result[0] if result else icao


def get_airport_country(icao):
    query = """
        SELECT c.name
        FROM airport a
        JOIN country c ON a.iso_country = c.iso_country
        WHERE a.ident = %s
    """
    cursor.execute(query, (icao,))
    result = cursor.fetchone()
    return result[0] if result else "Unknown country"


def spawn_baggage_between_countries(cursor, start_country_name, dest_country_name):
    cursor.execute("SELECT iso_country FROM country WHERE name LIKE %s LIMIT 1", (f"%{start_country_name}%",))
    start_result = cursor.fetchone()
    if not start_result:
        return None

    cursor.execute("SELECT iso_country FROM country WHERE name LIKE %s LIMIT 1", (f"%{dest_country_name}%",))
    dest_result = cursor.fetchone()
    if not dest_result:
        return None

    start_code, dest_code = start_result[0], dest_result[0]

    cursor.execute("""
        SELECT MIN(latitude_deg),
               MAX(latitude_deg),
               MIN(longitude_deg),
               MAX(longitude_deg)
        FROM airport
        WHERE iso_country = %s
    """, (start_code,))
    bounds1 = cursor.fetchone()

    cursor.execute("""
        SELECT MIN(latitude_deg),
               MAX(latitude_deg),
               MIN(longitude_deg),
               MAX(longitude_deg)
        FROM airport
        WHERE iso_country = %s
    """, (dest_code,))
    bounds2 = cursor.fetchone()

    if not bounds1 or not bounds2:
        print("Airport bounds not found")
        return None

    min_lat = min(bounds1[0], bounds2[0])
    max_lat = max(bounds1[1], bounds2[1])
    min_lon = min(bounds1[2], bounds2[2])
    max_lon = max(bounds1[3], bounds2[3])

    query = """
        SELECT ident, latitude_deg, longitude_deg, name, iso_country
        FROM airport
        WHERE latitude_deg BETWEEN %s AND %s
          AND longitude_deg BETWEEN %s AND %s
          AND iso_country != %s
          AND type = "large_airport"
        ORDER BY RAND()
        LIMIT 1
    """
    cursor.execute(query, (min_lat, max_lat, min_lon, max_lon, dest_code))
    baggage = cursor.fetchone()
    cursor.fetchall()

    if baggage:
        return baggage[0]

    print("Airports not found")
    return None


def kysy_seuraava_maa(connection):
    local_cursor = connection.cursor()
    sql = """
        SELECT DISTINCT country.name, country.iso_country
        FROM country
        JOIN airport ON airport.iso_country = country.iso_country
        WHERE airport.continent = 'EU'
        ORDER BY country.name
    """
    local_cursor.execute(sql)
    countries = local_cursor.fetchall()

    print("\nMihin maahan haluat lentää seuraavaksi?\n")
    for i, country in enumerate(countries, start=1):
        print(f"{i}. {country[0]}")

    while True:
        try:
            choice = int(input("\nValitse maan numero: "))
            if 1 <= choice <= len(countries):
                return countries[choice - 1][1]
        except Exception:
            pass
        print("Virheellinen valinta, yritä uudelleen.")


def valitse_lentokentta(connection, iso_country):
    local_cursor = connection.cursor()
    sql = """
        SELECT ident, name
        FROM airport
        WHERE iso_country = %s and type = "large_airport"
        ORDER BY name
    """
    local_cursor.execute(sql, (iso_country,))
    airports = local_cursor.fetchall()

    if not airports:
        print("Ei saatavilla olevia lentokenttiä tässä maassa.")
        return None

    print("\nSaatavilla olevat lentokentät:\n")
    for i, airport in enumerate(airports, start=1):
        print(f"{i}. {airport[1]} ({airport[0]})")

    print("\nHaluatko valita tietyn lentokentän vai satunnaisen?")
    print("1 = Valitsen itse")
    print("2 = Satunnainen lentokenttä")

    while True:
        choice = input("Valinta (1 tai 2): ").strip()
        if choice == "1":
            try:
                airport_choice = int(input("Valitse lentokentän numero: "))
                if 1 <= airport_choice <= len(airports):
                    valittu = airports[airport_choice - 1]
                    print(f"\nValitsit lentokentän: {valittu[1]} ({valittu[0]})")
                    return valittu[0]
            except Exception:
                pass
            print("Virheellinen valinta, yritä uudelleen.")
        elif choice == "2":
            satunnainen = random.choice(airports)
            print(f"\nSatunnainen lentokenttä: {satunnainen[1]} ({satunnainen[0]})")
            return satunnainen[0]
        else:
            print("Virheellinen valinta, syötä 1 или 2.")


def show_welcome_text():
    path = r"assets/welcome_screen.txt"
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
        print(text)


def get_random_meme():
    path = r"assets/meme.txt"
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines if line.strip()]
    return random.choice(lines)


def welcome_screen():
    show_welcome_text()
    previous_was_no = False

    while True:
        answer = input("Would you like to play? (yes/no): ").strip().lower()

        if answer == "yes":
            if previous_was_no:
                print("\n" + get_random_meme() + "\n")
            return
        elif answer == "no":
            previous_was_no = True
        else:
            print("Please answer yes or no.")


def airport_exists(country):
    query = """
        SELECT a.ident, a.name, c.name
        FROM airport AS a
        JOIN country AS c ON a.iso_country = c.iso_country
        WHERE c.name = %s AND a.type = "large_airport" AND a.ident IS NOT NULL
        ORDER BY RAND()
        LIMIT 1
    """
    cursor.execute(query, (country,))
    return cursor.fetchone()


def update_player_location(name, location):
    cursor.execute(
        "UPDATE GAME SET current_location = %s WHERE player_name = %s",
        (location, name)
    )


def player_exists(name):
    cursor.execute("SELECT id FROM GAME WHERE player_name = %s", (name,))
    return cursor.fetchone() is not None


def register_new_player(name, input_value):
    coords = get_airport_coordinates(input_value)

    if coords[0]:
        cursor.execute(
            "INSERT INTO GAME (player_name, current_level, current_location) VALUES (%s, 1, %s)",
            (name, input_value)
        )
        return True

    airport = airport_exists(input_value)
    if airport:
        ident, a_name, c_name = airport
        cursor.execute(
            "INSERT INTO GAME (player_name, current_level, current_location) VALUES (%s, 1, %s)",
            (name, ident)
        )
        print(f"Registered in {a_name} ({c_name})")
        return True

    print("Airport not found!")
    return False


def final_screen(luggage, airports):
    query = """
        SELECT DISTINCT c.name, a.name
        FROM airport AS a, country AS c
        WHERE ident = %s AND a.iso_country = c.iso_country
    """
    cursor.execute(query, (luggage,))
    country, airport = cursor.fetchone()

    print(f"Congratulations! You have successfully found your luggage in {airport}, {country}!")
    print(f"To found your luggage, you visited {len(airports)} airports.")
    for i, airport_info in enumerate(airports, start=1):
        print(f"{i}. {airport_info[1]}")
    print("\nSee you next time!")


def all_eu_countries():
    local_cursor = connection.cursor()
    query = """
        SELECT DISTINCT country.name, country.iso_country
        FROM country
        JOIN airport ON airport.iso_country = country.iso_country
        WHERE airport.continent = 'EU'
        ORDER BY country.name
    """
    local_cursor.execute(query)
    countries = local_cursor.fetchall()
    print("\nAll EU countries:")
    for country in countries:
        print(f"{country[0]}")
    return countries


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