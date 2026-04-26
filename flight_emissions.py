"""Flight Emissions Calculator"""

class FlightEmissions:
    # Fuel consumption in liters per km
    AIRCRAFT_TYPES = {
        'small': {'name': 'Small Aircraft (ATR 72)', 'fuel_per_km': 0.045, 'co2_per_liter': 2.31},
        'medium': {'name': 'Medium Aircraft (Boeing 737/Airbus A320)', 'fuel_per_km': 0.065, 'co2_per_liter': 2.31},
        'large': {'name': 'Large Aircraft (Boeing 777/Airbus A380)', 'fuel_per_km': 0.095, 'co2_per_liter': 2.31}
    }
    CO2_PER_LITER = 2.31  # kg CO2 per liter of jet fuel

    def __init__(self, aircraft_type='medium'):
        # Initialize emissions calculator with aircraft type
        if aircraft_type not in self.AIRCRAFT_TYPES:
            raise ValueError(f"Invalid aircraft type: {aircraft_type}")
        self.aircraft_type = aircraft_type
        self.aircraft_data = self.AIRCRAFT_TYPES[aircraft_type]
        self.flights_history = []
        self.total_distance = 0
        self.total_fuel = 0
        self.total_co2 = 0

    def calculate_fuel_consumption(self, distance_km):
        # Calculate fuel consumption in liters
        return round(distance_km * self.aircraft_data['fuel_per_km'], 2)

    def calculate_co2_emissions(self, fuel_liters):
        # Calculate CO2 emissions in kg
        return round(fuel_liters * self.CO2_PER_LITER, 2)

    def record_flight(self, distance_km, from_airport, to_airport):
        # Record flight and track emissions
        fuel = self.calculate_fuel_consumption(distance_km)
        co2 = self.calculate_co2_emissions(fuel)
        flight_data = {'from': from_airport, 'to': to_airport, 'distance_km': round(distance_km, 2), 'fuel_liters': fuel, 'co2_kg': co2}
        self.flights_history.append(flight_data)
        self.total_distance += distance_km
        self.total_fuel += fuel
        self.total_co2 += co2

        return flight_data

    def display_flight_stats(self, flight_data):
        # Display single flight stats
        print("\nFLIGHT STATISTICS")
        print("Aircraft Type: " + self.aircraft_data['name'])
        print("Distance: " + str(flight_data['distance_km']) + " km")
        print("Fuel Consumed: " + str(flight_data['fuel_liters']) + " liters")
        print("CO2 Emitted: " + str(flight_data['co2_kg']) + " kg")

    def display_cumulative_stats(self):
        # Display total flight stats and environmental impact
        print("\nCUMULATIVE FLIGHT STATISTICS")
        print("Total Flights: " + str(len(self.flights_history)))
        print("Total Distance: " + str(self.total_distance) + " km")
        print("Total Fuel Consumed: " + str(self.total_fuel) + " liters")
        print("Total CO2 Emitted: " + str(self.total_co2) + " kg")
        print("\nEnvironmental Impact:")
        print("Metric tons of CO2: " + str(round(self.total_co2 / 1000, 2)))
        print("Equivalent car miles: " + str(round(self.co2_to_car_miles(self.total_co2), 0)))
        print("Trees needed to offset: " + str(round(self.co2_to_trees(self.total_co2), 0)))

    def display_flight_history(self):
        # Display all flights in chronological order
        if not self.flights_history:
            print("\nNo flights recorded yet.")
            return
        print("\nFLIGHT HISTORY (" + str(len(self.flights_history)) + " flights)")
        for i, f in enumerate(self.flights_history, 1):
            print("Flight " + str(i) + ": " + f['from'] + " to " + f['to'] + " | " + str(f['distance_km']) + " km | Fuel: " + str(f['fuel_liters']) + " L | CO2: " + str(f['co2_kg']) + " kg")

    @staticmethod
    def co2_to_car_miles(co2_kg):
        # Convert CO2 to car miles equivalent (0.4 kg CO2 per mile)
        return co2_kg / 0.4

    @staticmethod
    def co2_to_trees(co2_kg):
        # Convert CO2 to trees needed to offset (20 kg CO2 per tree/year)
        return co2_kg / 20

    def get_flight_data(self):
        # Return list of all flights
        return self.flights_history

    def get_totals(self):
        # Return summary statistics dictionary
        return {'distance': round(self.total_distance, 2), 'fuel': round(self.total_fuel, 2), 'co2': round(self.total_co2, 2), 'flights': len(self.flights_history)}

    def change_aircraft_type(self, new_type):
        # Change aircraft type
        if new_type not in self.AIRCRAFT_TYPES:
            raise ValueError(f"Invalid aircraft type: {new_type}")
        self.aircraft_type = new_type
        self.aircraft_data = self.AIRCRAFT_TYPES[new_type]
        print("\nAircraft changed to: " + self.aircraft_data['name'])

    def reset_stats(self):
        # Reset all statistics
        self.flights_history = []
        self.total_distance = 0
        self.total_fuel = 0
        self.total_co2 = 0
        print("\nStatistics reset.")


if __name__ == "__main__":
    # Test example
    e = FlightEmissions(aircraft_type='medium')
    f1 = e.record_flight(450, 'EFHK', 'LFPG')
    e.display_flight_stats(f1)
    f2 = e.record_flight(300, 'LFPG', 'LEMD')
    e.display_flight_stats(f2)
    f3 = e.record_flight(600, 'LEMD', 'LIRF')
    e.display_flight_stats(f3)
    e.display_flight_history()
    e.display_cumulative_stats()

