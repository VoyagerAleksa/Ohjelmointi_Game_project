"""Flight Emissions Calculator"""

class FlightEmissions:
    AIRCRAFT_TYPES = {
        'small': {
            'name': 'ATR 72',
            'fuel_per_km': 0.045,
            'co2_per_liter': 2.31
        },
        'medium': {
            'name': 'Airbus A320',
            'fuel_per_km': 0.065,
            'co2_per_liter': 2.31
        },
        'large': {
            'name': 'Airbus A380',
            'fuel_per_km': 0.095,
            'co2_per_liter': 2.31
        }
    }

    CO2_PER_LITER = 2.31

    def __init__(self, aircraft_type='medium'):
        if aircraft_type not in self.AIRCRAFT_TYPES:
            raise ValueError(f"Invalid aircraft type: {aircraft_type}")
        self.aircraft_type = aircraft_type
        self.aircraft_data = self.AIRCRAFT_TYPES[aircraft_type]
        self.flights_history = []
        self.total_distance = 0
        self.total_fuel = 0
        self.total_co2 = 0

    def change_aircraft_type(self, new_type):
        if new_type not in self.AIRCRAFT_TYPES:
            raise ValueError(f"Invalid aircraft type: {new_type}")
        self.aircraft_type = new_type
        self.aircraft_data = self.AIRCRAFT_TYPES[new_type]

    def get_aircraft_name(self):
        return self.aircraft_data['name']

    def calculate_fuel_consumption(self, distance_km):
        return round(distance_km * self.aircraft_data['fuel_per_km'], 2)

    def calculate_co2_emissions(self, fuel_liters):
        return round(fuel_liters * self.CO2_PER_LITER, 2)

    def record_flight(self, distance_km, from_airport, to_airport):
        fuel = self.calculate_fuel_consumption(distance_km)
        co2 = self.calculate_co2_emissions(fuel)

        flight_data = {
            'from': from_airport,
            'to': to_airport,
            'distance_km': round(distance_km, 2),
            'fuel_liters': fuel,
            'co2_kg': co2,
            'aircraft_type': self.aircraft_type,
            'aircraft_name': self.get_aircraft_name()
        }

        self.flights_history.append(flight_data)
        self.total_distance += distance_km
        self.total_fuel += fuel
        self.total_co2 += co2

        return flight_data

    def get_totals(self):
        return {
            'distance': round(self.total_distance, 2),
            'fuel': round(self.total_fuel, 2),
            'co2': round(self.total_co2, 2),
            'flights': len(self.flights_history)
        }

    def display_flight_stats(self, flight_data):
        print("\nFLIGHT STATISTICS")
        print("Aircraft Type: " + flight_data['aircraft_name'])
        print("Distance: " + str(flight_data['distance_km']) + " km")
        print("Fuel Consumed: " + str(flight_data['fuel_liters']) + " liters")
        print("CO2 Emitted: " + str(flight_data['co2_kg']) + " kg")

    def display_cumulative_stats(self):
        print("\nCUMULATIVE FLIGHT STATISTICS")
        print("Total Flights: " + str(len(self.flights_history)))
        print("Total Distance: " + str(round(self.total_distance, 2)) + " km")
        print("Total Fuel Consumed: " + str(round(self.total_fuel, 2)) + " liters")
        print("Total CO2 Emitted: " + str(round(self.total_co2, 2)) + " kg")

    def display_flight_history(self):
        if not self.flights_history:
            print("\nNo flights recorded yet.")
            return

        print("\nFLIGHT HISTORY (" + str(len(self.flights_history)) + " flights)")
        for i, f in enumerate(self.flights_history, 1):
            print(
                "Flight " + str(i) + ": " +
                f['from'] + " to " + f['to'] +
                " | " + str(f['distance_km']) + " km" +
                " | Fuel: " + str(f['fuel_liters']) + " L" +
                " | CO2: " + str(f['co2_kg']) + " kg" +
                " | Aircraft: " + f['aircraft_name']
            )

    @staticmethod
    def co2_to_car_miles(co2_kg):
        return co2_kg / 0.4

    @staticmethod
    def co2_to_trees(co2_kg):
        return co2_kg / 20

    def reset_stats(self):
        self.flights_history = []
        self.total_distance = 0
        self.total_fuel = 0
        self.total_co2 = 0