"""Station-Tablet: /station/<nummer>"""
from nicegui import ui

import database_test as db          # später: import database as db
from config import BLAU, DUNKELBLAU, GRUEN, ORANGE, VIDEO_ORDNER
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

        # Kopfzeile: Station, Körperteil | Titel der Übung
        with ui.row().classes('w-full items-center gap-4 px-6 pt-4 no-wrap'):
            ui.label(str(station['nummer'])).classes('text-4xl font-bold rounded-2xl px-5 py-2') \
                .style(f'background:{BLAU}')
            ui.label(station['name']).classes('text-3xl text-gray-300')
            ui.label('|').classes('text-3xl text-gray-500')
            ui.label(uebung['name'] if uebung else 'Bereit?').classes('text-4xl font-bold')

        # Mitte: Video links, rechts Timer (oben) und Wiederholungen (unten)
        with ui.row().classes('w-full px-6 gap-6 no-wrap items-stretch').style('height: calc(100vh - 260px)'):
            with ui.element('div').classes('rounded-2xl overflow-hidden flex items-center justify-center') \
                    .style('flex: 2; background: black'):
                if uebung and uebung.get('video') and (VIDEO_ORDNER / uebung['video']).exists():
                    ui.video(f'/videos/{uebung["video"]}', autoplay=True, muted=False, loop=False) \
                        .classes('w-full h-full')
                else:
                    ui.icon('play_circle', size='96px', color='grey')

            with ui.column().classes('gap-6 no-wrap').style('flex: 1; min-height: 0'):
                # obere Hälfte: Timer
                with ui.card().classes('karte w-full items-center justify-center') \
                        .style(f'flex: 1; background:#1E293B; border: 2px solid {BLAU}'):
                    ui.label().classes('font-bold').style('font-size: 96px; line-height: 1') \
                        .bind_text_from(timer, 'rest', backward=uhrzeit)
                    with ui.row().classes('gap-3 mt-4'):
                        ui.button(icon='play_arrow', on_click=start_pause).props('round size=xl')
                        ui.button(icon='restart_alt', on_click=zuruecksetzen).props('round outline size=xl')

                # untere Hälfte: Wiederholungen
                with ui.card().classes('karte w-full items-center justify-center') \
                        .style(f'flex: 1; background:#1E293B; border: 2px solid {GRUEN}'):
                    if uebung is None:
                        ui.label('-').classes('font-bold').style('font-size: 120px; line-height: 1')
                    else:
                        ui.label(str(uebung['wiederholungen'])).classes('font-bold') \
                            .style(f'font-size: 120px; line-height: 1; color:{ORANGE}')
                    ui.label('Wiederholungen').classes('text-2xl text-gray-300')

        # Unten: Würfel-Button
        with ui.row().classes('w-full justify-center pt-4'):
            ui.button('Würfeln', icon='casino', color='warning', on_click=wuerfeln) \
                .classes('text-3xl px-16 py-4')

    inhalt()