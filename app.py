from flask import Flask, request, jsonify, session, send_from_directory
import mysql.connector

from difficulty_config import DifficultyConfig
from leaderboard import save_to_leaderboard, get_leaderboard_data
from distance_direction import Directions
from flight_emissions import FlightEmissions

app = Flask(__name__)
app.secret_key = '4e50547806c7a3595d3ffd549331232fd51ed516d5779331d6816e87a81976ab'

connection = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='game_project',
    user='root',
    password='BubaBuba60',
    autocommit=True,
    charset='utf8mb4',
    use_unicode=True
)
cursor = connection.cursor()


def choose_aircraft_type(distance_km):
    if distance_km < 1200:
        return "small"
    elif distance_km <= 2500:
        return "medium"
    return "large"


def safe_round(value, digits=2):
    try:
        return round(float(value), digits)
    except Exception:
        return 0


def get_airport_coordinates(icao):
    cursor.execute(
        "SELECT latitude_deg, longitude_deg FROM airport WHERE ident = %s LIMIT 1",
        (icao,)
    )
    row = cursor.fetchone()
    return (row[0], row[1]) if row else (None, None)


def get_airport_name(icao):
    cursor.execute("SELECT name FROM airport WHERE ident = %s LIMIT 1", (icao,))
    row = cursor.fetchone()
    return row[0] if row else icao


def get_airport_country(icao):
    cursor.execute("""
        SELECT c.name
        FROM airport a
        JOIN country c ON a.iso_country = c.iso_country
        WHERE a.ident = %s
        LIMIT 1
    """, (icao,))
    row = cursor.fetchone()
    return row[0] if row else "Unknown country"


def get_airport_iso_country(icao):
    cursor.execute("SELECT iso_country FROM airport WHERE ident = %s LIMIT 1", (icao,))
    row = cursor.fetchone()
    return row[0] if row else None


def get_country_name(iso_country):
    cursor.execute("SELECT name FROM country WHERE iso_country = %s LIMIT 1", (iso_country,))
    row = cursor.fetchone()
    return row[0] if row else iso_country


def get_all_european_countries():
    cursor.execute("""
        SELECT DISTINCT c.iso_country, c.name
        FROM country c
        JOIN airport a ON a.iso_country = c.iso_country
        WHERE a.continent = 'EU'
        ORDER BY c.name
    """)
    rows = cursor.fetchall()

    return [
        {"value": iso_country, "label": name}
        for iso_country, name in rows
    ]


def get_random_airport_by_country_name(country_name, airport_types):
    placeholders = ",".join(["%s"] * len(airport_types))
    query = f"""
        SELECT a.ident
        FROM airport a
        JOIN country c ON a.iso_country = c.iso_country
        WHERE c.name LIKE %s
          AND a.type IN ({placeholders})
          AND a.ident IS NOT NULL
          AND a.latitude_deg IS NOT NULL
          AND a.longitude_deg IS NOT NULL
        ORDER BY RAND()
        LIMIT 1
    """
    params = [f"%{country_name}%", *airport_types]
    cursor.execute(query, tuple(params))
    row = cursor.fetchone()
    return row[0] if row else None


def get_country_options_for_next_move():
    cursor.execute("""
        SELECT DISTINCT c.iso_country, c.name
        FROM airport a
        JOIN country c ON a.iso_country = c.iso_country
        WHERE a.continent = 'EU'
          AND a.ident IS NOT NULL
          AND a.latitude_deg IS NOT NULL
          AND a.longitude_deg IS NOT NULL
        ORDER BY c.name
    """)
    rows = cursor.fetchall()

    return [{"value": row[0], "label": row[1]} for row in rows]


def get_airports_in_country(iso_country, airport_types, current_location=None):
    placeholders = ",".join(["%s"] * len(airport_types))
    query = f"""
        SELECT ident, name
        FROM airport
        WHERE iso_country = %s
          AND type IN ({placeholders})
          AND ident IS NOT NULL
          AND latitude_deg IS NOT NULL
          AND longitude_deg IS NOT NULL
    """
    params = [iso_country, *airport_types]

    if current_location:
        query += " AND ident != %s"
        params.append(current_location)

    query += " ORDER BY name"
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()

    return [{"value": row[0], "label": row[1]} for row in rows]


