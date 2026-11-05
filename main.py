from fastapi import FastAPI, HTTPException
import sqlite3
from pydantic import BaseModel

# Initialisation de l'application FastAPI
app = FastAPI(
    title="L'Observatoire Météo API",
    description="API de restitution des relevés météorologiques stockés localement.",
    version="1.0.0"
)

DB_NAME = "meteo_observatoire.db"


# PYDANTIC 

class ReleveResponse(BaseModel):
    ville: str
    temperature: float
    vitesse_vent: float
    date_heure: str

    class Config:
        from_attributes = True



# ENDPOINTS DE L'API

@app.get("/", summary="Page d'accueil de l'Observatoire")
def root():
    return {"message": "Bienvenue sur l'API de L'Observatoire Météo ! Rendez-vous sur /docs pour explorer la documentation."}


@app.get("/meteo/{nom_ville}", response_model=list[ReleveResponse], summary="Récupérer les relevés d'une ville")
def get_meteo_by_ville(nom_ville: str):
    """
    Permet de récupérer l'historique des relevés météo enregistrés en base pour une ville donnée.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # Requête pour récupérer les relevés de la ville (insensible à la casse)
        cursor.execute("""
            SELECT v.nom, r.temperature, r.vitesse_vent, r.date_heure
            FROM releves r
            JOIN villes v ON r.ville_id = v.id
            WHERE v.nom COLLATE NOCASE = ?
            ORDER BY r.id DESC
        """, (nom_ville,))
        
        rows = cursor.fetchall()
        
        # Si la ville n'existe pas ou n'a aucun relevé, on renvoie une erreur HTTP 404 propre
        if not rows:
            raise HTTPException(
                status_code=404, 
                detail=f"Aucun relevé trouvé pour la ville : '{nom_ville}'."
            )
        
        # Transformation des résultats SQL en objets Pydantic 
        resultats = [
            ReleveResponse(
                ville=row[0],
                temperature=row[1],
                vitesse_vent=row[2],
                date_heure=row[3]
            )
            for row in rows
        ]
        
        return resultats