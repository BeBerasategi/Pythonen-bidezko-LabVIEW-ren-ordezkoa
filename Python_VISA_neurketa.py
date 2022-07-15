import PySimpleGUI as sg
import os.path

#For graphing:
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib
matplotlib.use('TkAgg')

import time


#VISA communication:
import pyvisa


#Instrument interaction related functions:
def full_query(my_instrument, arg):
    my_instrument.write(arg)
    try:
        s=str(my_instrument.read())
        my_instrument.clear()
        return s
    except UnicodeDecodeError:
        window["-BUFFER-"].print('----UnicodeDecodeError----')

def full_print(my_instrument):
    while True:
        try:
            s=str(my_instrument.read()).strip()
            ss=''
            if '*' in s:
                my_instrument.clear()
                break
            else:
                window["-BUFFER-"].print('    '+s)
        except UnicodeDecodeError:
            window["-BUFFER-"].print('----UnicodeDecodeError----')


#Functions needed for graphing:
def fig_maker(t,tenp):
    plt.ylim(20, 40)
    plt.grid()
    plt.scatter(t, tenp, c='blue')
    return plt.gcf()

def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def delete_fig_agg(fig_agg):
    fig_agg.get_tk_widget().forget()
    plt.close('all')

    
#---------------------------------------------------------------------------------------------------------


# Define the elements for the GUI

first_column = [
    [   sg.Text('VISA resource name',s=(20,1)), sg.Text('Time unit (s)',s=(20,1))],
    [   sg.Combo(['', 'Temperature', 'Arduino'],\
        s=(20,1), enable_events=True, readonly=True, key='-DEVICE-'),
        sg.Input(s=20, key='-TUNIT-', enable_events=True, default_text= '0.5')
    ],
    [
        sg.Text("File to save data")],
    [   sg.In(s=(30, 1), enable_events=True, key="-FILE-"),
        sg.FileBrowse(s=(10, 1)),
    ],
    [   sg.Text('Buffer')],
    [   sg.Multiline(s=(45, 20), enable_events=True, \
                     no_scrollbar = True, autoscroll=True, key="-BUFFER-", \
                     default_text= 'No data yet', do_not_clear=True)
    ],
]

second_column = [
    [   sg.Text('Time (s)',s=(17,1)),
        sg.Text('Temperature (ºC)',s=(20,1))
    ],
    [   sg.Multiline(s=(20, 1), enable_events=True, \
                     no_scrollbar = True, key="-TIME-", \
                     default_text= ' '),
        sg.Multiline(s=(20, 1), enable_events=True, \
                     no_scrollbar = True, key="-TEMPERATURE-", \
                     default_text= ' ')
    ],
    [   sg.VPush()],
    [   sg.Text('T vs t plot')],
    [   sg.Canvas(s=(300, 260), key='-CANVAS-',background_color='white')],
    [   sg.Text('', s=(10,1))],
    [
        sg.Button('Start', s=(11,2), enable_events=True, key="-START-"),
        sg.Button('Stop', s=(11,2),  enable_events=True, key="-STOP-"),
        sg.Button('Exit', s=(11,2),  enable_events=True, key="-EXIT-")
    ],
    [
        sg.Button('System Information', s=(37,1), enable_events=True, key="-INFO-")
    ]
]

# Set the right click menu
MENU_RIGHT_CLICK_EDITME_VER_EXIT = ['', ['Version', 'Exit']]
'''
Add this to your window call:
right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT
'''


# Set the full layout and the window
layout = [
    [
        sg.Column(first_column, s=(350,500)),
        sg.VSeperator(),
        sg.Column(second_column, s=(350,500)),
    ]
]

window = sg.Window("Temperature reading", layout, finalize=True, \
                   right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT)



# Run the Event Loop --------------------------------------------------------------------------------------

break_out_flag = False   #This will help us to exit all the while loops, from the innermost to the outside.
file_flag=False          #This speficies wheteher a file name has been given or not.
t_unit=0.5               #The default time between measurements will be 0.5s.

fig_agg0 = None          

