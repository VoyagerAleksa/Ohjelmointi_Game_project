import mysql.connector
import random
import math
import matplotlib.pyplot as plt
import json
from PIL import Image

connection = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='game_project',
    user='boris',
    password='Bubalar60',
    autocommit=True,
    charset = 'utf8mb4',
    use_unicode = True
)

cursor = connection.cursor()

class Directions:
    def __init__(self, lat1, lon1, lat2, lon2):
        self.lat1_r = math.radians(lat1)
        self.lon1_r = math.radians(lon1)
        self.lat2_r = math.radians(lat2)
        self.lon2_r = math.radians(lon2)
        self.deg_direction = self.direction_degrees()

    def direction_degrees(self):
        dist_lon = self.lon2_r - self.lon1_r
        x = math.sin(dist_lon) * math.cos(self.lat2_r)
        y = (math.cos(self.lat1_r) * math.sin(self.lat2_r) -
             math.sin(self.lat1_r) * math.cos(self.lat2_r) * math.cos(dist_lon))
        deg_direction = math.atan2(x,y)
        direction = (math.degrees(deg_direction) + 360) % 360
        return direction

    def cardinal_directions(self):
        direction = self.direction_degrees()
        if direction >= 337.5 or direction < 22.5:
            return "North(N)"
        elif direction < 67.5:
            return "Northeast(NE)"
        elif direction < 112.5:
            return "East(E)"
        elif direction < 157.5:
            return "Southeast(SE)"
        elif direction < 202.5:
            return "South(S)"
        elif direction < 247.5:
            return "Southwest(SW)"
        elif direction < 292.5:
            return "West(W)"
        else:  # 292.5-337.5
            return "NorthWest(NW)"

    def distance_km(self):
        dlat = self.lat2_r - self.lat1_r
        dlon = self.lon2_r - self.lon1_r

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(self.lat1_r) * math.cos(self.lat2_r) *
             math.sin(dlon / 2) ** 2)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        R = 6371
        return R * c


class CompassVisualizer:
    def __init__(self, compass_image_path):
        self.img = Image.open(compass_image_path)
        self.arrow_length = 0.4

    def visualize_direction(self, compass_object, save_path="compass.png", show_image=True):
        deg_direction = compass_object.deg_direction
        distance_km = compass_object.distance_km()

        fig, ax = plt.subplots(figsize=(6, 6), facecolor='black')
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_aspect('equal')
        ax.axis('off')


        rotation_angle = deg_direction
        rotated_img = self.img.rotate(rotation_angle, expand=True)


        img_width = 1.8
        img_height = img_width * (self.img.height / self.img.width)
        ax.imshow(rotated_img, extent=[-img_width / 2, img_width / 2, -img_height / 2, img_height / 2])

        ax.arrow(0, 0, 0, self.arrow_length,
                 head_width=0.08, head_length=0.1,
                 fc='red', ec='darkred', linewidth=4, zorder=10)

        ax.text(0, 0.9, f'Distance: {distance_km:.0f}km',
                ha='center', va='center', fontsize=20,
                color='white', weight='bold', zorder=11)

        plt.tight_layout(pad=0)
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='black')
        if show_image:
            plt.show()
        plt.close()


def get_airport_coordinates(icao):
    global cursor

    query = "SELECT latitude_deg, longitude_deg FROM airport WHERE ident LIKE %s LIMIT 1"
    cursor.execute(query, (icao,))

    coords = cursor.fetchone()

    if coords:
        cursor.fetchall()
        return coords[0], coords[1]

    cursor.fetchall()
    return None, None

def run_airport_distance(code1,code2):
    coords1 = get_airport_coordinates(code1)
    coords2 = get_airport_coordinates(code2)
    print(coords1, coords2)
    if not coords1 or not coords2:
        print("No airports")
        return coords1, coords2
    return coords1, coords2

IMAGE_PATH = r"assets/Compass.png"
compass_img = CompassVisualizer(IMAGE_PATH)

