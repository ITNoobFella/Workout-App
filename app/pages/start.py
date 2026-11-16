"""Startseite: Auswahl zwischen Lehrkraft (Master) und Station-Tablet."""
import socket

from nicegui import app, ui

import database_test as db          # später: import database as db
from config import DUNKELBLAU, MASTER_PIN, PORT
from pages import theme


def lokale_ip():
    """IP-Adresse dieses Rechners im WLAN (für die iPads)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return 'localhost'


@ui.page('/')
def startseite():
    theme.anwenden(dunkel=True)

    with ui.column().classes('w-full items-center gap-8 p-10'):
        ui.icon('fitness_center', size='72px', color='warning')
        ui.label('Workout Generator').classes('text-5xl font-bold')
        ui.label('Zirkeltraining - Industrieschule Chemnitz').classes('text-xl text-gray-400')

        with ui.row().classes('gap-8 mt-6 justify-center'):
            # Karte 1: Lehrkraft (Master)
            with ui.card().classes('karte w-80 items-center p-8 cursor-pointer') \
                    .style(f'background:{DUNKELBLAU}; border: 2px solid #3B82F6') \
                    .on('click', lambda: pin_dialog.open()):
                ui.icon('school', size='64px', color='primary')
                ui.label('Master-Tablet').classes('text-2xl font-bold text-white')
                ui.label('Übungen & Stationen verwalten').classes('text-gray-400 text-center')

            # Karte 2: Station-Tablet
            with ui.card().classes('karte w-80 items-center p-8 cursor-pointer') \
                    .style(f'background:{DUNKELBLAU}; border: 2px solid #10B981') \
                    .on('click', lambda: station_dialog.open()):
                ui.icon('tablet_mac', size='64px', color='positive')
                ui.label('Station-Tablet').classes('text-2xl font-bold text-white')
                ui.label('Dieses iPad als Station verwenden').classes('text-gray-400 text-center')

        ui.label(f'Adresse für die iPads:  http://{lokale_ip()}:{PORT}').classes('text-gray-500 mt-8')

    # --- PIN-Abfrage für die Lehrkraft
    with ui.dialog() as pin_dialog, ui.card().classes('karte p-6 items-center'):
        ui.label('PIN eingeben').classes('text-xl font-bold')
        pin = ui.input(password=True).props('outlined autofocus inputmode=numeric').classes('w-48 text-2xl')

        def pruefen():
            if pin.value == MASTER_PIN:
                app.storage.user['ist_lehrkraft'] = True
                ui.navigate.to('/master')
            else:
                ui.notify('Falsche PIN', type='negative')
                pin.value = ''
        pin.on('keydown.enter', pruefen)
        ui.button('Anmelden', on_click=pruefen).classes('w-48')

    # --- Auswahl der Stationsnummer
    with ui.dialog() as station_dialog, ui.card().classes('karte p-6 items-center'):
        ui.label('Welche Station ist dieses iPad?').classes('text-xl font-bold')
        stationen = db.alle_stationen()
        if not stationen:
            ui.label('Noch keine Stationen angelegt.')
        with ui.grid(columns=4).classes('gap-4'):
            for s in stationen:
                ui.button(str(s['nummer']), color='positive',
                          on_click=lambda nr=s['nummer']: ui.navigate.to(f'/station/{nr}')) \
                    .classes('w-20 h-20 text-3xl font-bold')