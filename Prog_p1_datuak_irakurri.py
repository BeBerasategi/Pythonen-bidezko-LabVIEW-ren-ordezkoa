import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import time

#Begin communication--------------------------------------------------------------------------

rm = pyvisa.ResourceManager()
my_instrument = rm.open_resource('ASRL1::INSTR')

my_instrument.baud_rate = 9600
my_instrument.data_bits=8
my_instrument.parity=0 #None
my_instrument.stop_bits=10 #one = <StopBits.one: 10>
my_instrument.flow_control=0 #none

my_instrument.read_termination = '\n'
my_instrument.write_termination = '\r'

print(f"{'List of resources:':<25}{rm.list_resources()}")
print(f"{'Current instrument:':<25}{my_instrument}",end=2*'\n')


#Functions defined for making communication easier--------------------------------------------

def full_print(my_instrument):
    #Reads and prints the device's whole answer
    while True:
        try:
            s=str(my_instrument.read()).strip()
            ss=''
            if '*' in s:
                my_instrument.clear()
                break
            else:
                print('    '+s)
        except UnicodeDecodeError:
            print('----UnicodeDecodeError----')

def full_read(my_instrument):
    #Reads and returns just the first line
    try:
        s=str(my_instrument.read())
        my_instrument.clear()
        return s
    except UnicodeDecodeError:
        print('----UnicodeDecodeError----')

def full_query(my_instrument, arg):
    #Writes arg, reads and returns just the first line
    my_instrument.write(arg)
    try:
        s=str(my_instrument.read())
        my_instrument.clear()
        return s
    except UnicodeDecodeError:
        print('----UnicodeDecodeError----')

def plot_Tt(tenp,t):
    plt.ylim(20, 40)
    plt.scatter(t, tenp, c='blue')
    plt.grid()
    plt.title("Thermometer reading")
    plt.xlabel("t (s)")
    plt.ylabel("T (ºC)")
    plt.pause(0.5)

#---------------------------------------------------------------------------------------------

##my_instrument.write('t')
##print(my_instrument.read())
##my_instrument.clear()
##my_instrument.write('b')
##print(my_instrument.read())
##my_instrument.clear()

#Print data
print(f"{'Enclosure temperature:':<25}{full_query(my_instrument, 'b')[2:]}ºC")

#Print system information
print(f"{'System information:':<25}")
my_instrument.write('i')
full_print(my_instrument)

#Print help
#my_instrument.write('h')
#full_print(my_instrument)

n=int(input('Set the desired number of measurements: '))
print(f"{'t(s)':<5}{'T(ºC)':>10}")

start_time = time.time()
for i in range(n):
    tenp=float(full_query(my_instrument, 't'))
    t=time.time()-start_time
    print(f"{t:<5.3f}{tenp:>10}")
    plot_Tt(tenp,t)

my_instrument.close()

