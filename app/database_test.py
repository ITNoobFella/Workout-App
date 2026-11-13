"""Testdaten mit denselben Funktionsnamen wie später database.py."""
import random

STATIONEN = [
    {'id': 1, 'nummer': 1, 'name': 'Oberkörper', 'dauer_sekunden':60},
    {'id': 2, 'nummer': 2, 'name': 'Beine', 'dauer_sekunden': 60},
]

UEBUNGEN = [
    {'id': 1, 'name': 'Liegestütze', 'beschreibung': 'Rücken gerade halten, Brust bis kurz vor den Boden.',
     'schwierigkeit': 'mittel', 'wiederholungen': 12, 'video': 'liegestuetze.mp4'},
    {'id': 2, 'name': 'Plank', 'beschreibung': 'Körper bildet eine gerade Linie, Bauch anspannen.',
     'schwierigkeit': 'mittel', 'wiederholungen': 1},
    {'id': 3, 'name': 'Burpees', 'beschreibung': 'Kniebeuge, Liegestütz, Sprung nach oben.',
     'schwierigkeit': 'schwer', 'wiederholungen': 10},
    {'id': 4, 'name': 'Kniebeugen', 'beschreibung': 'Kniebeuge, Liegestütz, Sprung nach oben.',
    'schwierigkeit': 'schwer', 'wiederholungen': 10, 'video': 'Knieboegen.mp4'},
]



def station_nach_nummer(nummer):
    return next((s for s in STATIONEN if s['nummer'] == nummer), None)


def zufaellige_uebung(station_id):
    return random.choice(UEBUNGEN) if UEBUNGEN else None

def alle_uebungen():
    return sorted(UEBUNGEN, key=lambda u: u['name'])


def uebung_speichern(daten, uebung_id=None):
    if uebung_id is None:                                   # neu anlegen
        neue_id = max((u['id'] for u in UEBUNGEN), default=0) + 1
        UEBUNGEN.append({'id': neue_id, **daten})
    else:                                                   # bestehende ändern
        for u in UEBUNGEN:
            if u['id'] == uebung_id:
                u.update(daten)

def uebung_loeschen(uebung_id):
    UEBUNGEN[:] = [u for u in UEBUNGEN if u['id'] != uebung_id]