"""coords1, coords2 = run_airport_distance()

if coords1 and coords2:
    compass = Directions(coords1[0], coords1[1], coords2[0], coords2[1])
    print(f"Direction: {compass.cardinal_directions()}")
    print(f"Distance: {compass.distance_km():.0f} km")
    compass_img.visualize_direction(compass)
"""
def get_neighbors(country):
    query_center = """
                   SELECT AVG(latitude_deg), AVG(longitude_deg)
                   FROM airport AS a
                            JOIN country AS c ON a.iso_country = c.iso_country
                   WHERE c.name = %s \
                   """
    cursor.execute(query_center, (country,))
    center = cursor.fetchone()
    if not center:
        print("Country not found!")
        return

    lat1, lon1 = center

    query_neighbors = """
                      SELECT c2.name, \
                             c2.iso_country,
                             ROUND(6371 * ACOS(
                                     COS(RADIANS(%s)) * COS(RADIANS(AVG(a2.latitude_deg))) *
                                     COS(RADIANS(AVG(a2.longitude_deg)) - RADIANS(%s)) +
                                     SIN(RADIANS(%s)) * SIN(RADIANS(AVG(a2.latitude_deg)))
                                          )) AS km
                      FROM country AS c2
                               JOIN airport AS a2 ON a2.iso_country = c2.iso_country
                      WHERE c2.name != %s
                      GROUP BY c2.name, c2.iso_country
                      HAVING km < 800
                      ORDER BY km \
                      """

    cursor.execute(query_neighbors, (lat1, lon1, lat1, country))
    neighbors = cursor.fetchall()

    print("Neighbors of " + country + ":")
    for neigh in neighbors:
        print("  " + neigh[0] + " (" + neigh[1] + ") - " + str(neigh[2]) + " km")


def spawn_baggage_between_countries(cursor, start_country_name, dest_country_name):

    # Get country code based on country name
    cursor.execute("SELECT iso_country FROM country WHERE name LIKE %s LIMIT 1", (f"%{start_country_name}%",))
    start_result = cursor.fetchone()
    if not start_result: return None

    cursor.execute("SELECT iso_country FROM country WHERE name LIKE %s LIMIT 1", (f"%{dest_country_name}%",))
    dest_result = cursor.fetchone()
    if not dest_result: return None

    start_code, dest_code = start_result[0], dest_result[0]

    # Get bounds
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
        print("For for any of the country is not found")
        return None

    min_lat = min(bounds1[0], bounds2[0])
    max_lat = max(bounds1[1], bounds2[1])
    min_lon = min(bounds1[2], bounds2[2])
    max_lon = max(bounds1[3], bounds2[3])

   #Luggage spawn
    query = """
            SELECT ident, latitude_deg, longitude_deg, name, iso_country
            FROM airport
            WHERE latitude_deg BETWEEN %s AND %s
              AND longitude_deg BETWEEN %s AND %s
              AND iso_country != %s
              AND type = "large_airport"
            ORDER BY RAND()
                LIMIT 1 \
            """
    cursor.execute(query, (min_lat, max_lat, min_lon, max_lon, dest_code))
    baggage = cursor.fetchone()
    cursor.fetchall()

    if baggage:
        return baggage[0]

    print(f"Airports not found")
    return None

def kysy_seuraava_maa(connection):
    cursor = connection.cursor()
    sql = """
        SELECT DISTINCT country.name, country.iso_country
        FROM country
        JOIN airport ON airport.iso_country = country.iso_country
        WHERE airport.continent = 'EU'
        ORDER BY country.name
    """
    cursor.execute(sql)
    countries = cursor.fetchall()

    print("\nMihin maahan haluat lentää seuraavaksi?\n")
    for i, country in enumerate(countries, start=1):
        print(f"{i}. {country[0]}")

    while True:
        try:
            choice = int(input("\nValitse maan numero: "))
            if 1 <= choice <= len(countries):
                return countries[choice - 1][1]  # palauttaa iso_country
        except:
            pass
        print("Virheellinen valinta, yritä uudelleen.")

def valitse_lentokentta(connection, iso_country):
    cursor = connection.cursor()
    sql = """
        SELECT ident, name
        FROM airport
        WHERE iso_country = %s and type = "large_airport"
        ORDER BY name
    """
    cursor.execute(sql, (iso_country,))
    airports = cursor.fetchall()

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
            except:
                pass
            print("Virheellinen valinta, yritä uudelleen.")
        elif choice == "2":
            satunnainen = random.choice(airports)
            print(f"\nSatunnainen lentokenttä: {satunnainen[1]} ({satunnainen[0]})")
            return satunnainen[0]
        else:
            print("Virheellinen valinta, syötä 1 tai 2.")

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

def update_player_location(name, location):
    if airport_exists(location):
        cursor.execute(
            "UPDATE GAME SET current_location = %s WHERE player_name = %s",
            (location, name)
        )
def player_exists(name):
    cursor.execute("SELECT id FROM GAME WHERE player_name = %s", (name,))
    return cursor.fetchone() is not None


