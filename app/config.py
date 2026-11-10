"""Zentrale Einstellungen der App."""
from pathlib import Path

# Ordner
BASIS_ORDNER = Path(__file__).parent
DATEN_ORDNER = BASIS_ORDNER / 'daten'
VIDEO_ORDNER = BASIS_ORDNER / 'videos'
DB_DATEI = DATEN_ORDNER / 'workout.db'

DATEN_ORDNER.mkdir(exist_ok=True)
VIDEO_ORDNER.mkdir(exist_ok=True)

# Server
PORT = 8080
STORAGE_SECRET = 'workout-generator-bitte-aendern'  # für Login-Sitzungen

# PIN für den Lehrkraft-Bereich (Master)
MASTER_PIN = '1234'

# Farbpalette
DUNKELBLAU = '#0F172A'
BLAU = '#3B82F6'
GRUEN = '#10B981'
ORANGE = '#F59E0B'

SCHWIERIGKEITEN = ['leicht', 'mittel', 'schwer']
SCHWIERIGKEIT_FARBE = {'leicht': GRUEN, 'mittel': ORANGE, 'schwer': '#EF4444'}
