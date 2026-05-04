"""
Difficulty configuration for the flight game.
Defines the gameplay rules for each difficulty level.
"""


class DifficultyConfig:
    """
    Configuration class for game difficulty levels.
    Controls airport pool, compass behavior, emissions penalty, and scoring.
    """

    DIFFICULTY_LEVELS = {
        'level1': {
            'name': 'Level 1',
            'airport_types': ['large_airport'],
            'compass_accuracy': 'full',
            'emissions_penalty_multiplier': 0.02,
            'score_multiplier': 1.0,
            'description': 'Major international airports only - perfect for beginners'
        },
        'level2': {
            'name': 'Level 2',
            'airport_types': ['large_airport', 'medium_airport'],
            'compass_accuracy': 'full',
            'emissions_penalty_multiplier': 0.08,
            'score_multiplier': 1.15,
            'description': 'Major and regional airports - balanced challenge'
        },
        'level3': {
            'name': 'Level 3',
            'airport_types': ['large_airport', 'medium_airport', 'small_airport'],
            'compass_accuracy': 'direction_only',
            'emissions_penalty_multiplier': 0.18,
            'score_multiplier': 1.3,
            'description': 'All airports including small airfields - challenging!'
        }
    }

    def __init__(self, difficulty_level='level2'):
        if difficulty_level not in self.DIFFICULTY_LEVELS:
            raise ValueError(
                f"Invalid difficulty level: {difficulty_level}. "
                f"Must be 'level1', 'level2', or 'level3'"
            )

        self.level = difficulty_level
        self.config = self.DIFFICULTY_LEVELS[difficulty_level]

        self.name = self.config['name']
        self.airport_types = self.config['airport_types']
        self.compass_accuracy = self.config['compass_accuracy']
        self.emissions_penalty_multiplier = self.config['emissions_penalty_multiplier']
        self.score_multiplier = self.config['score_multiplier']
        self.description = self.config['description']

    def get_compass_display(self, direction_degrees, distance_km):
        if self.compass_accuracy == 'full':
            return {
                'show_direction': True,
                'show_distance': True,
                'direction_degrees': direction_degrees,
                'distance_km': distance_km,
                'message': (
                    f"Direction: {self._degrees_to_cardinal(direction_degrees)}, "
                    f"Distance: {distance_km:.0f} km"
                )
            }

        if self.compass_accuracy == 'direction_only':
            return {
                'show_direction': True,
                'show_distance': False,
                'direction_degrees': direction_degrees,
                'distance_km': None,
                'message': (
                    f"Direction: {self._degrees_to_cardinal(direction_degrees)} "
                    f"(distance hidden)"
                )
            }

        return {
            'show_direction': False,
            'show_distance': False,
            'direction_degrees': None,
            'distance_km': None,
            'message': 'Compass disabled for this difficulty'
        }

    def calculate_score_penalty(self, emissions_kg):
        return emissions_kg * self.emissions_penalty_multiplier

    @classmethod
    def get_available_difficulties(cls):
        return [
            {
                'level': key,
                'name': config['name'],
                'description': config['description'],
                'score_multiplier': config['score_multiplier']
            }
            for key, config in cls.DIFFICULTY_LEVELS.items()
        ]

    @staticmethod
    def _degrees_to_cardinal(degrees):
        directions = [
            'North', 'Northeast', 'East', 'Southeast',
            'South', 'Southwest', 'West', 'Northwest'
        ]
        index = round(degrees / 45) % 8
        return directions[index]

    def __str__(self):
        return f"Difficulty: {self.name} ({self.level})"