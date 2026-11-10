"""Gemeinsames Aussehen aller Seiten (Farben, Touch-Optimierung)."""
from nicegui import ui

from config import BLAU, DUNKELBLAU, GRUEN, ORANGE


def anwenden(dunkel=False):
    ui.colors(primary=BLAU, secondary=DUNKELBLAU, positive=GRUEN, warning=ORANGE, accent=ORANGE, dark=DUNKELBLAU)
    ui.add_head_html('''
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    ''')
    ui.add_css(f'''
        body {{ -webkit-user-select: none; user-select: none; touch-action: manipulation;
               font-family: -apple-system, "Segoe UI", Roboto, sans-serif; }}
        input, textarea {{ -webkit-user-select: text; user-select: text; }}
        .q-btn {{ min-height: 48px; border-radius: 12px; }}   /* Touch: große Schaltflächen */
        .karte {{ border-radius: 16px; }}
    ''')
    if dunkel:
        ui.query('body').style(f'background-color: {DUNKELBLAU}; color: white')
    else:
        ui.query('body').style('background-color: #F1F5F9')