def register_new_player(name, input_value):
    #Airport, try ident
    coords = get_airport_coordinates(input_value)
    if coords[0]:
        cursor.execute("INSERT INTO GAME (player_name, current_level, current_location) VALUES (%s, 1, %s)",
                       (name, input_value))
        return True
    #Otherwise country
    airport = airport_exists(input_value)
    if airport:
        ident, a_name, c_name = airport
        cursor.execute("INSERT INTO GAME (player_name, current_level, current_location) VALUES (%s, 1, %s)",
                       (name, ident))
        print(f"Registered in {a_name} ({c_name})")
        return True
    print("Airport not found!")
    return False


def airport_exists(country):
    query = """
    SELECT a.ident, a.name, c.name
    FROM airport AS a JOIN country AS c ON a.iso_country = c.iso_country
    WHERE c.name = %s AND a.type = "large_airport" AND a.ident IS NOT NULL 
    ORDER BY RAND() LIMIT 1
    """
    cursor.execute(query, (country,))
    result = cursor.fetchone()
    return result

def final_screen(luggage, airports):
    query = """
    SELECT DISTINCT c.name, a.name FROM airport AS a, country AS c 
    WHERE ident = %s AND a.iso_country = c.iso_country
    """
    cursor.execute(query, (luggage,))
    country,airport = cursor.fetchone()
    print(f"Congratulations! You have successfully found your luggage in {airport}, {country}!")
    print(f"To found your luggage, you visited {len(airports)} airports.")
    for i in enumerate(airports,start=1):
        print(f"{i[0]}. {i[1]}")
    print("\nSee you next time!")

def get_current_location(icao):
    query = """
    SELECT name FROM airport WHERE ident = %s
    """
    cursor.execute(query, (icao,))
    result = cursor.fetchone()
    return result

def all_eu_countries():
    cursor = connection.cursor()
    query = """
        SELECT DISTINCT country.name, country.iso_country
        FROM country
        JOIN airport ON airport.iso_country = country.iso_country
        WHERE airport.continent = 'EU'
        ORDER BY country.name
    """
    cursor.execute(query)
    countries = cursor.fetchall()
    print("\nAll EU countries:")
    for i, country in enumerate(countries, start=1):
        print(f"{country[0]}")
    return countries

def save_current_location(coords, location_name, filename="map_weather/current_location.json"):
    data = {
        "name": get_current_location(location_name)[0],
        "lat": coords[0],
        "lng": coords[1]
    }

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
fly_last_time = input("\nWhere did you fly from last time? \n")
while True:
    country_name = input("Where did you fly to last time? \n").strip().upper()
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
current_airport_info = get_airport_coordinates(current_location)
if current_airport_info:
    cursor.execute("SELECT name FROM airport WHERE ident = %s", (current_location,))
    name = cursor.fetchone()[0]
    cursor.execute("SELECT name FROM country WHERE iso_country = (SELECT iso_country FROM airport WHERE ident = %s)", (current_location,))
    country = cursor.fetchone()[0]
    visited_airports.append((current_location, name, country))


coords_current = get_airport_coordinates(current_location)
coords_luggage = get_airport_coordinates(luggage)
save_current_location(coords_current, current_location)
if coords_current and coords_luggage:
    compass = Directions(coords_current[0], coords_current[1],
                        coords_luggage[0], coords_luggage[1])
    print("Lost bag:")
    print(f"Direction: {compass.cardinal_directions()}")
    print(f"Distance: {compass.distance_km():.0f} km")
    compass_img.visualize_direction(compass, "compass.png")

# maingame
while current_location != luggage:
    iso_country = kysy_seuraava_maa(connection)
    next_location = valitse_lentokentta(connection, iso_country)
    if not next_location:
        print("No airport selected, try again.")
        continue
    cursor.execute("SELECT name FROM airport WHERE ident = %s", (next_location,))
    name = cursor.fetchone()[0]
    cursor.execute("SELECT name FROM country WHERE iso_country = (SELECT iso_country FROM airport WHERE ident = %s)",
                   (next_location,))
    country = cursor.fetchone()[0]
    visited_airports.append((next_location, name, country))
    current_location = next_location
    coords_current = get_airport_coordinates(next_location)
    save_current_location(coords_current, current_location)
    if current_location == luggage:
        break

    coords_luggage = get_airport_coordinates(luggage)

    if coords_current and coords_luggage:
        compass = Directions(coords_current[0], coords_current[1],
                             coords_luggage[0], coords_luggage[1])
        print("Lost bag:")
        print(f"Direction: {compass.cardinal_directions()}")
        print(f"Distance: {compass.distance_km():.0f} km")
        compass_img.visualize_direction(compass)


final_screen(luggage, visited_airports)