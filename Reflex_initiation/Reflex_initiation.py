import reflex as rx
from typing import List, Dict, Any
import sqlmodel

# =====================================================================
# 1. MODÈLES DE LA BASE DE DONNÉES (Réf: Votre schéma SQLite)
# =====================================================================

class Villes(rx.Model, table=True):
    """Modèle pour la table 'villes'"""
    id: int = sqlmodel.Field(default=None, primary_key=True)
    nom: str = sqlmodel.Field(index=True, unique=True, nullable=False)
    latitude: float
    longitude: float

class Releves(rx.Model, table=True):
    """Modèle pour la table 'releves'"""
    id: int = sqlmodel.Field(default=None, primary_key=True)
    ville_id: int = sqlmodel.Field(foreign_key="villes.id", nullable=False)
    temperature: float
    vitesse_vent: float
    date_heure: str

# =====================================================================
# 2. ÉTAT DE L'APPLICATION (Logique de chargement)
# =====================================================================

class DataState(rx.State):
    # Liste pour stocker les relevés formatés pour Recharts
    chart_data: List[Dict[str, Any]] = []
    
    # KPIs calculés
    avg_temp: str = "N/A"
    max_vent: str = "N/A"

    def charger_donnees(self):
        """Récupère les données de SQLite et les prépare pour la Dataviz"""
        with rx.session() as session:
            # 1. Récupérer l'ID de Dunkerque
            ville = session.exec(
                sqlmodel.select(Villes).where(Villes.nom == "Dunkerque")
            ).first()
            
            if not ville:
                self.chart_data = []
                return

            # 2. Récupérer les relevés associés à cette ville ordonnés par date
            releves = session.exec(
                sqlmodel.select(Releves)
                .where(Releves.ville_id == ville.id)
                .order_by(Releves.date_heure)
            ).all()

            # 3. Formater les données pour Recharts (inverser l'ordre si besoin)
            formatted = []
            tot_temp = 0.0
            max_w = 0.0

            for r in reversed(releves): # Du plus ancien au plus récent
                # On nettoie la date pour l'affichage (ex: "2026-11-05T12:00" -> "05/11 12:00")
                date_propre = r.date_heure.replace("2026-", "").replace("T", " ")
                
                formatted.append({
                    "date": date_propre,
                    "Température (°C)": round(r.temperature, 1),
                    "Vent (km/h)": round(r.vitesse_vent, 1)
                })
                tot_temp += r.temperature
                if r.vitesse_vent > max_w:
                    max_w = r.vitesse_vent

            self.chart_data = formatted
            
            # Calcul des KPIs globaux
            if releves:
                self.avg_temp = f"{round(tot_temp / len(releves), 1)} °C"
                self.max_vent = f"{round(max_w, 1)} km/h"


# =====================================================================
# 3. INTERFACE COMPOSANTS & DASHBOARD
# =====================================================================

def kpi_card(title: str, value: str, icon_name: str, color: str) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(title, size="2", color_scheme="gray"),
                rx.text(value, size="6", weight="bold"),
                align="start",
                spacing="1",
            ),
            rx.icon(icon_name, size=28, color=color),
            justify="between",
            align="center",
            width="100%",
        ),
        width="100%",
    )

def index() -> rx.Component:
    return rx.vstack(
        # Header
        rx.hstack(
            rx.vstack(
                rx.heading("Suivi Météo Réel", size="6"),
                rx.text("Station : Dunkerque", color_scheme="gray", weight="medium"),
            ),
            # Bouton pour charger/rafraîchir les données depuis SQLite
            rx.button(
                "Charger les relevés", 
                on_click=DataState.charger_donnees,
                color_scheme="indigo",
                icon="refresh-cw"
            ),
            justify="between",
            align="center",
            width="100%",
            border_bottom="1px solid #E5E7EB",
            padding_bottom="4",
        ),

        # KPIs Cards
        rx.grid(
            kpi_card("Température Moyenne", DataState.avg_temp, "thermometer", "orange"),
            kpi_card("Rafale de Vent Max", DataState.max_vent, "wind", "blue"),
            columns="2",
            spacing="4",
            width="100%",
        ),

        # Graphique Mixte (Lignes)
        rx.card(
            rx.vstack(
                rx.text("Évolution Température vs Vitesse du vent", size="3", weight="medium"),
                rx.recharts.line_chart(
                    rx.recharts.line(data_key="Température (°C)", stroke="#F97316", stroke_width=2),
                    rx.recharts.line(data_key="Vent (km/h)", stroke="#3B82F6", stroke_width=2),
                    rx.recharts.x_axis(data_key="date"),
                    rx.recharts.y_axis(),
                    rx.recharts.graphing_tooltip(),
                    data=DataState.chart_data,
                    width="100%",
                    height=350,
                ),
                width="100%",
            ),
            width="100%",
            margin_top="4",
        ),
        
        padding="6",
        spacing="5",
        width="100%",
        max_width="1000px",
    )

app = rx.App()
app.add_page(index)

