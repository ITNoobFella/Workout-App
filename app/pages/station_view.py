"""Station-Tablet: /station/<nummer>"""
from nicegui import ui

import database_test as db          # später: import database as db
from config import BLAU, SCHWIERIGKEIT_FARBE
from pages import theme


@ui.page('/station/{nummer}')
def station_seite(nummer: int):
    theme.anwenden(dunkel=True)
    station = db.station_nach_nummer(nummer)
    zustand = {'uebung': None}

    def wuerfeln():
        zustand['uebung'] = db.zufaellige_uebung(station['id'])
        inhalt.refresh()

    @ui.refreshable
    def inhalt():
        if station is None:
            with ui.column().classes('w-full h-screen items-center justify-center'):
                ui.icon('portable_wifi_off', size='96px', color='grey')
                ui.label(f'Station {nummer} ist nicht eingerichtet').classes('text-3xl')
            return

        uebung = zustand['uebung']

        # Kopfzeile: Nummer + Stationsname
        with ui.row().classes('w-full items-center gap-4 px-6 pt-4'):
            ui.label(str(station['nummer'])).classes('text-4xl font-bold rounded-2xl px-5 py-2') \
                .style(f'background:{BLAU}')
            ui.label(station['name']).classes('text-3xl font-bold')

        # Mitte: links Videofläche, rechts Infos
        with ui.row().classes('w-full px-6 gap-6 no-wrap items-stretch').style('height: calc(100vh - 260px)'):
            with ui.element('div').classes('rounded-2xl flex items-center justify-center') \
                    .style('flex: 2; background: black'):
                ui.icon('play_circle', size='96px', color='grey')   # Platzhalter, Schritt 4: ui.video

            with ui.column().classes('gap-4').style('flex: 1'):
                if uebung is None:
                    ui.label('Drücke auf „Würfeln“').classes('text-2xl text-gray-400')
                else:
                    ui.label(uebung['name']).classes('text-5xl font-bold')
                    ui.label(uebung['schwierigkeit']).classes('text-xl font-bold rounded-xl px-4 py-1') \
                        .style(f'background:{SCHWIERIGKEIT_FARBE[uebung["schwierigkeit"]]}')
                    ui.label(f'{uebung["wiederholungen"]} Wiederholungen').classes('text-2xl')
                    ui.label(uebung['beschreibung']).classes('text-xl text-gray-300')

        # Unten: großer Würfel-Button
        with ui.row().classes('w-full justify-center pt-4'):
            ui.button('Würfeln', icon='casino', color='warning', on_click=wuerfeln) \
                .classes('text-3xl px-16 py-4')

    inhalt()