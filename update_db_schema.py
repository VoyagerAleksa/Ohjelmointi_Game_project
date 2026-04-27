import mysql.connector

# Database connection
conn = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='game_project',
    user='boris',
    password='Bubalar60',
    autocommit=True,
    charset='utf8mb4',
    use_unicode=True
)

cursor = conn.cursor()

try:
    # Add difficulty_level to GAME table
    cursor.execute("ALTER TABLE GAME ADD COLUMN difficulty_level ENUM('easy', 'medium', 'hard') DEFAULT 'medium'")
    print('✅ Added difficulty_level to GAME table')
except mysql.connector.Error as err:
    print(f'❌ GAME table error: {err}')

try:
    # Add difficulty_level to LEADERBOARD table
    cursor.execute("ALTER TABLE LEADERBOARD ADD COLUMN difficulty_level ENUM('easy', 'medium', 'hard') DEFAULT 'medium'")
    print('✅ Added difficulty_level to LEADERBOARD table')
except mysql.connector.Error as err:
    print(f'❌ LEADERBOARD table error: {err}')

cursor.close()
conn.close()
print('Database schema update complete!')
