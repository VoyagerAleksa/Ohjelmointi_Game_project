from flask import Flask, render_template, request, jsonify, session, send_from_directory
import os
from flight_emissions import FlightEmissions
from difficulty_config import DifficultyConfig
import mysql.connector
import random
import math
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Database connection (reuse from demogame.py)
db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'game_project',
    'user': 'boris',
    'password': 'Bubalar60',
    'autocommit': True,
    'charset': 'utf8mb4',
    'use_unicode': True
}

connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# Import functions from demogame.py (refactor these to be importable)

def get_airport_coordinates(icao):
    """Get airport coordinates from database"""
    query = "SELECT latitude_deg, longitude_deg FROM airport WHERE ident LIKE %s LIMIT 1"
    cursor.execute(query, (icao,))
    coords = cursor.fetchone()
    if coords:
        cursor.fetchall()
        return coords[0], coords[1]
    cursor.fetchall()
    return None, None

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using haversine formula"""
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_r) * math.cos(lat2_r) *
         math.sin(dlon / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    R = 6371  # Earth's radius in km
    return R * c

@app.before_request
def initialize_session():
    """Initialize game session if it doesn't exist"""
    if 'game_state' not in session:
        session['game_state'] = {
            'emissions_calculator': None,  # Will be initialized when game starts
            'current_location': None,
            'visited_airports': [],
            'player_name': None,
            'game_started': False,
            'luggage_location': None,
            'difficulty': None,  # Difficulty configuration
            'flight_count': 0,  # Track flight number for hint frequency
            'flight_start_time': None,  # For time limits
            'total_fuel_used': 0  # For fuel limits
        }

