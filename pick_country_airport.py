import random
import mysql.connector

connection = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='game_project',
    user='marleenk',
    password='salasana',
    autocommit=True
)

cursor = connection.cursor()

def kysy_seuraava_maa(connection):
    cursor = connection.cursor()
    sql = """
        SELECT DISTINCT country.name, country.iso_country
        FROM country
        JOIN airport ON airport.iso_country = country.iso_country
        WHERE airport.continent = 'EU'
        ORDER BY country.name
    """
    cursor.execute(sql)
    countries = cursor.fetchall()

    print("\nMihin maahan haluat lentää seuraavaksi?\n")
    for i, country in enumerate(countries, start=1):
        print(f"{i}. {country[0]}")

    while True:
        try:
            choice = int(input("\nValitse maan numero: "))
            if 1 <= choice <= len(countries):
                return countries[choice - 1][1]  # palauttaa iso_country
        except:
            pass
        print("Virheellinen valinta, yritä uudelleen.")

def valitse_lentokentta(connection, iso_country):
    cursor = connection.cursor()
    sql = """
        SELECT ident, name
        FROM airport
        WHERE iso_country = %s
        ORDER BY name
    """
    cursor.execute(sql, (iso_country,))
    airports = cursor.fetchall()

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
            except:
                pass
            print("Virheellinen valinta, yritä uudelleen.")
        elif choice == "2":
            satunnainen = random.choice(airports)
            print(f"\nSatunnainen lentokenttä: {satunnainen[1]} ({satunnainen[0]})")
            return satunnainen[0]
        else:
            print("Virheellinen valinta, syötä 1 tai 2.")


iso_country = kysy_seuraava_maa(connection)
airport_ident = valitse_lentokentta(connection, iso_country)
print("\nSeuraava lentokenttä valittu:", airport_ident)
