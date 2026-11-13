"""Workout Generator - Startpunkt der Anwendung.

Starten:  python main.py
Danach im Browser / auf den iPads:  http://<IP-dieses-Rechners>:8080
"""
from nicegui import app, ui
from config import VIDEO_ORDNER

app.add_media_files('/videos', VIDEO_ORDNER)

#import database as db
from config import PORT, STORAGE_SECRET
from pages import master_view, start, station_view  # noqa: F401  (registriert die Seiten)

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(title='Workout Generator', host='0.0.0.0', port=PORT,
           storage_secret=STORAGE_SECRET, favicon='💪', language='de')
