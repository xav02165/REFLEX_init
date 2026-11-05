

import reflex as rx

config = rx.Config(
    app_name="Reflex_initiation",
    # On force l'activation du plugin de thème officiel Radix
    plugins=[
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="light",
                has_background=True,
                radius="large",
                accent_color="indigo", # Donne une couleur de base (boutons, liens...)
            )
        )
    ],
)
