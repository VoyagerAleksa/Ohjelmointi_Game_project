def save_progress(name, current_location, level):
    cursor.execute("""
        UPDATE game
        SET current_location = %s,
            current_level = %s
        WHERE player_name = %s
    """, (current_location, level, name))
