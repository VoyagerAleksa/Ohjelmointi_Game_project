import mysql.connector
import random

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
