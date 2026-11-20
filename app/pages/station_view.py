"""Station-Tablet: /station/<nummer>"""
import asyncio
import random

from nicegui import ui

import database_test as db          # später: import database as db
import sync
from config import BLAU, DUNKELBLAU, GRUEN, ORANGE, VIDEO_ORDNER
from pages import theme


@ui.page('/station/{nummer}')
def station_seite(nummer: int):
    theme.anwenden(dunkel=True)
    start = db.station_nach_nummer(nummer)
    dauer0 = start['dauer_sekunden'] if start else 60
    timer = {'rest': dauer0, 'laeuft': False, 'dauer': dauer0}
    zustand = {'version': -1, 'fingerabdruck': None}

    # ============================================================ 1. Timer
    def tick():                                   # jede Sekunde
        if timer['laeuft'] and timer['rest'] > 0:
            timer['rest'] -= 1
            if timer['rest'] == 0:
                timer['laeuft'] = False
                timer_steuerung.refresh()
                ui.notify('Zeit abgelaufen!', type='warning')

    def start_pause():
        timer['laeuft'] = not timer['laeuft']
        timer_steuerung.refresh()                 # Symbol Play <-> Pause

    def zuruecksetzen():
        timer['laeuft'] = False
        timer['rest'] = timer['dauer']

    def zuruecksetzen_klick():
        zuruecksetzen()
        timer_steuerung.refresh()

    ui.timer(1.0, tick)

    def uhrzeit(sekunden):
        return f'{sekunden // 60:02d}:{sekunden % 60:02d}'

    @ui.refreshable
    def timer_steuerung():
        with ui.row().classes('gap-3 mt-4'):
            ui.button(icon='pause' if timer['laeuft'] else 'play_arrow', on_click=start_pause) \
                .props('round size=40px')
            ui.button(icon='restart_alt', on_click=zuruecksetzen_klick).props('round outline size=40px')

    # ============================================================ 2. Übung wählen
    async def wuerfeln():
        station = db.station_nach_nummer(nummer)
        uebungen = db.station_uebungen(station['id'])
        if not uebungen:
            ui.notify('Dieser Station sind noch keine Übungen zugeordnet', type='warning')
            return
        # kleine "Glücksrad"-Animation
        with ui.dialog().props('persistent') as d, ui.card().classes('karte p-10 items-center') \
                .style(f'background:{DUNKELBLAU}; min-width: 500px'):
            ui.icon('casino', size='64px', color='warning')
            name = ui.label().classes('text-4xl font-bold text-white')
        d.open()
        for i in range(14):
            name.text = random.choice(uebungen)['name']
            await asyncio.sleep(0.05 + i * 0.012)
        gewaehlt = db.zufaellige_uebung(station['id'])
        name.text = gewaehlt['name']
        name.style(f'color:{GRUEN}')
        await asyncio.sleep(0.8)
        d.close()
        zuruecksetzen()
        neu_zeichnen()

    def liste_zeigen():
        station = db.station_nach_nummer(nummer)
        with ui.dialog() as d, ui.card().classes('karte p-6').style(f'background:{DUNKELBLAU}; min-width: 500px'):
            ui.label('Übungen dieser Station').classes('text-2xl font-bold text-white')

            def auswaehlen(uebung_id):
                db.aktuelle_uebung_setzen(station['id'], uebung_id)
                zuruecksetzen()
                d.close()
                neu_zeichnen()

            for u in db.station_uebungen(station['id']):
                ui.button(u['name'], on_click=lambda uid=u['id']: auswaehlen(uid)) \
                    .classes('w-full text-xl') \
                    .props('outline' if u['id'] != station.get('aktuelle_uebung_id') else '')
        d.open()

    # ============================================================ 3. Synchronisation
    def fingerabdruck(station):
        """Alles, was die Anzeige beeinflusst. Ändert es sich, wird neu gezeichnet."""
        if station is None:
            return None
        ids = tuple(u['id'] for u in db.station_uebungen(station['id']))
        uebung = db.uebung_holen(station['aktuelle_uebung_id']) if station.get('aktuelle_uebung_id') else None
        return (station['name'], station['modus'], station['dauer_sekunden'], ids,
                tuple(uebung.items()) if uebung else None)

    def neu_zeichnen():
        """Nach eigener Änderung: andere informieren und selbst neu zeichnen."""
        sync.aenderung_melden()
        zustand['version'] = sync.version()
        zustand['fingerabdruck'] = fingerabdruck(db.station_nach_nummer(nummer))
        inhalt.refresh()

    def pruefen():
        sync.station_meldet_sich(nummer)
        if sync.version() == zustand['version']:
            return
        zustand['version'] = sync.version()
        station = db.station_nach_nummer(nummer)
        neu = fingerabdruck(station)
        if neu != zustand['fingerabdruck']:
            zustand['fingerabdruck'] = neu
            if station and station['dauer_sekunden'] != timer['dauer']:
                timer['dauer'] = station['dauer_sekunden']      # Lehrkraft hat die Dauer geändert
                zuruecksetzen()
            inhalt.refresh()

    # ============================================================ 4. Anzeige
    @ui.refreshable
    def inhalt():
        station = db.station_nach_nummer(nummer)
        if station is None:
            with ui.column().classes('w-full h-screen items-center justify-center'):
                ui.icon('portable_wifi_off', size='96px', color='grey')
                ui.label(f'Station {nummer} ist nicht eingerichtet').classes('text-3xl')
                ui.label('Die Lehrkraft kann sie im Master anlegen.').classes('text-gray-400')
            return

        uebung = db.uebung_holen(station['aktuelle_uebung_id']) if station.get('aktuelle_uebung_id') else None

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
                    ui.video(f'/videos/{uebung["video"]}', controls=True, autoplay=False, loop=False) \
                        .props('playsinline').classes('w-full h-full').style('object-fit: contain')
                else:
                    with ui.column().classes('items-center text-gray-500'):
                        ui.icon('videocam_off', size='80px')
                        ui.label('Kein Video vorhanden' if uebung else 'Noch keine Übung ausgewählt') \
                            .classes('text-xl')

            with ui.column().classes('gap-6 no-wrap').style('flex: 1; min-height: 0'):
                with ui.card().classes('karte w-full items-center justify-center') \
                        .style(f'flex: 1; background:#1E293B; border: 2px solid {BLAU}'):
                    ui.label().classes('font-bold').style('font-size: 96px; line-height: 1') \
                        .bind_text_from(timer, 'rest', backward=uhrzeit)
                    timer_steuerung()

                with ui.card().classes('karte w-full items-center justify-center') \
                        .style(f'flex: 1; background:#1E293B; border: 2px solid {GRUEN}'):
                    if uebung is None:
                        ui.label('-').classes('font-bold').style('font-size: 120px; line-height: 1')
                    else:
                        ui.label(str(uebung['wiederholungen'])).classes('font-bold') \
                            .style(f'font-size: 120px; line-height: 1; color:{ORANGE}')
                    ui.label('Wiederholungen').classes('text-2xl text-gray-300')

        # Untere Leiste: Zufall = Würfeln + Liste, Fest = Hinweis
        with ui.row().classes('w-full px-6 py-4 gap-4 justify-center'):
            if station['modus'] == 'zufall':
                ui.button('Übung würfeln', icon='casino', color='warning', on_click=wuerfeln) \
                    .classes('text-2xl font-bold px-10').style('min-height: 80px; color: white')
                ui.button('Liste', icon='list', on_click=liste_zeigen) \
                    .classes('text-2xl px-8').style('min-height: 80px')
            else:
                with ui.row().classes('items-center gap-2 text-gray-400 text-xl').style('min-height: 80px'):
                    ui.icon('lock')
                    ui.label('Übung von der Lehrkraft festgelegt')

    zustand['fingerabdruck'] = fingerabdruck(db.station_nach_nummer(nummer))
    zustand['version'] = sync.version()
    inhalt()
    ui.timer(0.5, pruefen)