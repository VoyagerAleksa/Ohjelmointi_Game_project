import mysql.connector

from Demopeli.Demopeli import name, visited_airports

connection = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='game_project',
    user='marleenk',
    password='salasana',
    autocommit=True
)

cursor = connection.cursor()

def calculate_score(moves):
    return max(1000 - moves * 10, 0)

def save_to_leaderboard(player_name, score, level, flights):
    cursor.execute("""
        INSERT INTO LEADERBOARD (player_name, score, level, flights_number)
        VALUES (%s, %s, %s, %s)
    """, (player_name, score, level, flights))

def show_leaderboard():
    cursor.execute("""
        SELECT player_name, MAX(score) as best_score, level, flights_number
        FROM LEADERBOARD
        GROUP BY player_name
        ORDER BY best_score DESC
        LIMIT 10
    """)
    results = cursor.fetchall()

    print("\n🏆 LEADERBOARD (TOP 10) 🏆\n")
    for i, row in enumerate(results, start=1):
        print(f"{i}. {row[0]} | Score: {row[1]} | Level: {row[2]} | Flights: {row[3]}")

def show_player_rank(player_name):
    cursor.execute("""
        SELECT MAX(score) FROM LEADERBOARD WHERE player_name = %s
    """, (player_name,))
    player_best = cursor.fetchone()[0]

    if player_best is None:
        print("No ranking available.")
        return

    cursor.execute("""
        SELECT COUNT(*) + 1
        FROM (
            SELECT MAX(score) as best_score
            FROM LEADERBOARD
            GROUP BY player_name
        ) AS scores
        WHERE best_score > %s
    """, (player_best,))

    rank = cursor.fetchone()[0]
    print(f"\n🎯 Your rank: {rank}")

moves = len(visited_airports)

score = calculate_score(moves)
level = 1
flights = moves

save_to_leaderboard(name, score, level, flights)

show_leaderboard()
show_player_rank(name)