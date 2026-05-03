def spawn_baggage_between_countries(cursor, start_country_name, dest_country_name):
    cursor.execute("SELECT iso_country FROM country WHERE name LIKE %s LIMIT 1", (f"%{start_country_name}%",))
    start_result = cursor.fetchone()
    if not start_result:
        return None

    cursor.execute("SELECT iso_country FROM country WHERE name LIKE %s LIMIT 1", (f"%{dest_country_name}%",))
    dest_result = cursor.fetchone()
    if not dest_result:
        return None

    start_code, dest_code = start_result[0], dest_result[0]

    cursor.execute("""
        SELECT MIN(latitude_deg),
               MAX(latitude_deg),
               MIN(longitude_deg),
               MAX(longitude_deg)
        FROM airport
        WHERE iso_country = %s
    """, (start_code,))
    bounds1 = cursor.fetchone()

    cursor.execute("""
        SELECT MIN(latitude_deg),
               MAX(latitude_deg),
               MIN(longitude_deg),
               MAX(longitude_deg)
        FROM airport
        WHERE iso_country = %s
    """, (dest_code,))
    bounds2 = cursor.fetchone()

    if not bounds1 or not bounds2:
        print("Airport bounds not found")
        return None

    min_lat = min(bounds1[0], bounds2[0])
    max_lat = max(bounds1[1], bounds2[1])
    min_lon = min(bounds1[2], bounds2[2])
    max_lon = max(bounds1[3], bounds2[3])

    query = """
        SELECT ident, latitude_deg, longitude_deg, name, iso_country
        FROM airport
        WHERE latitude_deg BETWEEN %s AND %s
          AND longitude_deg BETWEEN %s AND %s
          AND iso_country != %s
          AND type = "large_airport"
        ORDER BY RAND()
        LIMIT 1
    """
    cursor.execute(query, (min_lat, max_lat, min_lon, max_lon, dest_code))
    baggage = cursor.fetchone()
    cursor.fetchall()

    if baggage:
        return baggage[0]

    print("Airports not found")
    return None