import math
from geopy.distance import geodesic

class Directions:
    def __init__(self, current_coords, luggage_coords):
        self.lat1 = current_coords[0]
        self.lon1 = current_coords[1]
        self.lat2 = luggage_coords[0]
        self.lon2 = luggage_coords[1]
        self.lat1_r = math.radians(current_coords[0])
        self.lon1_r = math.radians(current_coords[1])
        self.lat2_r = math.radians(luggage_coords[0])
        self.lon2_r = math.radians(luggage_coords[1])
        self.deg_direction = self.direction_degrees()

    def direction_degrees(self):
        dist_lon = self.lon2_r - self.lon1_r
        x = math.sin(dist_lon) * math.cos(self.lat2_r)
        y = (math.cos(self.lat1_r) * math.sin(self.lat2_r) -
             math.sin(self.lat1_r) * math.cos(self.lat2_r) * math.cos(dist_lon))
        deg_direction = math.atan2(x,y)
        direction = (math.degrees(deg_direction) + 360) % 360
        return direction

    def cardinal_directions(self):
        direction = self.direction_degrees()
        if direction >= 337.5 or direction < 22.5:
            return "North(N)"
        elif direction < 67.5:
            return "Northeast(NE)"
        elif direction < 112.5:
            return "East(E)"
        elif direction < 157.5:
            return "Southeast(SE)"
        elif direction < 202.5:
            return "South(S)"
        elif direction < 247.5:
            return "Southwest(SW)"
        elif direction < 292.5:
            return "West(W)"
        else:  # 292.5-337.5
            return "NorthWest(NW)"

    def distance_km(self):
        coords1 = (self.lat1, self.lon1)
        coords2 = (self.lat2, self.lon2)
        distance = geodesic(coords1, coords2).km
        return distance