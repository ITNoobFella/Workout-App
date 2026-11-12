"""Testdaten mit denselben Funktionsnamen wie später database.py."""
import random

STATIONEN = [
    {'id': 1, 'nummer': 1, 'name': 'Oberkörper'},
    {'id': 2, 'nummer': 2, 'name': 'Beine'},
]

UEBUNGEN = [
    {'id': 1, 'name': 'Liegestütze', 'beschreibung': 'Rücken gerade halten, Brust bis kurz vor den Boden.',
     'schwierigkeit': 'mittel', 'wiederholungen': 12},
    {'id': 2, 'name': 'Plank', 'beschreibung': 'Körper bildet eine gerade Linie, Bauch anspannen.',
     'schwierigkeit': 'mittel', 'wiederholungen': 1},
    {'id': 3, 'name': 'Burpees', 'beschreibung': 'Kniebeuge, Liegestütz, Sprung nach oben.',
     'schwierigkeit': 'schwer', 'wiederholungen': 10},
]


def alle_stationen():
    return STATIONEN


def station_nach_nummer(nummer):
    return next((s for s in STATIONEN if s['nummer'] == nummer), None)


def zufaellige_uebung(station_id):
    return random.choice(UEBUNGEN)