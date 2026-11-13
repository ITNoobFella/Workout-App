"""Lehrkraft-Ansicht: Übungen verwalten (/master)"""
from nicegui import ui

import database_test as db          # später: import database as db
from config import SCHWIERIGKEIT_FARBE, SCHWIERIGKEITEN
from pages import theme


@ui.page('/master')
def master_seite():
    theme.anwenden()

    # ------------------------------------------------------ Liste
    @ui.refreshable
    def uebungen_liste():
        uebungen = db.alle_uebungen()
        if not uebungen:
            ui.label('Noch keine Übungen angelegt.').classes('text-gray-500')
        for u in uebungen:
            with ui.card().classes('karte w-full'):
                with ui.row().classes('w-full items-center justify-between no-wrap'):
                    with ui.column().classes('gap-0'):
                        ui.label(u['name']).classes('text-xl font-bold')
                        ui.label(f'{u["wiederholungen"]} Wiederholungen  -  {u["beschreibung"]}') \
                            .classes('text-gray-500')
                    with ui.row().classes('items-center gap-2 no-wrap'):
                        ui.label(u['schwierigkeit']).classes('text-white font-bold rounded-xl px-3 py-1') \
                            .style(f'background:{SCHWIERIGKEIT_FARBE[u["schwierigkeit"]]}')
                        ui.button(icon='edit', on_click=lambda u=u: uebung_dialog(u)).props('flat round')
                        ui.button(icon='delete', color='negative',
                                  on_click=lambda u=u: loeschen_dialog(u)).props('flat round')

    # ------------------------------------------------------ Dialog: anlegen / bearbeiten
    def uebung_dialog(u=None):
        with ui.dialog() as d, ui.card().classes('karte w-96'):
            ui.label('Übung bearbeiten' if u else 'Neue Übung').classes('text-xl font-bold')
            name = ui.input('Name', value=u['name'] if u else '').props('outlined').classes('w-full')
            beschreibung = ui.textarea('Beschreibung', value=u['beschreibung'] if u else '') \
                .props('outlined').classes('w-full')
            schwierigkeit = ui.select(SCHWIERIGKEITEN, label='Schwierigkeit',
                                      value=u['schwierigkeit'] if u else 'mittel') \
                .props('outlined').classes('w-full')
            wdh = ui.number('Wiederholungen', value=u['wiederholungen'] if u else 10,
                            min=1, step=1, format='%d').props('outlined').classes('w-full')

            def speichern():
                if not name.value or not name.value.strip():
                    ui.notify('Bitte einen Namen eingeben', type='negative')
                    return
                db.uebung_speichern({
                    'name': name.value.strip(),
                    'beschreibung': beschreibung.value or '',
                    'schwierigkeit': schwierigkeit.value,
                    'wiederholungen': int(wdh.value or 1),
                }, u['id'] if u else None)
                d.close()
                uebungen_liste.refresh()
                ui.notify('Gespeichert', type='positive')

            with ui.row().classes('w-full justify-end'):
                ui.button('Abbrechen', on_click=d.close).props('flat')
                ui.button('Speichern', icon='save', color='positive', on_click=speichern)
        d.open()

    # ------------------------------------------------------ Dialog: löschen
    def loeschen_dialog(u):
        with ui.dialog() as d, ui.card().classes('karte'):
            ui.label(f'„{u["name"]}“ wirklich löschen?').classes('text-lg')

            def bestaetigen():
                db.uebung_loeschen(u['id'])
                d.close()
                uebungen_liste.refresh()

            with ui.row().classes('w-full justify-end'):
                ui.button('Abbrechen', on_click=d.close).props('flat')
                ui.button('Löschen', icon='delete', color='negative', on_click=bestaetigen)
        d.open()

    # ------------------------------------------------------ Seite
    with ui.column().classes('w-full max-w-3xl mx-auto p-6 gap-4'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('Übungen verwalten').classes('text-3xl font-bold')
            ui.button('Neue Übung', icon='add', on_click=lambda: uebung_dialog(None))
        uebungen_liste()