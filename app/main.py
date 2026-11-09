from nicegui import ui

ui.colors(primary='#0F172A', secondary='#3B82F6', accent='#10B981')
ui.label('Hello NiceGUI!').classes('text-2xl text-secondary font-bold1')
ui.label('Hello Niklas!').classes('text-3xl text-secondary font-bold1')
ui.button('Test Button', on_click=lambda: ui.notify('Hello, Pollo frito'))

ui.run()
                