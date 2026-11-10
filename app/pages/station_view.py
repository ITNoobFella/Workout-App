import random

from nicegui import ui

from pages import theme

UEBUNGEN = [   # Testdaten statt db.station_uebungen(...)
    {'name': 'Liegestütze', 'beschreibung': 'Rücken gerade halten'},
    {'name': 'Plank', 'beschreibung': 'Körper bildet eine Linie'},
    {'name': 'Kniebeugen', 'beschreibung': 'Knie nicht über die Zehen'},
]


@ui.page('/station/{nummer}')
def station_seite(nummer: int):
    theme.anwenden(dunkel=True)
    zustand = {'uebung': UEBUNGEN[0]}

    @ui.refreshable
    def inhalt():
        with ui.column().classes('w-full items-center gap-6 p-10'):
            ui.label(f'Station {nummer}').classes('text-4xl font-bold')
            ui.label(zustand['uebung']['name']).classes('text-6xl font-bold')
            ui.label(zustand['uebung']['beschreibung']).classes('text-xl text-gray-400')
            ui.button('Würfeln', icon='casino', color='warning', on_click=wuerfeln) \
                .classes('text-2xl px-10')

    def wuerfeln():
        zustand['uebung'] = random.choice(UEBUNGEN)   # später: db.zufaellige_uebung(...)
        inhalt.refresh()

    inhalt()