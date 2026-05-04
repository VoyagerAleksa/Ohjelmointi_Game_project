import mysql.connector
import math
import matplotlib.pyplot as plt
from PIL import Image



connect = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='game_project',
    user='boris',
    password='Bubalar60',
    autocommit=True
)
cursor = connect.cursor()

class Directions:
    def __init__(self, lat1, lon1, lat2, lon2):
        self.lat1_r = math.radians(lat1)
        self.lon1_r = math.radians(lon1)
        self.lat2_r = math.radians(lat2)
        self.lon2_r = math.radians(lon2)
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
        dlat = self.lat2_r - self.lat1_r
        dlon = self.lon2_r - self.lon1_r

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(self.lat1_r) * math.cos(self.lat2_r) *
             math.sin(dlon / 2) ** 2)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        R = 6371
        return R * c


class CompassVisualizer:
    def __init__(self, compass_image_path):
        self.img = Image.open(compass_image_path)
        self.arrow_length = 0.4

    def visualize_direction(self, compass_object, save_path="compass.png", show_image=True):
        deg_direction = compass_object.deg_direction
        distance_km = compass_object.distance_km()

        fig, ax = plt.subplots(figsize=(6, 6), facecolor='black')
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_aspect('equal')
        ax.axis('off')


        rotation_angle = deg_direction
        rotated_img = self.img.rotate(rotation_angle, expand=True)


        img_width = 1.8
        img_height = img_width * (self.img.height / self.img.width)
        ax.imshow(rotated_img, extent=[-img_width / 2, img_width / 2, -img_height / 2, img_height / 2])

        ax.arrow(0, 0, 0, self.arrow_length,
                 head_width=0.08, head_length=0.1,
                 fc='red', ec='darkred', linewidth=4, zorder=10)

        ax.text(0, 0.9, f'Distance: {distance_km:.0f}km',
                ha='center', va='center', fontsize=20,
                color='white', weight='bold', zorder=11)

        plt.tight_layout(pad=0)
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='black')
        if show_image:
            plt.show()
        plt.close()


def get_airport_coordinates(name_part):
    global cursor

    query = "SELECT latitude_deg, longitude_deg FROM airport WHERE name LIKE %s LIMIT 1"
    cursor.execute(query, (f"%{name_part}%",))

    coords = cursor.fetchone()

    if coords:
        cursor.fetchall()
        return coords[0], coords[1]

    cursor.fetchall()
    return None, None

def run_airport_distance():
    code1 = input("Enter the city of the first airport: ").upper()
    code2 = input("Enter the city code of the second airport: ").upper()
    coords1 = get_airport_coordinates(code1)
    coords2 = get_airport_coordinates(code2)
    print(coords1, coords2)
    if not coords1 or not coords2:
        print("No airports")
        return coords1, coords2  # возвращаем для проверки
    return coords1, coords2

IMAGE_PATH = r"D:\Metropolia\Ohjelmointi1\Projekti\Compass.png"
compass_img = CompassVisualizer(IMAGE_PATH)

coords1, coords2 = run_airport_distance()

if coords1 and coords2:
    compass = Directions(coords1[0], coords1[1], coords2[0], coords2[1])
    print(f"Direction: {compass.cardinal_directions()}")
    print(f"Distance: {compass.distance_km():.0f} km")
    compass_img.visualize_direction(compass)
