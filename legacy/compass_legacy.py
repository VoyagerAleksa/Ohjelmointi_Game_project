import matplotlib.pyplot as plt
from PIL import Image

class CompassVisualizer:
    def __init__(self, compass_image_path):
        self.img = Image.open(compass_image_path).convert("RGBA")
        self.arrow_length = 0.4

    def visualize_direction(self, compass_object, save_path="compass.png", show_image=False):
        deg_direction = compass_object.deg_direction
        distance_km = compass_object.distance_km()

        fig, ax = plt.subplots(figsize=(6, 6))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        ax.set_position([0, 0, 1, 1])

        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_aspect('equal')
        ax.axis('off')

        rotated_img = self.img.rotate(deg_direction, expand=True)

        img_width = 1.8
        img_height = img_width * (rotated_img.height / rotated_img.width)

        ax.imshow(
            rotated_img,
            extent=[-img_width / 2, img_width / 2, -img_height / 2, img_height / 2]
        )
        ax.arrow(
            0, 0, 0, self.arrow_length,
            head_width=0.08, head_length=0.1,
            fc='red', ec='darkred', linewidth=4, zorder=10
        )
        ax.text(
            0, -0.9, f'Distance: {distance_km:.0f} km',
            ha='center', va='center',
            fontsize=20, color='black', weight='bold', zorder=11
        )
        plt.savefig(
            save_path,
            dpi=150,
            transparent=True,
            bbox_inches='tight',
            pad_inches=0
        )
        if show_image:
            plt.show()
        plt.close()

"""IMAGE_PATH = r"assets/Compass.png"
compass_img = CompassVisualizer(IMAGE_PATH)
coords1, coords2 = run_airport_distance()

if coords_current and coords_luggage:
    compass = Directions(coords_current[0], coords_current[1],
                        coords_luggage[0], coords_luggage[1])
    print("Lost bag:")
    print(f"Direction: {compass.cardinal_directions()}")
    print(f"Distance: {compass.distance_km():.0f} km")
    compass_img.visualize_direction(compass, "compass.png")   
"""