while True:
    event, values = window.read()

    #Exit the program:
    if event == "Exit" or event == sg.WIN_CLOSED or break_out_flag or event == '-EXIT-':
        break

    #Choose and configure the device. It only works for the thermometer.
    elif event == '-DEVICE-':
        rm = pyvisa.ResourceManager()
        if values['-DEVICE-'] == 'Temperature':
            try:
                #Set connection with the device
                my_instrument = rm.open_resource('ASRL1::INSTR')
                my_instrument.baud_rate = 9600
                my_instrument.data_bits=8
                my_instrument.parity=0        #None
                my_instrument.stop_bits=10    #one = <StopBits.one: 10>
                my_instrument.flow_control=0  #none

                my_instrument.read_termination = '\n'
                my_instrument.write_termination = '\r'

                window["-BUFFER-"].update(f"Current instrument:\n{my_instrument}\n\n")
            except:
                window["-BUFFER-"].print('Connection with the thermometer can not be done. \
                                    Try again.', end=2*'\n')
                continue
            finally:
                #Print data
                window["-BUFFER-"].print(f"{'Enclosure temperature:':<25}{full_query(my_instrument, 'b')[2:]}ºC", end=2*'\n')
            
        elif values['-DEVICE-'] == 'Arduino':
            window["-BUFFER-"].update("This program does not support the selected device.")
        else:
            window["-BUFFER-"].update('No device selected.')

    #Choose and open the file where the data will be written.
    elif event == "-FILE-":
        file_name = values["-FILE-"]
        if file_name.lower().endswith((".txt", ".dat")):
            window["-BUFFER-"].update(f'Data will be written in: {file_name}')
            file_flag=True
            try:
                file=open(file_name, 'w', encoding='utf-8')
            except:
                window["-BUFFER-"].update("Error while opening the file.\n")
        else:
            window["-BUFFER-"].update('The file type is not correct. Try .txt or .dat.')
            #raise TypeError('The file type is not correct. Try .txt or .dat')

    #Set a different timing between measurements.
    elif event == '-TUNIT-':
        try:
            t_unit=float(values['-TUNIT-'])
            window["-BUFFER-"].update(f'Time unit: {t_unit}s.')
        except:
            window["-BUFFER-"].update('Time unit value error.')
            t_unit=0.5

    #This configures one of the options of the right-click menu.
    elif event == 'Version':
        sg.popup_scrolled(sg.get_versions())

    #Pressing the STOP button will pause the program but will not close it.
    elif event == '-STOP-':
        window["-BUFFER-"].update('')
        window["-TIME-"].update('')
        window["-TEMPERATURE-"].update('')
        delete_fig_agg(fig_agg0)

    #Pressing the INFO button will print the system information that the computer can get.
    elif event == '-INFO-':
        if values['-DEVICE-'] == 'Temperature':
            window["-BUFFER-"].update("System information:")
            my_instrument.write('i')
            full_print(my_instrument)
        else:
            window["-BUFFER-"].update('Select an appropriate device.')
            
    #Pressing START will begin the measurements. An additional while loop will be needed.
    elif event == '-START-':
        if values['-DEVICE-'] != 'Temperature': #This program only supports the thermometer.
            window["-BUFFER-"].update('Select an appropriate device.')
            continue
        window["-BUFFER-"].update(f"{'  t(s)':>10}        {'T(ºC)':^10}\n")
        t_0=time.time()
        t_1=0
        t_list=[]
        tenp_list=[]
        while True:
            event, values = window.read(timeout=1) #Unit: ms
            if event == "Exit" or event == sg.WIN_CLOSED:
                break_out_flag=True #When this is checked in the general loop, the cycle will be exited without needing to press EXIT again.
                break
            elif event == "-STOP-": #Pressing STOP does not delete the data written on the file, it only adds an empty line between sets of measurements.
                if file_flag:
                    file.write("\n")
                break
            else:
                t=time.time()-t_0
                if t-t_1 >= t_unit:
                    t_1=t
                    tenp=float(full_query(my_instrument, 't'))
                    window["-BUFFER-"].print(f"{t:>10.3f}        {tenp:<10}", end='\n')
                    window["-TIME-"].update(round(t,3))
                    window["-TEMPERATURE-"].update(tenp)

                    t_list.append(t)
                    tenp_list.append(tenp)
                    fig = fig_maker(t_list,tenp_list)
                        
                    fig.set_size_inches(3, 2.6, forward=True)
                    fig_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
                    if fig_agg0 is not None:
                        delete_fig_agg(fig_agg0)
                    window.Refresh()
                    fig_agg0=fig_agg
                    
                    if file_flag:
                        file.write(f"{t:>10.3f}        {tenp:<10}\n")
                    
    
if file_flag: #closes the file only if a file has been opened before.
    file.close()
    
window.close()
my_instrument.close()
