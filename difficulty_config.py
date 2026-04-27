"""
Difficulty Configuration for Flight Game
Defines rules, hints, and challenges for each difficulty level.
"""

class DifficultyConfig:
    """
    Configuration class for game difficulty levels.
    Controls aircraft type, hint frequency, penalties, and scoring.
    """

    # Difficulty level configurations
    DIFFICULTY_LEVELS = {
        'level1': {
            'name': 'Level 1',
            'aircraft_type': 'small',
            'airport_types': ['large_airport'],  # Only major international airports
            'compass_accuracy': 'full',  # Shows exact direction + distance
            'hint_frequency': 1,  # Hints every flight
            'show_country_hints': True,
            'time_limit_minutes': None,  # No time limit
            'fuel_limit_liters': None,  # No fuel limit
            'emissions_penalty_multiplier': 0,  # No emissions penalty
            'score_multiplier': 0.8,
            'description': 'Major international airports only - perfect for beginners'
        },
        'level2': {
            'name': 'Level 2',
            'aircraft_type': 'medium',
            'airport_types': ['large_airport', 'medium_airport'],  # Major + regional airports
            'compass_accuracy': 'full',  # Shows exact direction + distance
            'hint_frequency': 1,  # Hints every flight
            'show_country_hints': False,
            'time_limit_minutes': None,  # No time limit
            'fuel_limit_liters': None,  # No fuel limit
            'emissions_penalty_multiplier': 0.05,  # Light penalty
            'score_multiplier': 1.0,
            'description': 'Major and regional airports - balanced challenge'
        },
        'level3': {
            'name': 'Level 3',
            'aircraft_type': 'large',
            'airport_types': ['large_airport', 'medium_airport', 'small_airport'],  # All airport types
            'compass_accuracy': 'direction_only',  # Direction only, no distance
            'hint_frequency': 2,  # Hints every 2nd flight
            'show_country_hints': False,
            'time_limit_minutes': 20,  # 20 minutes per flight
            'fuel_limit_liters': 4000,  # 4000L total fuel limit
            'emissions_penalty_multiplier': 0.15,  # Heavy penalty
            'score_multiplier': 1.5,
            'description': 'All airports including small airfields - challenging!'
        }
    }

    def __init__(self, difficulty_level='level2'):
        """
        Initialize difficulty configuration.

        Args:
            difficulty_level: 'level1', 'level2', or 'level3'
        """
        if difficulty_level not in self.DIFFICULTY_LEVELS:
            raise ValueError(f"Invalid difficulty level: {difficulty_level}. Must be 'level1', 'level2', or 'level3'")

        self.level = difficulty_level
        self.config = self.DIFFICULTY_LEVELS[difficulty_level]

        # Extract config values for easy access
        self.name = self.config['name']
        self.aircraft_type = self.config['aircraft_type']
        self.airport_types = self.config['airport_types']  # Add airport types
        self.compass_accuracy = self.config['compass_accuracy']
        self.hint_frequency = self.config['hint_frequency']
        self.show_country_hints = self.config['show_country_hints']
        self.time_limit_minutes = self.config['time_limit_minutes']
        self.fuel_limit_liters = self.config['fuel_limit_liters']
        self.emissions_penalty_multiplier = self.config['emissions_penalty_multiplier']
        self.score_multiplier = self.config['score_multiplier']
        self.description = self.config['description']

    def should_show_hint(self, flight_number):
        """
        Determine if a hint should be shown for the current flight.

        Args:
            flight_number: Current flight number (1-based)

        Returns:
            bool: True if hint should be shown
        """
        return flight_number % self.hint_frequency == 0

    def get_compass_display(self, direction_degrees, distance_km):
        """
        Get compass display based on difficulty level.

        Args:
            direction_degrees: Direction in degrees
            distance_km: Distance in kilometers

        Returns:
            dict: Display information for compass
        """
        if self.compass_accuracy == 'full':
            return {
                'show_direction': True,
                'show_distance': True,
                'direction_degrees': direction_degrees,
                'distance_km': distance_km,
                'message': f"Direction: {self._degrees_to_cardinal(direction_degrees)}, Distance: {distance_km:.0f} km"
            }
        elif self.compass_accuracy == 'direction_only':
            return {
                'show_direction': True,
                'show_distance': False,
                'direction_degrees': direction_degrees,
                'distance_km': None,
                'message': f"Direction: {self._degrees_to_cardinal(direction_degrees)} (distance hidden)"
            }
        else:
            return {
                'show_direction': False,
                'show_distance': False,
                'direction_degrees': None,
                'distance_km': None,
                'message': "Compass disabled for this difficulty"
            }

    def calculate_score_penalty(self, emissions_kg):
        """
        Calculate emissions penalty for scoring.

        Args:
            emissions_kg: Total CO2 emissions in kg

        Returns:
            float: Points to subtract from score
        """
        return emissions_kg * self.emissions_penalty_multiplier

    def is_time_limit_exceeded(self, flight_start_time, current_time):
        """
        Check if time limit is exceeded for current flight.

        Args:
            flight_start_time: Start time of flight (datetime)
            current_time: Current time (datetime)

        Returns:
            bool: True if time limit exceeded
        """
        if self.time_limit_minutes is None:
            return False

        time_elapsed = (current_time - flight_start_time).total_seconds() / 60
        return time_elapsed > self.time_limit_minutes

    def is_fuel_limit_exceeded(self, total_fuel_used):
        """
        Check if fuel limit is exceeded.

        Args:
            total_fuel_used: Total fuel used in liters

        Returns:
            bool: True if fuel limit exceeded
        """
        if self.fuel_limit_liters is None:
            return False

        return total_fuel_used > self.fuel_limit_liters

    def get_available_difficulties(self):
        """
        Get list of all available difficulty levels.

        Returns:
            list: List of difficulty level dictionaries
        """
        return [
            {
                'level': key,
                'name': config['name'],
                'description': config['description'],
                'score_multiplier': config['score_multiplier']
            }
            for key, config in self.DIFFICULTY_LEVELS.items()
        ]

    @staticmethod
    def _degrees_to_cardinal(degrees):
        """
        Convert degrees to cardinal direction.

        Args:
            degrees: Direction in degrees

        Returns:
            str: Cardinal direction
        """
        directions = [
            "North", "Northeast", "East", "Southeast",
            "South", "Southwest", "West", "Northwest"
        ]
        index = round(degrees / 45) % 8
        return directions[index]

    def __str__(self):
        """String representation of difficulty config."""
        return f"Difficulty: {self.name} ({self.level})"
