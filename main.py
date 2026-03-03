import os
from dotenv import load_dotenv
import mysql.connector
import math

load_dotenv()  # Load .env if using it

yhteys = mysql.connector.connect(
    host=os.getenv('DB_HOST', '127.0.0.1'),
    port=int(os.getenv('DB_PORT', 3306)),
    database=os.getenv('DB_NAME', 'game_project'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    autocommit=True
)

def geo_to_deg(lat1,lon1,lat2,lon2):
