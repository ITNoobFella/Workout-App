"""Testdaten mit denselben Funktionsnamen wie später database.py."""
import random

STATIONEN = [
    {'id': 1, 'nummer': 1, 'name': 'Oberkörper', 'dauer_sekunden': 60,
     'modus': 'zufall', 'uebung_ids': [1, 2, 3], 'aktuelle_uebung_id': 1},
    {'id': 2, 'nummer': 2, 'name': 'Beine', 'dauer_sekunden': 60,
     'modus': 'zufall', 'uebung_ids': [3, 4], 'aktuelle_uebung_id': 4},
]

UEBUNGEN = [
    {'id': 1, 'name': 'Liegestütze','wiederholungen': 12, 'video': 'liegestuetze.mp4'},
    {'id': 2, 'name': 'Plank','wiederholungen': 1, 'video': 'plank.mp4'},
    {'id': 3, 'name': 'Burpees', 'wiederholungen': 10, 'video': 'Burpees.mp4'},
    {'id': 4, 'name': 'Kniebeugen', 'wiederholungen': 10, 'video': 'Knieboegen.mp4'},
    {'id': 5, 'name': 'Hampelmann', 'wiederholungen': 10, 'video': 'jumping_jacks.mp4'},
    {'id': 6, 'name': 'Crunches', 'wiederholungen': 15, 'video': 'crunch.mp4'},
]


# ------------------------------------------------------------------ Stationen
def alle_stationen():
    return STATIONEN


def station_nach_nummer(nummer):
    return next((s for s in STATIONEN if s['nummer'] == nummer), None)


def _station_nach_id(station_id):
    return next((s for s in STATIONEN if s['id'] == station_id), None)


def station_uebungen(station_id):
    s = _station_nach_id(station_id)
    if not s:
        return []
    return [u for u in UEBUNGEN if u['id'] in s['uebung_ids']]


def station_speichern(daten, station_id=None):
    if station_id is None:
        neue_id = max((s['id'] for s in STATIONEN), default=0) + 1
        STATIONEN.append({'id': neue_id, 'modus': 'zufall', 'uebung_ids': [],
                          'aktuelle_uebung_id': None, **daten})
        return neue_id
    _station_nach_id(station_id).update(daten)
    return station_id


def station_loeschen(station_id):
    STATIONEN[:] = [s for s in STATIONEN if s['id'] != station_id]


def station_uebungen_setzen(station_id, uebung_ids):
    s = _station_nach_id(station_id)
    if s:
        s['uebung_ids'] = list(uebung_ids)


def modus_setzen(station_id, modus):
    s = _station_nach_id(station_id)
    if s:
        s['modus'] = modus


def aktuelle_uebung_setzen(station_id, uebung_id):
    s = _station_nach_id(station_id)
    if s:
        s['aktuelle_uebung_id'] = uebung_id


# ------------------------------------------------------------------ Übungen
def uebung_holen(uebung_id):
    return next((u for u in UEBUNGEN if u['id'] == uebung_id), None)


def zufaellige_uebung(station_id):
    """Zufällige Übung der Station, möglichst nicht dieselbe wie vorher."""
    s = _station_nach_id(station_id)
    kandidaten = station_uebungen(station_id)
    if not kandidaten:
        return None
    if len(kandidaten) > 1:
        kandidaten = [u for u in kandidaten if u['id'] != s.get('aktuelle_uebung_id')]
    gewaehlt = random.choice(kandidaten)
    aktuelle_uebung_setzen(station_id, gewaehlt['id'])
    return gewaehlt


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
    for s in STATIONEN:                                     # auch aus den Stationen entfernen
        s['uebung_ids'] = [i for i in s['uebung_ids'] if i != uebung_id]
        if s.get('aktuelle_uebung_id') == uebung_id:
            s['aktuelle_uebung_id'] = None