"""Master-Ansicht für die Lehrkraft: /master

Tab "Stationen": Übersicht aller Stationen, Zufallsmodus ein/aus, Übungen zuordnen
Tab "Übungen":   Übungen anlegen, bearbeiten, löschen, MP4-Video hochladen
"""
import uuid

from nicegui import app, ui

from config import BLAU, GRUEN, SCHWIERIGKEIT_FARBE, SCHWIERIGKEITEN, VIDEO_ORDNER
from pages import theme


@ui.page('/master')
def master_seite():
    if not app.storage.user.get('ist_lehrkraft'):
        ui.navigate.to('/')
        return
    theme.anwenden()
    zustand = {'version': sync.version()}
    online_punkte = {}          # Stationsnummer -> Icon (grün = verbunden)

    def abmelden():
        app.storage.user['ist_lehrkraft'] = False
        ui.navigate.to('/')

    # ------------------------------------------------------------ Kopfzeile
    with ui.header().classes('items-center justify-between px-6 py-3 bg-secondary'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('fitness_center', size='32px', color='warning')
            ui.label('Workout Generator').classes('text-2xl font-bold')
            ui.label('Lehrkraft').classes('text-lg text-gray-400')
        ui.button('Abmelden', icon='logout', on_click=abmelden).props('flat color=white')

    with ui.tabs().classes('w-full bg-white') as tabs:
        tab_stationen = ui.tab('Stationen', icon='grid_view')
        tab_uebungen = ui.tab('Übungen', icon='sports_gymnastics')

    dialog_bereich = ui.element('div')     # fester Platz für Dialoge

    def geaendert():
        """Nach jeder Änderung: alle Tablets informieren und eigene Ansicht neu zeichnen."""
        sync.aenderung_melden()
        zustand['version'] = sync.version()
        stationen_liste.refresh()
        uebungen_liste.refresh()

    # ============================================================ STATIONEN
    @ui.refreshable
    def stationen_liste():
        online_punkte.clear()
        stationen = db.alle_stationen()
        with ui.row().classes('w-full items-center gap-3 mb-4'):
            ui.button('Neue Station', icon='add', on_click=lambda: station_dialog(None))
            ui.button('Alle: Zufall an', icon='casino', color='warning', on_click=lambda: alle_modus('zufall')) \
                .props('outline')
            ui.button('Alle: Fest', icon='lock', on_click=lambda: alle_modus('fest')).props('outline color=grey-8')

        if not stationen:
            ui.label('Noch keine Stationen. Lege die erste an!').classes('text-gray-500 text-lg')
        with ui.grid().classes('w-full gap-4').style('grid-template-columns: repeat(auto-fill, minmax(300px, 1fr))'):
            for s in stationen:
                station_karte(s)

    def station_karte(s):
        uebungen = db.station_uebungen(s['id'])
        aktuell = db.uebung_holen(s['aktuelle_uebung_id']) if s['aktuelle_uebung_id'] else None
        with ui.card().classes('karte p-5 gap-3'):
            with ui.row().classes('w-full items-center justify-between no-wrap'):
                with ui.row().classes('items-center gap-3 no-wrap'):
                    ui.label(str(s['nummer'])).classes('text-2xl font-bold text-white rounded-xl px-3 py-1') \
                        .style(f'background:{BLAU}')
                    ui.label(s['name'] or 'Ohne Namen').classes('text-xl font-bold')
                online_punkte[s['nummer']] = ui.icon('circle', size='14px')

            with ui.row().classes('items-center gap-2'):
                ui.icon('play_circle', color='positive')
                ui.label(aktuell['name'] if aktuell else '- keine Übung -').classes('text-lg')

            ui.label(f'{len(uebungen)} Übungen  ·  Timer {s["dauer_sekunden"]} s').classes('text-gray-500')

            ui.switch('Zufallsmodus', value=s['modus'] == 'zufall',
                      on_change=lambda e, sid=s['id']: modus_aendern(sid, e.value)).props('color=warning')

            with ui.row().classes('w-full gap-2'):
                ui.button('Bearbeiten', icon='edit', on_click=lambda st=s: station_dialog(st)).props('outline')
                ui.button(icon='casino', on_click=lambda sid=s['id']: fuer_station_wuerfeln(sid)) \
                    .props('outline color=warning').tooltip('Neu würfeln')
                ui.button(icon='open_in_new', on_click=lambda nr=s['nummer']: ui.navigate.to(f'/station/{nr}', new_tab=True)) \
                    .props('outline color=grey-8').tooltip('Stationsansicht öffnen')
        online_aktualisieren()

    def online_aktualisieren():
        for nummer, punkt in online_punkte.items():
            punkt.props(f'color={"positive" if sync.ist_online(nummer) else "grey-4"}')

    def modus_aendern(station_id, zufall):
        db.modus_setzen(station_id, 'zufall' if zufall else 'fest')
        geaendert()

    def alle_modus(modus):
        for s in db.alle_stationen():
            db.modus_setzen(s['id'], modus)
        geaendert()
        ui.notify('Alle Stationen: ' + ('Zufallsmodus' if modus == 'zufall' else 'feste Übung'))

    def fuer_station_wuerfeln(station_id):
        u = db.zufaellige_uebung(station_id)
        if u is None:
            ui.notify('Keine Übungen zugeordnet', type='warning')
            return
        geaendert()
        ui.notify(f'Neue Übung: {u["name"]}')

    def station_dialog(s):
        """Station anlegen (s=None) oder bearbeiten."""
        alle = {u['id']: u['name'] for u in db.alle_uebungen()}
        zugeordnet = [u['id'] for u in db.station_uebungen(s['id'])] if s else []
        naechste_nr = max([x['nummer'] for x in db.alle_stationen()], default=0) + 1

        with dialog_bereich, ui.dialog() as d, ui.card().classes('karte p-6 gap-3').style('min-width: 520px'):
            ui.label('Station bearbeiten' if s else 'Neue Station').classes('text-2xl font-bold')
            with ui.row().classes('w-full gap-3 no-wrap'):
                nummer = ui.number('Nummer', value=s['nummer'] if s else naechste_nr, min=1, format='%d') \
                    .props('outlined').classes('w-28')
                name = ui.input('Name', value=s['name'] if s else '').props('outlined').classes('flex-grow')
            dauer = ui.number('Timer (Sekunden)', value=s['dauer_sekunden'] if s else 60, min=5, step=5, format='%d') \
                .props('outlined')
            modus = ui.toggle({'zufall': 'Zufall', 'fest': 'Feste Übung'}, value=s['modus'] if s else 'zufall')
            uebungen = ui.select(alle, multiple=True, value=zugeordnet, label='Übungen an dieser Station') \
                .props('outlined use-chips').classes('w-full')
            aktuell = ui.select(alle, value=s['aktuelle_uebung_id'] if s else None, clearable=True,
                                label='Aktuell angezeigte Übung').props('outlined').classes('w-full')

            def speichern():
                andere = [x for x in db.alle_stationen() if not s or x['id'] != s['id']]
                if any(x['nummer'] == int(nummer.value or 0) for x in andere):
                    ui.notify(f'Station {int(nummer.value)} gibt es schon', type='negative')
                    return
                station_id = db.station_speichern({
                    'nummer': int(nummer.value), 'name': name.value, 'modus': modus.value,
                    'dauer_sekunden': int(dauer.value or 60), 'aktuelle_uebung_id': aktuell.value,
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
        d.on('hide', d.delete)
        d.open()

    # ============================================================ ÜBUNGEN
    @ui.refreshable
    def uebungen_liste():
        uebungen = db.alle_uebungen()
        ui.button('Neue Übung', icon='add', on_click=lambda: uebung_dialog(None)).classes('mb-4')
        with ui.grid().classes('w-full gap-4').style('grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))'):
            for u in uebungen:
                hat_video = bool(u['video']) and (VIDEO_ORDNER / u['video']).exists()
                with ui.card().classes('karte p-5 gap-2 cursor-pointer').on('click', lambda uu=u: uebung_dialog(uu)):
                    with ui.row().classes('w-full items-center justify-between no-wrap'):
                        ui.label(u['name']).classes('text-xl font-bold')
                        ui.icon('videocam' if hat_video else 'videocam_off',
                                color='positive' if hat_video else 'grey-5')
                    with ui.row().classes('gap-2'):
                        ui.badge(u['schwierigkeit'], color=SCHWIERIGKEIT_FARBE.get(u['schwierigkeit']))
                        if u['kategorie']:
                            ui.badge(u['kategorie'], color='grey-7')
                        if u['wiederholungen']:
                            ui.badge(u['wiederholungen'], color='primary')
                    ui.label(u['beschreibung']).classes('text-gray-500 text-sm')

    def uebung_dialog(u):
        """Übung anlegen (u=None) oder bearbeiten - inkl. Video-Upload."""
        video = {'datei': u['video'] if u else None}

        with dialog_bereich, ui.dialog() as d, ui.card().classes('karte p-6 gap-3').style('min-width: 560px'):
            ui.label('Übung bearbeiten' if u else 'Neue Übung').classes('text-2xl font-bold')
            name = ui.input('Name', value=u['name'] if u else '').props('outlined').classes('w-full')
            beschreibung = ui.textarea('Beschreibung / Technik-Hinweise', value=u['beschreibung'] if u else '') \
                .props('outlined autogrow').classes('w-full')
            with ui.row().classes('w-full gap-3 no-wrap'):
                kategorie = ui.select(db.alle_kategorien(), value=(u['kategorie'] or None) if u else None,
                                      label='Kategorie', with_input=True, new_value_mode='add-unique') \
                    .props('outlined').classes('flex-grow')
                wdh = ui.input('Wiederholungen / Dauer', value=u['wiederholungen'] if u else '',
                               placeholder='z. B. 15 Wdh. oder 30 Sek.').props('outlined').classes('flex-grow')
            schwierigkeit = ui.toggle(SCHWIERIGKEITEN, value=u['schwierigkeit'] if u else 'mittel')

            ui.label('Video (MP4)').classes('font-bold mt-2')
            video_info = ui.label().classes('text-gray-600')

            def info_zeigen():
                vorhanden = video['datei'] and (VIDEO_ORDNER / video['datei']).exists()
                video_info.text = f'✔ {video["datei"]}' if vorhanden else 'Noch kein Video hochgeladen'
                video_info.style(f'color:{GRUEN if vorhanden else "#64748B"}')
            info_zeigen()

            async def hochgeladen(e):
                dateiname = f'{uuid.uuid4().hex[:8]}_{e.file.name}'
                await e.file.save(VIDEO_ORDNER / dateiname)
                video['datei'] = dateiname
                info_zeigen()
                ui.notify('Video hochgeladen', type='positive')

            ui.upload(on_upload=hochgeladen, auto_upload=True, label='MP4 auswählen') \
                .props('accept=video/mp4 flat bordered').classes('w-full')

            def speichern():
                if not name.value.strip():
                    ui.notify('Bitte einen Namen eingeben', type='negative')
                    return
                db.uebung_speichern({
                    'name': name.value.strip(), 'beschreibung': beschreibung.value or '',
                    'kategorie': kategorie.value or '', 'schwierigkeit': schwierigkeit.value,
                    'wiederholungen': wdh.value or '', 'video': video['datei'],
                }, u['id'] if u else None)
                d.close()
                geaendert()
                ui.notify('Gespeichert', type='positive')

            def loeschen():
                db.uebung_loeschen(u['id'])
                d.close()
                geaendert()

            with ui.row().classes('w-full justify-between mt-2'):
                if u:
                    ui.button('Löschen', icon='delete', color='negative', on_click=loeschen).props('flat')
                else:
                    ui.element()
                with ui.row():
                    ui.button('Abbrechen', on_click=d.close).props('flat')
                    ui.button('Speichern', icon='save', color='positive', on_click=speichern)
        d.on('hide', d.delete)
        d.open()

    # ------------------------------------------------------------ Tabs
    with ui.tab_panels(tabs, value=tab_stationen).classes('w-full bg-transparent'):
        with ui.tab_panel(tab_stationen):
            stationen_liste()
        with ui.tab_panel(tab_uebungen):
            uebungen_liste()

    # Synchronisation: Änderungen von den Stationen (z. B. Schüler würfelt) übernehmen
    def pruefen():
        online_aktualisieren()
        if sync.version() != zustand['version']:
            zustand['version'] = sync.version()
            stationen_liste.refresh()
    ui.timer(1.0, pruefen)
