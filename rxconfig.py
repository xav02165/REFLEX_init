

import reflex as rx

config = rx.Config(
    app_name="Reflex_initiation",
    # Indique à Reflex d'utiliser votre fichier SQLite local nommé 'meteo.db'
    db_url="sqlite:///meteo_observatoire.db", 
    plugins=[
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="light",
                has_background=True,
                radius="large",
                accent_color="indigo",
            )
        )
    ],
)
