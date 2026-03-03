import mysql.connector
import math

yhteys = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='game_project',
    user='boris',
    password='Bubalar60',
    autocommit=True
)

def geo_to_deg(lat1,lon1,lat2,lon2):
