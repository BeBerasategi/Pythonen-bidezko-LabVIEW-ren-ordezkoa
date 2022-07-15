import PySimpleGUI as sg
import os.path
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')







# The window will have two columns. The elements of each of these are defined in the following lines, using lists. -----------------------------------

first_column = [
    [   sg.Text('VISA resource name'), sg.Text('Time unit (s)')],
    [   sg.Combo(['', 'Tenp'],\
        s=(15,22), enable_events=True, readonly=True, key='-DEVICE-'),
        sg.Input(s=15)
    ],
    [
        sg.Text("Folder to save data")],
    [   sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [   sg.Text('Buffer')],
    [   sg.Multiline(s=(40, 20), enable_events=True, \
                     no_scrollbar = True, autoscroll=True, key="-BUFFER-", \
                     default_text= 'No data yet', do_not_clear=False)
    ],
]

second_column = [
    [
        sg.Button('Start', s=(10,2), enable_events=True, key="-START-"),
        sg.Button('Stop', s=(10,2),  enable_events=True, key="-STOP-")
    ],
    [   sg.Text('Temperature')],
    [   sg.Multiline(s=(25, 1), enable_events=True, \
                     no_scrollbar = True, key="-TEMPERATURE-", \
                     default_text= ' ')
    ],
    [sg.Canvas(s=(40, 20), key='-CANVAS-')]
]


# Configuration of the right click menu ----------------------------------------------------------------------------------------------------------------

MENU_RIGHT_CLICK_EDITME_VER_EXIT = ['', ['Exit']]
'''
Add this to your window call:
right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT
'''


# Matplotlib code here----------------------------------------------------------------------------------------------------------------------------------
fig = matplotlib.figure.Figure(figsize=(3.5, 3), dpi=100)
t = np.arange(0, 3, .01)
fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

#MATPLOTLIB helper code
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

#--------------------------------------------------------------------------------------------------------------------------------------------------------












# Full layout --------------------------------------------------------------------------------------------------------------------------------------------

layout = [
    [
        sg.Column(first_column, s=(350,500)),
        sg.VSeperator(),
        sg.Column(second_column, s=(350,500)),
    ]
]

window = sg.Window("Temperature reading", layout, finalize=True, \
                   right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT)
fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)




# Run the Event Loop ----------------------------------------------------------------------------------------------------------------------------------------

while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []

window.close()