def enumerate_options(raw_options):
    return [
        {"index": i + 1, "value": opt["value"], "label": opt["label"]}
        for i, opt in enumerate(raw_options)
    ]


def spawn_baggage_between_countries(start_country_name, dest_country_name):
    cursor.execute(
        "SELECT iso_country FROM country WHERE name LIKE %s LIMIT 1",
        (f"%{start_country_name}%",)
    )
    start_result = cursor.fetchone()
    if not start_result:
        return None

    cursor.execute(
        "SELECT iso_country FROM country WHERE name LIKE %s LIMIT 1",
        (f"%{dest_country_name}%",)
    )
    dest_result = cursor.fetchone()
    if not dest_result:
        return None

    start_code, dest_code = start_result[0], dest_result[0]

    cursor.execute("""
        SELECT MIN(latitude_deg), MAX(latitude_deg), MIN(longitude_deg), MAX(longitude_deg)
        FROM airport
        WHERE iso_country = %s
    """, (start_code,))
    bounds1 = cursor.fetchone()

    cursor.execute("""
        SELECT MIN(latitude_deg), MAX(latitude_deg), MIN(longitude_deg), MAX(longitude_deg)
        FROM airport
        WHERE iso_country = %s
    """, (dest_code,))
    bounds2 = cursor.fetchone()

    if not bounds1 or not bounds2:
        return None

    min_lat = min(bounds1[0], bounds2[0])
    max_lat = max(bounds1[1], bounds2[1])
    min_lon = min(bounds1[2], bounds2[2])
    max_lon = max(bounds1[3], bounds2[3])

    query = """
        SELECT ident, latitude_deg, longitude_deg, name, iso_country
        FROM airport
        WHERE latitude_deg BETWEEN %s AND %s
          AND longitude_deg BETWEEN %s AND %s
          AND iso_country != %s
          AND type = 'large_airport'
        ORDER BY RAND()
        LIMIT 1
    """
    cursor.execute(query, (min_lat, max_lat, min_lon, max_lon, dest_code))
    baggage = cursor.fetchone()

    if baggage:
        return baggage[0]

    return None


def build_setup_question(game_state):
    countries = get_all_european_countries()
    setup_stage = game_state.get('setup_stage', 'start_country')

    if not countries:
        raise ValueError("No European countries found in database")

    if setup_stage == 'start_country':
        game_state['question_stage'] = 'setup'
        game_state['question_text'] = 'Which country did you fly from last time?'
        game_state['options'] = enumerate_options(countries)
        return

    if setup_stage == 'destination_country':
        game_state['question_stage'] = 'setup'
        game_state['question_text'] = 'Which country did you fly to last time?'
        game_state['options'] = enumerate_options(countries)
        return


def build_country_question(game_state):
    raw_options = get_country_options_for_next_move()

    if not raw_options:
        raise ValueError("Database returned no available European countries")

    game_state['question_stage'] = 'country'
    game_state['selected_country'] = None
    game_state['question_text'] = 'Which country do you want to fly to next?'
    game_state['options'] = enumerate_options(raw_options)


def build_airport_question(game_state, iso_country):
    level_config = DifficultyConfig(game_state['difficulty_level'])
    raw_options = get_airports_in_country(
        iso_country,
        level_config.airport_types,
        current_location=game_state['current_location']
    )

    if not raw_options:
        game_state['feedback'] = 'No airports found in selected country.'
        build_country_question(game_state)
        return

    country_name = get_country_name(iso_country)
    game_state['question_stage'] = 'airport'
    game_state['selected_country'] = iso_country
    game_state['question_text'] = f'Which airport in {country_name} do you want to fly to?'
    game_state['options'] = enumerate_options(raw_options)


