from Demopeli.Demopeli import cursor, current_location, luggage, visited_airports, next_location, name, country


def save_progress(name, current_location, level):
    cursor.execute("""
        UPDATE game
        SET current_location = %s,
            current_level = %s
        WHERE player_name = %s
    """, (current_location, level, name))


#in here
while current_location != luggage:
#after
visited_airports.append((next_location, name, country))
#put this
save_progress(name, current_location, 1)