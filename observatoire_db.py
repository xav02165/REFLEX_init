import sqlite3
from pydantic import BaseModel, ValidationError 
import requests
from requests.exceptions import RequestException


# MODÈLES PYDANTIC (Rappel Jour 1)
class CurrentWeather(BaseModel):
    time: str
    temperature_2m: float
    wind_speed_10m: float

class WeatherResponseModel(BaseModel):
    latitude: float
    longitude: float
    current: CurrentWeather



# CLIENT API (Rappel Jour 1)

def fetch_weather_data(lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m"
    }
    with requests.Session() as session:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

# Utilisation d'un bloc 'with requests.Session()' pour optimiser les connexions HTTP
    try:
        with requests.Session() as session:
            # Timeout de 10 secondes pour éviter de bloquer 
            response = session.get(url, params=params, timeout=10)
            
            # Vérifie si le code de statut indique une erreur (4xx ou 5xx)
            response.raise_for_status()
            
            # Retourne les données sous forme de dictionnaire Python 
            return response.json()

    except requests.exceptions.Timeout:
        print(" Erreur : Le serveur Open-Meteo met trop de temps à répondre (Timeout).")
        raise
    except requests.exceptions.HTTPError as http_err:
        print(f" Erreur HTTP : {http_err} (Statut: {response.status_code})")
        raise
    except RequestException as err:
        print(f" Erreur réseau critique : {err}")
        raise


#  EXÉCUTION DU SCRIPT ( JOUR 1)

if __name__ == "__main__":
    # Coordonnées de Dunkerque (Latitude, Longitude)
    LATITUDE = 51.0344
    LONGITUDE = 2.3767

    print(f" Interrogation de l'API Open-Meteo pour les coordonnées ({LATITUDE}, {LONGITUDE})...")

    try:
        #  Récupération des données brutes
        raw_data = fetch_weather_data(LATITUDE, LONGITUDE)
        print(" Données brutes récupérées avec succès !")

        # Validation  via Pydantic
        # Si une clé manque ou si un type est incorrect,
        # Pydantic lève une exception 'ValidationError'.
        validated_weather = WeatherResponseModel(**raw_data)
        
        print("\n Données validées et structurées par Pydantic :")
        print(f"   - Latitude : {validated_weather.latitude}")
        print(f"   - Longitude : {validated_weather.longitude}")
        print(f"   - Heure du relevé : {validated_weather.current.time}")
        print(f"   - Température : {validated_weather.current.temperature_2m} °C")
        print(f"   - Vitesse du vent : {validated_weather.current.wind_speed_10m} km/h")

    except ValidationError as val_err:
        print(" Erreur de validation Pydantic : Les données reçues ne respectent pas le contrat attendu.")
        print(val_err)
    except Exception as e:
        print(f" Une erreur inattendue est survenue : {e}")


#  GESTION DE LA BASE DE DONNÉES SQLITE

DB_NAME = "meteo_observatoire.db"

def init_database():
    """Crée les tables SQLite si elles n'existent pas."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # Table des villes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS villes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT UNIQUE NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL
            )
        """)
        
        # Table des relevés météo liés à une ville
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS releves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ville_id INTEGER NOT NULL,
                temperature REAL NOT NULL,
                vitesse_vent REAL NOT NULL,
                date_heure TEXT NOT NULL,
                FOREIGN KEY (ville_id) REFERENCES villes (id)
            )
        """)
        conn.commit()
    print(" Base de données initialisée avec succès.")


def save_weather_to_db(nom_ville: str, lat: float, lon: float, weather_data: WeatherResponseModel):
    """Insère la ville (si besoin) et le relevé météo dans SQLite."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        #  Insertion ou récupération de l'ID de la ville (INSERT OR IGNORE + SELECT)
        cursor.execute("""
            INSERT OR IGNORE INTO villes (nom, latitude, longitude)
            VALUES (?, ?, ?)
        """, (nom_ville, lat, lon))
        
        cursor.execute("SELECT id FROM villes WHERE nom = ?", (nom_ville,))
        ville_id = cursor.fetchone()[0]
        
        #  Insertion du relevé météo validé par Pydantic
        cursor.execute("""
            INSERT INTO releves (ville_id, temperature, vitesse_vent, date_heure)
            VALUES (?, ?, ?, ?)
        """, (
            ville_id,
            weather_data.current.temperature_2m,
            weather_data.current.wind_speed_10m,
            weather_data.current.time
        ))
        
        conn.commit()
    print(f" Relevé de {nom_ville} enregistré en base de données.")


def get_recent_releves():
    """Lit et affiche les derniers relevés enregistrés en base."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.nom, r.temperature, r.vitesse_vent, r.date_heure
            FROM releves r
            JOIN villes v ON r.ville_id = v.id
            ORDER BY r.id DESC
            LIMIT 5
        """)
        return cursor.fetchall()



#  EXÉCUTION GLOBAL (JOUR 1 + JOUR 2)
# 
if __name__ == "__main__":
    # Initialisation de la base
    init_database()

    # Paramètres de test (Dunkerque)
    NOM_VILLE = "Dunkerque"
    LATITUDE = 51.0344
    LONGITUDE = 2.3767

    try:
        print(f"\n Récupération des données pour {NOM_VILLE}...")
        raw_data = fetch_weather_data(LATITUDE, LONGITUDE)
        
        # Validation Pydantic
        validated_weather = WeatherResponseModel(**raw_data)
        print(" Données validées par Pydantic.")

        # Stockage SQLite
        save_weather_to_db(NOM_VILLE, LATITUDE, LONGITUDE, validated_weather)

        # Lecture de contrôle
        print("\n Derniers relevés stockés en base :")
        historique = get_recent_releves()
        for row in historique:
            ville, temp, vent, heure = row
            print(f"   - [{heure}] {ville} : {temp} °C, Vent : {vent} km/h")

    except Exception as e:
        print(f" Une erreur est survenue : {e}")