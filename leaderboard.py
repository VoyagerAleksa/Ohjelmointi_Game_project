import mysql.connector
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
leaderboard_cursor = connection.cursor(dictionary=True)


def calculate_score(moves, level='level2', emissions_kg=0):
    try:
        level_config = DifficultyConfig(level)
    except ValueError:
        level_config = DifficultyConfig('level2')

    base_score = max(1000 - moves * 15, 0)
    score_with_multiplier = base_score * level_config.score_multiplier
    emissions_penalty = level_config.calculate_score_penalty(emissions_kg)
    final_score = max(0, score_with_multiplier - emissions_penalty)

    return int(final_score)


def save_to_leaderboard(player_name, score, difficulty_level='level2'):
    try:
        cursor.execute("""
            INSERT INTO leaderboard (player_name, difficulty_level, score)
            VALUES (%s, %s, %s)
        """, (player_name, difficulty_level, int(score)))
        return True
    except Exception as e:
        print("Save leaderboard error:", e)
        return False


def get_leaderboard_data(level_filter=None, limit=10):
    try:
        if level_filter:
            query = """
                SELECT player_name, difficulty_level, MAX(score) AS best_score
                FROM leaderboard
                WHERE difficulty_level = %s
                GROUP BY player_name, difficulty_level
                ORDER BY best_score DESC
                LIMIT %s
            """
            leaderboard_cursor.execute(query, (level_filter, limit))
        else:
            query = """
                SELECT player_name, difficulty_level, MAX(score) AS best_score
                FROM leaderboard
                GROUP BY player_name, difficulty_level
                ORDER BY best_score DESC
                LIMIT %s
            """
            leaderboard_cursor.execute(query, (limit,))

        rows = leaderboard_cursor.fetchall()

        leaderboard = []
        for i, row in enumerate(rows, start=1):
            leaderboard.append({
                'rank': i,
                'player_name': row['player_name'],
                'difficulty_level': row['difficulty_level'],
                'score': int(row['best_score'])
            })

        return leaderboard

    except Exception as e:
        print("Leaderboard fetch error:", e)
        return []


def show_leaderboard(level_filter=None):
    results = get_leaderboard_data(level_filter=level_filter, limit=10)

    if level_filter:
        title = f"🏆 LEADERBOARD - {level_filter.upper()} (TOP 10) 🏆"
    else:
        title = "🏆 LEADERBOARD - ALL LEVELS (TOP 10) 🏆"

    print(f"\n{title}\n")
    for row in results:
        print(
            f"{row['rank']}. {row['player_name']} | "
            f"Difficulty: {row['difficulty_level']} | "
            f"Score: {row['score']}"
        )