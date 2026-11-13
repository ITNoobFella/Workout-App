"""Station-Tablet: /station/<nummer>"""
from nicegui import ui

import database_test as db          # später: import database as db
from config import BLAU, SCHWIERIGKEIT_FARBE, VIDEO_ORDNER
from pages import theme


@ui.page('/station/{nummer}')
def station_seite(nummer: int):
    theme.anwenden(dunkel=True)
    station = db.station_nach_nummer(nummer)
    dauer = station['dauer_sekunden'] if station else 60 
    zustand = {'uebung': None}
    timer = {'rest': dauer, 'laeuft': False}

    # ---------------------------------------------------------- Timer
    def tick():                                   # wird jede Sekunde aufgerufen
        if timer['laeuft'] and timer['rest'] > 0:
            timer['rest'] -= 1
            if timer['rest'] == 0:
                timer['laeuft'] = False
                ui.notify('Zeit abgelaufen!', type='warning')

    def start_pause():
        timer['laeuft'] = not timer['laeuft']

    def zuruecksetzen():
        timer['laeuft'] = False
        timer['rest'] = dauer

    ui.timer(1.0, tick)

    def uhrzeit(sekunden):
        return f'{sekunden // 60:02d}:{sekunden % 60:02d}'

    # ---------------------------------------------------------- Würfeln
    def wuerfeln():
        zustand['uebung'] = db.zufaellige_uebung(station['id'])
        zuruecksetzen()
        inhalt.refresh()

    # ---------------------------------------------------------- Anzeige
    @ui.refreshable
    def inhalt():
        if station is None:
            with ui.column().classes('w-full h-screen items-center justify-center'):
                ui.icon('portable_wifi_off', size='96px', color='grey')
                ui.label(f'Station {nummer} ist nicht eingerichtet').classes('text-3xl')
            return

        uebung = zustand['uebung']

        # Kopfzeile: Nummer, Name und Timer
        with ui.row().classes('w-full items-center justify-between px-6 pt-4'):
            with ui.row().classes('items-center gap-4'):
                ui.label(str(station['nummer'])).classes('text-4xl font-bold rounded-2xl px-5 py-2') \
                    .style(f'background:{BLAU}')
                ui.label(station['name']).classes('text-3xl font-bold')
            with ui.row().classes('items-center gap-3'):
                ui.label().classes('text-5xl font-bold') \
                    .bind_text_from(timer, 'rest', backward=uhrzeit)
                ui.button(icon='play_arrow', on_click=start_pause).props('round')
                ui.button(icon='restart_alt', on_click=zuruecksetzen).props('round outline')

        # Mitte: Video links, Infos rechts
        with ui.row().classes('w-full px-6 gap-6 no-wrap items-stretch').style('height: calc(100vh - 260px)'):
            with ui.element('div').classes('rounded-2xl overflow-hidden flex items-center justify-center') \
                    .style('flex: 2; background: black'):
                if uebung and uebung.get('video') and (VIDEO_ORDNER / uebung['video']).exists():
                    ui.video(f'/videos/{uebung["video"]}', autoplay=True, muted=True, loop=True) \
                        .classes('w-full h-full')
                else:
                    ui.icon('play_circle', size='96px', color='grey')

            with ui.column().classes('gap-4').style('flex: 1'):
                if uebung is None:
                    ui.label('Drücke auf „Würfeln“').classes('text-2xl text-gray-400')
                else:
                    ui.label(uebung['name']).classes('text-5xl font-bold')
                    ui.label(uebung['schwierigkeit']).classes('text-xl font-bold rounded-xl px-4 py-1') \
                        .style(f'background:{SCHWIERIGKEIT_FARBE[uebung["schwierigkeit"]]}')
                    ui.label(f'{uebung["wiederholungen"]} Wiederholungen').classes('text-2xl')
                    ui.label(uebung['beschreibung']).classes('text-xl text-gray-300')

        # Unten: Würfel-Button
        with ui.row().classes('w-full justify-center pt-4'):
            ui.button('Würfeln', icon='casino', color='warning', on_click=wuerfeln) \
                .classes('text-3xl px-16 py-4')

    inhalt()