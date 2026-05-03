import mysql.connector
from flight_emissions import FlightEmissions
from difficulty_config import DifficultyConfig

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


def calculate_score(moves, level='level2', emissions_kg=0):
    """
    Calculate score with difficulty multipliers and emissions penalties.

    Args:
        moves: Number of flights taken
        level: 'level1', 'level2', or 'level3'
        emissions_kg: Total CO2 emissions in kg

    Returns:
        int: Final score
    """
    try:
        level_config = DifficultyConfig(level)
    except ValueError:
        level_config = DifficultyConfig('level2')

    base_score = max(1000 - moves * 15, 0)
    score_with_multiplier = base_score * level_config.score_multiplier
    emissions_penalty = level_config.calculate_score_penalty(emissions_kg)
    final_score = max(0, score_with_multiplier - emissions_penalty)

    return int(final_score)


def save_to_leaderboard(player_name, score, level, flights, level_name='level2', emissions_kg=0):
    """
    Save game results to leaderboard with difficulty tracking.

    Args:
        player_name: Player's name
        score: Final score
        level: Game level number (1, 2, or 3)
        flights: Number of flights taken
        level_name: Difficulty identifier ('level1', 'level2', 'level3')
        emissions_kg: Total CO2 emissions
    """
    cursor.execute("""
        INSERT INTO LEADERBOARD (player_name, score, level, flights_number, difficulty_level, total_emissions)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (player_name, score, level, flights, level_name, emissions_kg))


def show_leaderboard(level_filter=None):
    """
    Display leaderboard, optionally filtered by difficulty.

    Args:
        level_filter: 'level1', 'level2', 'level3', or None for all
    """
    if level_filter:
        query = """
            SELECT player_name, MAX(score) AS best_score, level, flights_number, difficulty_level, total_emissions
            FROM LEADERBOARD
            WHERE difficulty_level = %s
            GROUP BY player_name
            ORDER BY best_score DESC
            LIMIT 10
        """
        cursor.execute(query, (level_filter,))
        title = f"🏆 LEADERBOARD - {level_filter.upper()} (TOP 10) 🏆"
    else:
        query = """
            SELECT player_name, MAX(score) AS best_score, level, flights_number, difficulty_level, total_emissions
            FROM LEADERBOARD
            GROUP BY player_name
            ORDER BY best_score DESC
            LIMIT 10
        """
        cursor.execute(query)
        title = "🏆 LEADERBOARD - ALL LEVELS (TOP 10) 🏆"

    results = cursor.fetchall()

    print(f"\n{title}\n")
    for i, row in enumerate(results, start=1):
        difficulty_name = row[4].upper() if row[4] else 'UNKNOWN'
        total_emissions = row[5] or 0
        print(
            f"{i}. {row[0]} | "
            f"Score: {row[1]} | "
            f"Level: {row[2]} | "
            f"Flights: {row[3]} | "
            f"Difficulty: {difficulty_name} | "
            f"CO2: {total_emissions:.1f}kg"
        )


def show_player_rank(player_name, level=None):
    """
    Show player's rank, optionally for specific difficulty.

    Args:
        player_name: Player's name
        level: Specific difficulty level, or None for overall
    """
    if level:
        cursor.execute("""
            SELECT MAX(score) FROM LEADERBOARD
            WHERE player_name = %s AND difficulty_level = %s
        """, (player_name, level))

        player_best = cursor.fetchone()[0]

        if player_best is None:
            print(f"No ranking available for {player_name} on {level}.")
            return

        cursor.execute("""
            SELECT COUNT(*) + 1
            FROM (
                SELECT MAX(score) AS best_score
                FROM LEADERBOARD
                WHERE difficulty_level = %s
                GROUP BY player_name
            ) AS scores
            WHERE best_score > %s
        """, (level, player_best))

        rank = cursor.fetchone()[0]
        print(f"\n🎯 Your rank on {level.upper()}: {rank}")
    else:
        cursor.execute("""
            SELECT MAX(score) FROM LEADERBOARD
            WHERE player_name = %s
        """, (player_name,))

        player_best = cursor.fetchone()[0]

        if player_best is None:
            print(f"No ranking available for {player_name}.")
            return

        cursor.execute("""
            SELECT COUNT(*) + 1
            FROM (
                SELECT MAX(score) AS best_score
                FROM LEADERBOARD
                GROUP BY player_name
            ) AS scores
            WHERE best_score > %s
        """, (player_best,))

        rank = cursor.fetchone()[0]
        print(f"\n🎯 Your overall rank: {rank}")


if __name__ == "__main__":
    print("Score examples:")
    print(f"10 flights, level1, 500kg CO2: {calculate_score(10, 'level1', 500)}")
    print(f"10 flights, level2, 500kg CO2: {calculate_score(10, 'level2', 500)}")
    print(f"10 flights, level3, 500kg CO2: {calculate_score(10, 'level3', 500)}")

    show_leaderboard()
    show_leaderboard('level3')