def finalize_game_setup(game_state):
    level_config = DifficultyConfig(game_state['difficulty_level'])

    start_country_name = game_state['start_country_name']
    destination_country_name = game_state['destination_country_name']

    current_location = get_random_airport_by_country_name(
        destination_country_name,
        level_config.airport_types
    )
    luggage_location = spawn_baggage_between_countries(
        start_country_name,
        destination_country_name
    )

    if not current_location:
        raise ValueError("Could not find starting airport in destination country")

    if not luggage_location:
        raise ValueError("Could not spawn luggage between selected countries")

    current_coords = get_airport_coordinates(current_location)
    luggage_coords = get_airport_coordinates(luggage_location)

    if not current_coords or current_coords[0] is None:
        raise ValueError("Could not resolve starting airport coordinates")

    if not luggage_coords or luggage_coords[0] is None:
        raise ValueError("Could not resolve luggage airport coordinates")

    direction_to_luggage = Directions(current_coords, luggage_coords)
    distance_to_luggage = direction_to_luggage.distance_km()

    game_state['game_started'] = True
    game_state['setup_stage'] = 'complete'

    game_state['current_location'] = current_location
    game_state['current_airport_name'] = get_airport_name(current_location)
    game_state['current_country_name'] = get_airport_country(current_location)

    game_state['luggage_location'] = luggage_location
    game_state['visited_airports'] = [
        {
            "icao": current_location,
            "name": get_airport_name(current_location),
            "country": get_airport_country(current_location)
        }
    ]

    game_state['lat'] = current_coords[0]
    game_state['lng'] = current_coords[1]
    game_state['heading'] = safe_round(direction_to_luggage.direction_degrees(), 2)
    game_state['m_direction'] = safe_round(direction_to_luggage.direction_degrees(), 2)
    game_state['distance_to_luggage'] = safe_round(distance_to_luggage, 2)
    game_state['flight_distance'] = 0

    game_state['aircraft_type'] = 'medium'
    game_state['aircraft_name'] = 'Waiting for flight'
    game_state['flight_co2'] = 0
    game_state['session_co2'] = 0

    game_state['feedback'] = (
        f"Current location: {game_state['current_airport_name']} in {game_state['current_country_name']}."
    )

    build_country_question(game_state)


def build_game_view(game_state):
    return {
        'map': {
            'name': game_state.get('current_airport_name', 'Unknown airport'),
            'lat': game_state.get('lat'),
            'lng': game_state.get('lng'),
            'heading': game_state.get('heading', 0),
            'm_direction': game_state.get('m_direction', 0)
        },
        'flight': {
            'distance_to_luggage': game_state.get('distance_to_luggage', 0),
            'flight_distance': game_state.get('flight_distance', 0),
            'aircraft_type': game_state.get('aircraft_type', 'medium'),
            'aircraft_name': game_state.get('aircraft_name', 'Waiting for flight'),
            'flight_co2': game_state.get('flight_co2', 0),
            'session_co2': game_state.get('session_co2', 0)
        },
        'panel': {
            'current_airport': game_state.get('current_airport_name', '—'),
            'question': game_state.get('question_text', 'Waiting for question...'),
            'options': game_state.get('options', []),
            'feedback': game_state.get('feedback', '')
        },
        'game': {
            'won': game_state.get('won', False),
            'player_name': game_state.get('player_name'),
            'difficulty_level': game_state.get('difficulty_level'),
            'visited_airports': game_state.get('visited_airports', []),
            'question_stage': game_state.get('question_stage', 'setup'),
            'setup_stage': game_state.get('setup_stage', 'start_country'),
            'game_started': game_state.get('game_started', False)
        }
    }


def initialize_new_game_state(player_name, level):
    game_state = {
        'player_name': player_name,
        'difficulty_level': level,
        'game_started': False,
        'won': False,

        'setup_stage': 'start_country',
        'question_stage': 'setup',

        'start_country_name': None,
        'destination_country_name': None,
        'selected_country': None,

        'current_location': None,
        'current_airport_name': None,
        'current_country_name': None,
        'luggage_location': None,

        'visited_airports': [],

        'lat': None,
        'lng': None,
        'heading': 0,
        'm_direction': 0,
        'distance_to_luggage': 0,
        'flight_distance': 0,

        'aircraft_type': 'medium',
        'aircraft_name': 'Waiting for flight',
        'flight_co2': 0,
        'session_co2': 0,

        'moves': 0,
        'question_text': '',
        'options': [],
        'feedback': ''
    }

    build_setup_question(game_state)
    return game_state


