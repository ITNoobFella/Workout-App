"""Synchronisation zwischen Master und Station-Tablets (einfach gehalten)."""
import time

_version = 0
_letzter_kontakt = {}   # Stationsnummer -> Zeitpunkt der letzten Meldung


def aenderung_melden():
    global _version
    _version += 1


def version():
    return _version


def station_meldet_sich(nummer):
    _letzter_kontakt[nummer] = time.time()


def ist_online(nummer):
    return time.time() - _letzter_kontakt.get(nummer, 0) < 3