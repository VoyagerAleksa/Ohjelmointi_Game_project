#!/usr/bin/env python3
"""
Test script for the difficulty system implementation.
Tests difficulty configuration, scoring, and emissions calculations.
"""

from difficulty_config import DifficultyConfig
from flight_emissions import FlightEmissions


def calculate_score(moves, difficulty_level='level2', emissions_kg=0):
    """Calculate score with difficulty multipliers and emissions penalties."""
    try:
        difficulty_config = DifficultyConfig(difficulty_level)
    except ValueError:
        difficulty_config = DifficultyConfig('level2')

    base_score = max(1000 - moves * 15, 0)
    score_with_multiplier = base_score * difficulty_config.score_multiplier
    emissions_penalty = emissions_kg * difficulty_config.emissions_penalty_multiplier
    final_score = max(0, score_with_multiplier - emissions_penalty)

    return int(final_score)


def test_difficulty_config():
    print('🧪 Testing Level Configuration...\n')

    for level in ['level1', 'level2', 'level3']:
        config = DifficultyConfig(level)
        print(f'✅ {level.upper()}: {config.name}')
        print(f'   Airport types: {config.airport_types}')
        print(f'   Compass mode: {config.compass_accuracy}')
        print(f'   Emissions penalty: {config.emissions_penalty_multiplier}')
        print(f'   Score multiplier: {config.score_multiplier}')
        print(f'   Description: {config.description}')
        print()


def test_scoring():
    print('🧪 Testing Score Calculations...\n')

    test_cases = [
        (5, 'level1', 100),
        (5, 'level2', 100),
        (5, 'level3', 100),
        (10, 'level1', 500),
        (10, 'level2', 500),
        (10, 'level3', 500),
    ]

    for moves, level, emissions in test_cases:
        score = calculate_score(moves, level, emissions)
        print(f'✅ {moves} flights, {level}, {emissions}kg CO2 → Score: {score}')


def test_emissions():
    print('\n🧪 Testing Emissions Calculations...\n')

    for aircraft in ['small', 'medium', 'large']:
        emissions = FlightEmissions(aircraft_type=aircraft)
        flight = emissions.record_flight(500, 'EFHK', 'LFPG')
        print(
            f"✅ {aircraft.upper()} aircraft, 500km: "
            f"{flight['fuel_liters']:.1f}L fuel, {flight['co2_kg']:.1f}kg CO2"
        )


def test_compass_display():
    print('\n🧪 Testing Compass Display...\n')

    configs = {
        'level1': DifficultyConfig('level1'),
        'level2': DifficultyConfig('level2'),
        'level3': DifficultyConfig('level3')
    }

    for level, config in configs.items():
        display = config.get_compass_display(45, 500)
        print(f"✅ {level.upper()}: {display['message']}")


def test_available_difficulties():
    print('\n🧪 Testing Available Difficulties...\n')

    difficulties = DifficultyConfig.get_available_difficulties()
    for difficulty in difficulties:
        print(
            f"✅ {difficulty['level']}: "
            f"{difficulty['name']} | "
            f"x{difficulty['score_multiplier']} | "
            f"{difficulty['description']}"
        )


def main():
    print('🚀 Running Level System Tests...\n')
    test_difficulty_config()
    test_scoring()
    test_emissions()
    test_compass_display()
    test_available_difficulties()
    print('\n🎉 All tests completed successfully!')


if __name__ == '__main__':
    main()