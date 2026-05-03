from flask import Flask, request, jsonify, session, send_from_directory
import mysql.connector
import math
from difficulty_config import DifficultyConfig
from leaderboard import save_to_leaderboard, get_leaderboard_data

app = Flask(__name__)
app.secret_key = '4e50547806c7a3595d3ffd549331232fd51ed516d5779331d6816e87a81976ab'

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
    query = "SELECT latitude_deg, longitude_deg FROM airport WHERE ident = %s LIMIT 1"
    cursor.execute(query, (icao,))
    coords = cursor.fetchone()
    if coords:
        return coords[0], coords[1]
    return None, None


def calculate_distance(lat1, lon1, lat2, lon2):
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 6371 * c


@app.before_request
def initialize_session():
    if 'game_state' not in session:
        session['game_state'] = {
            'current_location': None,
            'visited_airports': [],
            'player_name': None,
            'game_started': False,
            'difficulty_level': None
        }


@app.route('/')
def index():
    return send_from_directory('web_page', 'index.html')


@app.route('/js.js')
def serve_js():
    return send_from_directory('web_page', 'js.js')


@app.route('/style.css')
def serve_css():
    return send_from_directory('web_page', 'style.css')


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('assets', filename)


@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('audio', filename)


@app.route('/api/start_game', methods=['POST'])
def start_game():
    data = request.get_json()

    player_name = data.get('player_name', 'Guest')
    level = data.get('level', 'level2')

    try:
        level_config = DifficultyConfig(level)
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400

    starting_airport = 'EFHK'
    coords = get_airport_coordinates(starting_airport)

    session['game_state'] = {
        'current_location': starting_airport,
        'visited_airports': [starting_airport],
        'player_name': player_name,
        'game_started': True,
        'difficulty_level': level
    }

    return jsonify({
        'success': True,
        'message': f'Game started for {player_name}',
        'current_location': starting_airport,
        'coordinates': coords,
        'level': {
            'level': level_config.level,
            'name': level_config.name,
            'description': level_config.description,
            'score_multiplier': level_config.score_multiplier,
            'airport_types': level_config.airport_types
        }
    })


@app.route('/api/game_state', methods=['GET'])
def get_game_state():
    game_state = session.get('game_state', {})
    if not game_state.get('game_started'):
        return jsonify({'success': False, 'error': 'No active game'}), 400

    return jsonify({
        'success': True,
        'game_state': game_state
    })


@app.route('/api/leaderboard', methods=['GET'])
def api_leaderboard():
    level = request.args.get('level')
    leaders = get_leaderboard_data(level_filter=level, limit=10)

    return jsonify({
        'success': True,
        'leaders': leaders
    })


@app.route('/api/save_score', methods=['POST'])
def api_save_score():
    data = request.get_json()

    player_name = data.get('player_name')
    difficulty_level = data.get('difficulty_level', 'level2')
    score = data.get('score')

    if not player_name:
        return jsonify({'success': False, 'error': 'Missing player_name'}), 400

    if score is None:
        return jsonify({'success': False, 'error': 'Missing score'}), 400

    ok = save_to_leaderboard(player_name, score, difficulty_level)

    if not ok:
        return jsonify({'success': False, 'error': 'Failed to save score'}), 500

    return jsonify({
        'success': True,
        'player_name': player_name,
        'difficulty_level': difficulty_level,
        'score': int(score)
    })


@app.route('/api/reset_game', methods=['POST'])
def reset_game():
    session.clear()
    return jsonify({'success': True, 'message': 'Game reset'})


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)