def apply_flight_move(game_state, next_location):
    current_location = game_state['current_location']
    current_coords = (game_state['lat'], game_state['lng'])

    next_coords = get_airport_coordinates(next_location)
    if not next_coords or next_coords[0] is None:
        game_state['feedback'] = 'Could not resolve destination coordinates.'
        build_country_question(game_state)
        return game_state, False, game_state['feedback']

    movement_direction = Directions(current_coords, next_coords)
    flight_distance = movement_direction.distance_km()

    aircraft_type = choose_aircraft_type(flight_distance)
    emissions = FlightEmissions(aircraft_type)
    flight_data = emissions.record_flight(flight_distance, current_location, next_location)

    previous_session_co2 = float(game_state.get('session_co2', 0))
    total_session_co2 = previous_session_co2 + float(flight_data.get('co2_kg', 0))

    luggage_location = game_state['luggage_location']
    luggage_coords = get_airport_coordinates(luggage_location)
    direction_to_luggage = Directions(next_coords, luggage_coords)
    distance_to_luggage = direction_to_luggage.distance_km()

    if not any(a["icao"] == next_location for a in game_state['visited_airports']):
        game_state['visited_airports'].append({
            "icao": next_location,
            "name": get_airport_name(next_location),
            "country": get_airport_country(next_location)
        })

    game_state['current_location'] = next_location
    game_state['current_airport_name'] = get_airport_name(next_location)
    game_state['current_country_name'] = get_airport_country(next_location)

    game_state['lat'] = next_coords[0]
    game_state['lng'] = next_coords[1]
    game_state['heading'] = safe_round(direction_to_luggage.direction_degrees(), 2)
    game_state['m_direction'] = safe_round(movement_direction.direction_degrees(), 2)
    game_state['distance_to_luggage'] = safe_round(distance_to_luggage, 2)
    game_state['flight_distance'] = safe_round(flight_distance, 2)

    game_state['aircraft_type'] = aircraft_type
    game_state['aircraft_name'] = flight_data.get('aircraft_name', aircraft_type)
    game_state['flight_co2'] = safe_round(flight_data.get('co2_kg', 0), 2)
    game_state['session_co2'] = safe_round(total_session_co2, 2)

    game_state['moves'] = int(game_state.get('moves', 0)) + 1
    game_state['selected_country'] = None

    if next_location == luggage_location:
        game_state['won'] = True
        game_state['question_text'] = 'You found the luggage!'
        game_state['options'] = []
        game_state['feedback'] = f"You found the luggage at {game_state['current_airport_name']}!"
        return game_state, True, game_state['feedback']

    game_state['feedback'] = f"Flight set to {game_state['current_airport_name']}."
    build_country_question(game_state)
    return game_state, True, game_state['feedback']


def apply_answer_to_game(game_state, answer):
    if game_state.get('won'):
        game_state['feedback'] = 'Game already finished.'
        return game_state, False, 'Game already finished.'

    try:
        answer_index = int(answer)
    except (TypeError, ValueError):
        return game_state, False, 'Please enter a valid number.'

    options = game_state.get('options', [])
    selected = next((opt for opt in options if opt['index'] == answer_index), None)

    if not selected:
        return game_state, False, 'Option number not found.'

    if not game_state.get('game_started'):
        setup_stage = game_state.get('setup_stage', 'start_country')

        if setup_stage == 'start_country':
            game_state['start_country_name'] = selected['label']
            game_state['setup_stage'] = 'destination_country'
            game_state['feedback'] = f"Origin selected: {selected['label']}"
            build_setup_question(game_state)
            return game_state, True, game_state['feedback']

        if setup_stage == 'destination_country':
            game_state['destination_country_name'] = selected['label']
            finalize_game_setup(game_state)
            return game_state, True, game_state['feedback']

        return game_state, False, 'Invalid setup stage.'

    stage = game_state.get('question_stage', 'country')

    if stage == 'country':
        selected_country = selected['value']
        build_airport_question(game_state, selected_country)
        game_state['feedback'] = f"Country selected: {selected['label']}"
        return game_state, True, game_state['feedback']

    if stage == 'airport':
        next_location = selected['value']
        return apply_flight_move(game_state, next_location)

    return game_state, False, 'Unknown question stage.'


