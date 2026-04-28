import json

def save_game_state(name, current_location, luggage, visited_airports):
    visited_json = json.dumps(visited_airports)

    cursor.execute("""
        UPDATE GAME
        SET current_location = %s,
            luggage = %s,
            visited = %s
        WHERE player_name = %s
    """, (current_location, luggage, visited_json, name))

    connection.commit()


def load_game_state(name):
    cursor.execute("""
        SELECT current_location, luggage, visited
        FROM GAME
        WHERE player_name = %s
    """, (name,))

    result = cursor.fetchone()

    if not result:
        return None, None, []

    current_location, luggage, visited = result

    if visited:
        visited_airports = json.loads(visited)
    else:
        visited_airports = []

    return current_location, luggage, visited_airports

#after this
welcome_screen()

name = input("Enter your name: ").strip()
is_existing = player_exists(name)

#add this
visited_airports = []
luggage = None

if is_existing:
    print(f"Welcome back, {name}!")

    choice = input("Do you want to continue your saved game? (yes/no): ").strip().lower()

    if choice == "yes":
        current_location, luggage, visited_airports = load_game_state(name)

        if current_location:
            print(f"Loaded game! Current location: {current_location}")
        else:
            print("No saved game found, starting new game.")
            choice = "no"

    if choice != "yes":
        print("Starting a new game...")
        is_existing = False

if not is_existing:
    visited_airports = []
    print(f"Hello, {name}! Let's register you as a new player. Your adventure begins at difficulty level 1.")


#in here
while current_location != luggage:
#after
visited_airports.append((next_location, name, country))
current_location = next_location
#put this
save_game_state(name, current_location, luggage, visited_airports)

#and add
save_game_state(name, current_location, luggage, visited_airports)
#also before
final_screen(luggage, visited_airports)