@app.route('/')
def index():
    """Serve the main game page"""
    return send_from_directory('web_page', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from various directories"""
    if filename.startswith('web_page/'):
        return send_from_directory('web_page', filename[9:])
    elif filename.startswith('map_weather/'):
        return send_from_directory('map_weather', filename[12:])
    elif filename.startswith('show_route_js/'):
        return send_from_directory('show_route_js', filename[13:])
    elif filename.startswith('assets/'):
        return send_from_directory('assets', filename[7:])
    else:
        # Try to serve from root directory
        if os.path.exists(filename):
            return send_from_directory('.', filename)
        return "File not found", 404

@app.route('/api/get_difficulties', methods=['GET'])
def get_difficulties():
    """Get available difficulty levels"""
    try:
        difficulty_config = DifficultyConfig()
        difficulties = difficulty_config.get_available_difficulties()
        return jsonify({'difficulties': difficulties})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start_game', methods=['POST'])
def start_game():
    """Initialize a new game session with level selection"""
    data = request.get_json()
    player_name = data.get('player_name', 'Anonymous')
    level = data.get('level', 'level2')  # Changed from 'difficulty' to 'level'

    # Validate level
    try:
        level_config = DifficultyConfig(level)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # Initialize emissions calculator with level-based aircraft
    emissions = FlightEmissions(aircraft_type=level_config.aircraft_type)

    # Get starting location (implement this logic)
    # For now, use a default airport
    starting_airport = 'EFHK'  # Helsinki as default

    coords = get_airport_coordinates(starting_airport)
    if not coords:
        return jsonify({'error': 'Could not find starting airport'}), 500

    # Update session with level
    session['game_state'] = {
        'emissions_calculator': emissions.get_totals(),
        'current_location': starting_airport,
        'visited_airports': [{
            'icao': starting_airport,
            'name': 'Starting Airport',
            'country': 'Finland',
            'coords': coords
        }],
        'player_name': player_name,
        'game_started': True,
        'luggage_location': None,
        'level': level_config.__dict__,  # Store level config
        'flight_count': 0,
        'flight_start_time': datetime.now().isoformat(),
        'total_fuel_used': 0
    }

    # Store emissions calculator in a way Flask can handle
    session['emissions_data'] = {
        'aircraft_type': emissions.aircraft_type,
        'flights_history': [],
        'total_distance': 0,
        'total_fuel': 0,
        'total_co2': 0
    }

    return jsonify({
        'success': True,
        'message': f'Game started for {player_name} on {level_config.name}',
        'current_location': starting_airport,
        'coordinates': coords,
        'emissions': session['emissions_data'],
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
    """Get current game state"""
    if not session.get('game_state', {}).get('game_started', False):
        return jsonify({'error': 'No active game session'}), 400

    return jsonify({
        'current_location': session['game_state']['current_location'],
        'visited_airports': session['game_state']['visited_airports'],
        'player_name': session['game_state']['player_name'],
        'emissions': session.get('emissions_data', {}),
        'game_started': True
    })

@app.route('/api/fly', methods=['POST'])
def fly_to_airport():
    """Handle flight to a new airport with difficulty-based rules"""
    if not session.get('game_state', {}).get('game_started', False):
        return jsonify({'error': 'No active game session'}), 400

    # Get level configuration
    level_data = session['game_state'].get('level', {})
    level_config = DifficultyConfig(level_data.get('level', 'level2'))

    # Check time limit if applicable
    if level_config.time_limit_minutes:
        flight_start = session['game_state'].get('flight_start_time')
        if flight_start:
            start_time = datetime.fromisoformat(flight_start)
            if level_config.is_time_limit_exceeded(start_time, datetime.now()):
                return jsonify({
                    'error': f'Time limit exceeded! You had {level_config.time_limit_minutes} minutes per flight.',
                    'game_over': True
                }), 400

    # Check fuel limit if applicable
    if level_config.fuel_limit_liters:
        current_fuel = session['game_state'].get('total_fuel_used', 0)
        if level_config.is_fuel_limit_exceeded(current_fuel):
            return jsonify({
                'error': f'Fuel limit exceeded! Maximum {level_config.fuel_limit_liters}L allowed.',
                'game_over': True
            }), 400

    data = request.get_json()
    destination = data.get('destination')

    if not destination:
        return jsonify({'error': 'No destination provided'}), 400

    current_location = session['game_state']['current_location']

    # Get coordinates for both airports
    current_coords = get_airport_coordinates(current_location)
    dest_coords = get_airport_coordinates(destination)

    if not current_coords or not dest_coords:
        return jsonify({'error': 'Could not find airport coordinates'}), 400

    # Calculate distance
    distance = calculate_distance(current_coords[0], current_coords[1],
                                dest_coords[0], dest_coords[1])

    # Create emissions calculator from session data
    emissions = FlightEmissions(session.get('emissions_data', {}).get('aircraft_type', 'medium'))
    emissions.flights_history = session.get('emissions_data', {}).get('flights_history', [])
    emissions.total_distance = session.get('emissions_data', {}).get('total_distance', 0)
    emissions.total_fuel = session.get('emissions_data', {}).get('total_fuel', 0)
    emissions.total_co2 = session.get('emissions_data', {}).get('total_co2', 0)

    # Record the flight
    flight_data = emissions.record_flight(distance, current_location, destination)

    # Update flight tracking
    flight_count = session['game_state']['flight_count'] + 1
    fuel_used = session['game_state']['total_fuel_used'] + flight_data['fuel_liters']

    # Determine if hint should be shown based on difficulty
    show_hint = level_config.should_show_hint(flight_count)

    # Get compass display based on difficulty
    compass_info = level_config.get_compass_display(
        0,  # direction_degrees - you'll need to calculate this
        distance if show_hint else 0
    )

    # Update session
    session['game_state']['current_location'] = destination
    session['game_state']['visited_airports'].append({
        'icao': destination,
        'name': 'Destination Airport',  # You'll need to get actual name
        'country': 'Country',  # You'll need to get actual country
        'coords': dest_coords
    })
    session['game_state']['flight_count'] = flight_count
    session['game_state']['total_fuel_used'] = fuel_used
    session['game_state']['flight_start_time'] = datetime.now().isoformat()  # Reset timer

    # Update emissions data in session
    session['emissions_data'] = {
        'aircraft_type': emissions.aircraft_type,
        'flights_history': emissions.flights_history,
        'total_distance': emissions.total_distance,
        'total_fuel': emissions.total_fuel,
        'total_co2': emissions.total_co2
    }

    return jsonify({
        'success': True,
        'flight_data': flight_data,
        'new_location': destination,
        'coordinates': dest_coords,
        'distance': round(distance, 2) if show_hint else None,
        'emissions': session['emissions_data'],
        'compass': compass_info,
        'show_hint': show_hint,
        'flight_count': flight_count,
        'fuel_remaining': level_config.fuel_limit_liters - fuel_used if level_config.fuel_limit_liters else None,
        'time_limit': level_config.time_limit_minutes
    })

@app.route('/api/get_european_airports', methods=['GET'])
def get_european_airports():
    """Get list of European airports for the frontend, filtered by current level"""
    try:
        # Get current level from session if game is active
        level_types = ['large_airport', 'medium_airport', 'small_airport']  # Default to all
        if session.get('game_state', {}).get('game_started', False):
            level_data = session['game_state'].get('level', {})
            level_config = DifficultyConfig(level_data.get('level', 'level2'))
            level_types = level_config.airport_types

        # Build query with airport type filter
        placeholders = ','.join(['%s'] * len(level_types))
        query = f"""
        SELECT ident, name, iso_country, type
        FROM airport
        WHERE continent = 'EU' AND type IN ({placeholders})
        ORDER BY name
        LIMIT 200  # Increased limit for more airports
        """

        cursor.execute(query, level_types)
        airports = cursor.fetchall()

        airport_list = []
        for airport in airports:
            coords = get_airport_coordinates(airport[0])
            if coords:
                airport_list.append({
                    'icao': airport[0],
                    'name': airport[1],
                    'country': airport[2],
                    'type': airport[3],
                    'lat': coords[0],
                    'lng': coords[1]
                })

        return jsonify({
            'airports': airport_list,
            'level_filter': level_types,
            'total_count': len(airport_list)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset_game', methods=['POST'])
def reset_game():
    """Reset the current game session"""
    session.clear()
    return jsonify({'success': True, 'message': 'Game reset'})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
