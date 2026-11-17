"""Lehrkraft-Ansicht: Stationen und Übungen verwalten (/master)"""
from nicegui import ui

import database_test as db          # später: import database as db
import sync
from config import BLAU, SCHWIERIGKEIT_FARBE, SCHWIERIGKEITEN
from pages import theme


@ui.page('/master')
def master_seite():
    theme.anwenden()
    zustand = {'version': sync.version()}

    def geaendert():
        """Nach jeder Änderung: Stationen informieren und eigene Ansicht neu zeichnen."""
        sync.aenderung_melden()
        zustand['version'] = sync.version()
        stationen_liste.refresh()
        uebungen_liste.refresh()

    # ------------------------------------------------------------ Kopfzeile + Tabs
    with ui.header().classes('items-center justify-between px-6 py-3 bg-secondary'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('fitness_center', size='32px', color='warning')
            ui.label('Workout Generator').classes('text-2xl font-bold')
            ui.label('Lehrkraft').classes('text-lg text-gray-400')

    with ui.tabs().classes('w-full bg-white') as tabs:
        tab_stationen = ui.tab('Stationen', icon='grid_view')
        tab_uebungen = ui.tab('Übungen', icon='sports_gymnastics')

    # ============================================================ STATIONEN
    @ui.refreshable
    def stationen_liste():
        stationen = db.alle_stationen()
        with ui.row().classes('w-full items-center gap-3 mb-4'):
            ui.button('Neue Station', icon='add', on_click=lambda: station_dialog(None))
            ui.button('Alle: Zufall an', icon='casino', color='warning',
                      on_click=lambda: alle_modus('zufall')).props('outline')
            ui.button('Alle: Fest', icon='lock', on_click=lambda: alle_modus('fest')).props('outline color=grey-8')
        if not stationen:
            ui.label('Noch keine Stationen. Lege die erste an!').classes('text-gray-500 text-lg')
        with ui.grid().classes('w-full gap-4').style('grid-template-columns: repeat(auto-fill, minmax(300px, 1fr))'):
            for s in stationen:
                station_karte(s)

    def station_karte(s):
        anzahl = len(db.station_uebungen(s['id']))
        aktuell = db.uebung_holen(s['aktuelle_uebung_id']) if s.get('aktuelle_uebung_id') else None
        with ui.card().classes('karte p-5 gap-3'):
            with ui.row().classes('items-center gap-3 no-wrap'):
                ui.label(str(s['nummer'])).classes('text-2xl font-bold text-white rounded-xl px-3 py-1') \
                    .style(f'background:{BLAU}')
                ui.label(s['name'] or 'Ohne Namen').classes('text-xl font-bold')

            with ui.row().classes('items-center gap-2'):
                ui.icon('play_circle', color='positive')
                ui.label(aktuell['name'] if aktuell else '- keine Übung -').classes('text-lg')

            ui.label(f'{anzahl} Übungen  ·  Timer {s["dauer_sekunden"]} s').classes('text-gray-500')
            ui.switch('Zufallsmodus', value=s['modus'] == 'zufall',
                      on_change=lambda e, sid=s['id']: modus_aendern(sid, e.value)).props('color=warning')
            with ui.row().classes('w-full gap-2'):
                ui.button('Bearbeiten', icon='edit', on_click=lambda st=s: station_dialog(st)).props('outline')
                ui.button(icon='open_in_new',
                          on_click=lambda nr=s['nummer']: ui.navigate.to(f'/station/{nr}', new_tab=True)) \
                    .props('outline color=grey-8').tooltip('Stationsansicht öffnen')

    def modus_aendern(station_id, zufall):
        db.modus_setzen(station_id, 'zufall' if zufall else 'fest')
        geaendert()

    def alle_modus(modus):
        for s in db.alle_stationen():
            db.modus_setzen(s['id'], modus)
        geaendert()
        ui.notify('Alle Stationen: ' + ('Zufallsmodus' if modus == 'zufall' else 'feste Übung'))

    def station_dialog(s):
        """Station anlegen (s=None) oder bearbeiten."""
        alle = {u['id']: u['name'] for u in db.alle_uebungen()}
        zugeordnet = [u['id'] for u in db.station_uebungen(s['id'])] if s else []
        naechste_nr = max([x['nummer'] for x in db.alle_stationen()], default=0) + 1

        with ui.dialog() as d, ui.card().classes('karte p-6 gap-3').style('min-width: 520px'):
            ui.label('Station bearbeiten' if s else 'Neue Station').classes('text-2xl font-bold')
            with ui.row().classes('w-full gap-3 no-wrap'):
                nummer = ui.number('Nummer', value=s['nummer'] if s else naechste_nr, min=1, format='%d') \
                    .props('outlined').classes('w-28')
                name = ui.input('Name / Körperteil', value=s['name'] if s else '') \
                    .props('outlined').classes('flex-grow')
            dauer = ui.number('Timer (Sekunden)', value=s['dauer_sekunden'] if s else 60,
                              min=5, step=5, format='%d').props('outlined')
            uebungen = ui.select(alle, multiple=True, value=zugeordnet, label='Übungen an dieser Station') \
                .props('outlined use-chips').classes('w-full')
            aktuell = ui.select(alle, value=s.get('aktuelle_uebung_id') if s else None, clearable=True,
                                label='Feste Übung (im Fest-Modus)').props('outlined').classes('w-full')

            def speichern():
                andere = [x for x in db.alle_stationen() if not s or x['id'] != s['id']]
                if any(x['nummer'] == int(nummer.value or 0) for x in andere):
                    ui.notify(f'Station {int(nummer.value)} gibt es schon', type='negative')
                    return
                station_id = db.station_speichern({
                    'nummer': int(nummer.value), 'name': name.value or '',
                    'dauer_sekunden': int(dauer.value or 60),
                    'aktuelle_uebung_id': aktuell.value,
                }, s['id'] if s else None)
                db.station_uebungen_setzen(station_id, uebungen.value or [])
                d.close()
                geaendert()
                ui.notify('Gespeichert', type='positive')

            def loeschen():
                db.station_loeschen(s['id'])
                d.close()
                geaendert()

            with ui.row().classes('w-full justify-between mt-2'):
                if s:
                    ui.button('Löschen', icon='delete', color='negative', on_click=loeschen).props('flat')
                else:
                    ui.element()
                with ui.row():
                    ui.button('Abbrechen', on_click=d.close).props('flat')
                    ui.button('Speichern', icon='save', color='positive', on_click=speichern)
        d.open()

    # ============================================================ ÜBUNGEN
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
                geaendert()
                ui.notify('Gespeichert', type='positive')

            with ui.row().classes('w-full justify-end'):
                ui.button('Abbrechen', on_click=d.close).props('flat')
                ui.button('Speichern', icon='save', color='positive', on_click=speichern)
        d.open()

    def loeschen_dialog(u):
        with ui.dialog() as d, ui.card().classes('karte'):
            ui.label(f'„{u["name"]}“ wirklich löschen?').classes('text-lg')

            def bestaetigen():
                db.uebung_loeschen(u['id'])
                d.close()
                geaendert()

            with ui.row().classes('w-full justify-end'):
                ui.button('Abbrechen', on_click=d.close).props('flat')
                ui.button('Löschen', icon='delete', color='negative', on_click=bestaetigen)
        d.open()

    # ============================================================ Tabs
    with ui.tab_panels(tabs, value=tab_stationen).classes('w-full bg-transparent'):
        with ui.tab_panel(tab_stationen):
            stationen_liste()
        with ui.tab_panel(tab_uebungen):
            with ui.column().classes('w-full max-w-3xl mx-auto gap-4'):
                ui.button('Neue Übung', icon='add', on_click=lambda: uebung_dialog(None))
                uebungen_liste()

    # Änderungen der Stationen (z. B. Schüler würfelt) übernehmen
    def pruefen():
        if sync.version() != zustand['version']:
            zustand['version'] = sync.version()
            stationen_liste.refresh()

    ui.timer(1.0, pruefen)