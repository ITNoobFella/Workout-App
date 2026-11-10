from nicegui import ui

from pages import theme

STATIONEN = [{'nummer': 1}, {'nummer': 2}, {'nummer': 3}]   # Testdaten statt db.alle_stationen()


@ui.page('/')
def startseite():
    theme.anwenden(dunkel=True)
    with ui.column().classes('w-full items-center gap-8 p-10'):
        ui.icon('fitness_center', size='72px', color='warning')
        ui.label('Workout Generator').classes('text-5xl font-bold')
        with ui.row().classes('gap-4'):
            for s in STATIONEN:
                ui.button(str(s['nummer']), color='positive',
                          on_click=lambda nr=s['nummer']: ui.navigate.to(f'/station/{nr}')) \
                    .classes('w-20 h-20 text-3xl font-bold')