def calculate_final_score(game_state):
    try:
        level_config = DifficultyConfig(game_state.get('difficulty_level', 'level2'))
    except ValueError:
        level_config = DifficultyConfig('level2')

    moves = int(game_state.get('moves', 0))
    emissions_kg = float(game_state.get('session_co2', 0))

    base_score = max(1000 - moves * 15, 0)
    score_with_multiplier = base_score * level_config.score_multiplier
    emissions_penalty = level_config.calculate_score_penalty(emissions_kg)
    return int(max(0, score_with_multiplier - emissions_penalty))


@app.before_request
def initialize_session():
    if 'game_state' not in session:
        session['game_state'] = None


@app.route('/')
def index():
    return send_from_directory('web_page', 'index.html')


@app.route('/index.html')
def index_html():
    return send_from_directory('web_page', 'index.html')


@app.route('/js.js')
def serve_js():
    return send_from_directory('web_page', 'js.js')


@app.route('/style.css')
def serve_css():
    return send_from_directory('web_page', 'style.css')


@app.route('/map.html')
def serve_map_html():
    return send_from_directory('map_weather', 'map.html')


@app.route('/map.js')
def serve_map_js():
    return send_from_directory('map_weather', 'map.js')


@app.route('/map_style.css')
def serve_map_css():
    return send_from_directory('map_weather', 'map_style.css')


@app.route('/weather.js')
def serve_weather_js():
    return send_from_directory('map_weather', 'weather.js')


@app.route('/assistant.js')
def serve_assistant_js():
    return send_from_directory('map_weather', 'assistant.js')


@app.route('/game_panel.js')
def serve_game_panel_js():
    return send_from_directory('map_weather', 'game_panel.js')


@app.route('/show_route.js')
def serve_show_route_js():
    return send_from_directory('show_route', 'show_route.js')


@app.route('/victory/<path:filename>')
def serve_victory_files(filename):
    return send_from_directory('victory', filename)


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('assets', filename)


@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('audio', filename)


@app.route('/api/start_game', methods=['POST'])
def start_game():
    data = request.get_json() or {}
    player_name = data.get('player_name', 'Guest')
    level = data.get('level', 'level2')

    try:
        DifficultyConfig(level)
        game_state = initialize_new_game_state(player_name, level)
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to start game: {str(e)}'}), 500

    session['game_state'] = game_state

    return jsonify({
        'success': True,
        'message': f'Game setup started for {player_name}',
        'view': build_game_view(game_state)
    })


@app.route('/api/game_view', methods=['GET'])
def get_game_view():
    game_state = session.get('game_state')

    if not game_state or not game_state.get('question_text'):
        return jsonify({'success': False, 'error': 'No active game'}), 400

    return jsonify({'success': True, 'view': build_game_view(game_state)})


@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    data = request.get_json() or {}
    answer = data.get('answer')

    if answer is None:
        return jsonify({'success': False, 'error': 'Missing answer'}), 400

    game_state = session.get('game_state', {})
    if not game_state:
        return jsonify({'success': False, 'error': 'No active game'}), 400

    try:
        updated_state, ok, message = apply_answer_to_game(game_state, answer)
        session['game_state'] = updated_state
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to apply answer: {str(e)}'}), 500

    response = {
        'success': ok,
        'message': message,
        'view': build_game_view(updated_state)
    }

    if updated_state.get('won'):
        response['won'] = True
        response['final_score'] = calculate_final_score(updated_state)

    return jsonify(response)


@app.route('/api/finish_game', methods=['POST'])
def finish_game():
    game_state = session.get('game_state', {})
    if not game_state:
        return jsonify({'success': False, 'error': 'No active game'}), 400

    return jsonify({
        'success': True,
        'won': game_state.get('won', False),
        'score': calculate_final_score(game_state),
        'player_name': game_state.get('player_name'),
        'difficulty_level': game_state.get('difficulty_level')
    })


@app.route('/api/leaderboard', methods=['GET'])
def api_leaderboard():
    level = request.args.get('level')
    leaders = get_leaderboard_data(level_filter=level, limit=10)
    return jsonify({'success': True, 'leaders': leaders})


@app.route('/api/save_score', methods=['POST'])
def api_save_score():
    data = request.get_json() or {}

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