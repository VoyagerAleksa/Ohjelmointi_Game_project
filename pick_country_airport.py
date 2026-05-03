import random

def kysy_seuraava_maa(connection):
    local_cursor = connection.cursor()
    sql = """
        SELECT DISTINCT country.name, country.iso_country
        FROM country
        JOIN airport ON airport.iso_country = country.iso_country
        WHERE airport.continent = 'EU'
        ORDER BY country.name
    """
    local_cursor.execute(sql)
    countries = local_cursor.fetchall()

    print("\nMihin maahan haluat lentää seuraavaksi?\n")
    for i, country in enumerate(countries, start=1):
        print(f"{i}. {country[0]}")

    while True:
        try:
            choice = int(input("\nValitse maan numero: "))
            if 1 <= choice <= len(countries):
                return countries[choice - 1][1]
        except Exception:
            pass
        print("Virheellinen valinta, yritä uudelleen.")

def valitse_lentokentta(connection, iso_country):
    local_cursor = connection.cursor()
    sql = """
        SELECT ident, name
        FROM airport
        WHERE iso_country = %s and type = "large_airport"
        ORDER BY name
    """
    local_cursor.execute(sql, (iso_country,))
    airports = local_cursor.fetchall()

    if not airports:
        print("Ei saatavilla olevia lentokenttiä tässä maassa.")
        return None

    print("\nSaatavilla olevat lentokentät:\n")
    for i, airport in enumerate(airports, start=1):
        print(f"{i}. {airport[1]} ({airport[0]})")

    print("\nHaluatko valita tietyn lentokentän vai satunnaisen?")
    print("1 = Valitsen itse")
    print("2 = Satunnainen lentokenttä")

    while True:
        choice = input("Valinta (1 tai 2): ").strip()
        if choice == "1":
            try:
                airport_choice = int(input("Valitse lentokentän numero: "))
                if 1 <= airport_choice <= len(airports):
                    valittu = airports[airport_choice - 1]
                    print(f"\nValitsit lentokentän: {valittu[1]} ({valittu[0]})")
                    return valittu[0]
            except Exception:
                pass
            print("Virheellinen valinta, yritä uudelleen.")
        elif choice == "2":
            satunnainen = random.choice(airports)
            print(f"\nSatunnainen lentokenttä: {satunnainen[1]} ({satunnainen[0]})")
            return satunnainen[0]
        else:
            print("Virheellinen valinta, syötä 1 или 2.")
