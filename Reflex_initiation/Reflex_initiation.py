import reflex as rx
import random

# =====================================================================
# 1. ÉTAT DE L'APPLICATION (Logique métier)
# =====================================================================
class DataState(rx.State):
    # Données brutes simulées (ex: Ventes par mois pour deux catégories)
    full_data: list[dict] = [
        {"mois": "Jan", "Électronique": 4000, "Mode": 2400},
        {"mois": "Fév", "Électronique": 3000, "Mode": 1398},
        {"mois": "Mar", "Électronique": 2000, "Mode": 9800},
        {"mois": "Avr", "Électronique": 2780, "Mode": 3908},
        {"mois": "Mai", "Électronique": 1890, "Mode": 4800},
        {"mois": "Juin", "Électronique": 2390, "Mode": 3800},
    ]
    
    # Filtre sélectionné par l'utilisateur
    selected_category: str = "Toutes"
    
    # Fonction pour modifier le filtre
    def set_category(self, value: str):
        self.selected_category = value

    # Propriété calculée (Computed Var) : se met à jour automatiquement
    @rx.var
    def total_ventes(self) -> str:
        total = 0
        for item in self.full_data:
            if self.selected_category == "Électronique":
                total += item["Électronique"]
            elif self.selected_category == "Mode":
                total += item["Mode"]
            else:
                total += item["Électronique"] + item["Mode"]
        return f"{total:,} €"

    
 #=====================================================================
# ÉTAPE B : AJOUTER LE COMPOSANT KPI ICI (Il manquait probablement)
# =====================================================================
def kpi_card(title: str, value: str, change: str, is_positive: bool) -> rx.Component:
    badge_color = "green" if is_positive else "red"
    badge_icon = "trending-up" if is_positive else "trending-down"
    
    return rx.card(
        rx.vstack(
            rx.text(title, size="2", color_scheme="gray"),
            rx.hstack(
                rx.text(value, size="6", weight="bold"),
                rx.badge(
                    rx.icon(badge_icon, size=14),
                    change,
                    color_scheme=badge_color,
                    variant="soft",
                ),
                align="center",
                spacing="2",
            ),
            align="start",
            spacing="1",
        ),
        width="100%",
    )

# =====================================================================
# ÉTAPE C : L'interface principale (qui appelle kpi_card)
# =====================================================================
def index() -> rx.Component:
    return rx.vstack
# =====================================================================
# 2. INTERFACE UTILISATEUR
# =====================================================================
def index() -> rx.Component:
    return rx.vstack(
        # Barre supérieure / Header
        rx.hstack(
            rx.vstack(
                rx.heading("Dashboard Commercial", size="6"),
                rx.text("Suivi des performances mensuelles", color_scheme="gray"),
            ),
            # Menu déroulant pour filtrer
            rx.select(
                ["Toutes", "Électronique", "Mode"],
                value=DataState.selected_category,
                on_change=DataState.set_category,
                width="200px",
            ),
            justify="between",
            align="center",
            width="100%",
            border_bottom="1px solid #E5E7EB",
            padding_bottom="4",
        ),

        # Section des KPIs
        rx.grid(
            kpi_card("Chiffre d'Affaires Global", DataState.total_ventes, "+12.4%", True),
            kpi_card("Objectif Annuel", "65%", "-2.1%", False),
            kpi_card("Clients Actifs", "1,248", "+8.3%", True),
            columns="3",
            spacing="4",
            width="100%",
        ),

        # Section du Graphique principal
        rx.card(
            rx.vstack(
                rx.text("Évolution des ventes par segment", size="3", weight="medium"),
                rx.recharts.line_chart(
                    # Ligne 1 : Électronique (masquée si le filtre est sur 'Mode')
                    rx.cond(
                        DataState.selected_category != "Mode",
                        rx.recharts.line(data_key="Électronique", stroke="#3B82F6", stroke_width=2),
                    ),
                    # Ligne 2 : Mode (masquée si le filtre est sur 'Électronique')
                    rx.cond(
                        DataState.selected_category != "Électronique",
                        rx.recharts.line(data_key="Mode", stroke="#10B981", stroke_width=2),
                    ),
                    rx.recharts.x_axis(data_key="mois"),
                    rx.recharts.y_axis(),
                    rx.recharts.graphing_tooltip(),
                    data=DataState.full_data,
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
        max_width="1200px",
    )

# Config de l'application
app = rx.App()
app.add_page(index)
