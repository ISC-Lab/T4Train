#!/usr/bin/env python3
# ============================================================================
""" 
The arduino nano 33 data handler receives data via serial from a nano 33,
reshapes the data by channels, and hands a complete data frame to T4Train.
This data handler compared to the Arduino data handler, is optimized to maximize
the data throughput. 


Setup: In config.ini, set the proper `DS_FILE_NUM` index that corresponds 
to this file, based on the filenames listed in `DS_FILENAMES`. The
`FRAME_LENGTH' needs to match ``samplelength'' in this file and the 
`CHANNELS' needs to match ``numchannels''.

Performance Notes: There are many ``magic numbers'' in this file. These
numbers maximized the performance of the Teensy while retaining reliability. 
A baud rate greater than 2000000 decreases reliability and a sample length
greater than 1500 causes timing issues on the Teensy. This file is largely
not ``plug-and-play'' for performance. 

"""
# ============================================================================


# System
import os
import sys
import time
import signal
import configparser
from datetime import timedelta
import glob

# Data processing
import numpy as np
# from scipy import signal

# serial
import serial

# for windows
from timeloop import Timeloop

# Self-define functions
# import utils



def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    # Windows
    if sys.platform.startswith('win'):
        ports=['COM%s' % (i + 1) for i in range(6)]
    # Linux
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports=glob.glob('/dev/tty[A-Za-z]*')
    # MAC
    elif sys.platform.startswith('darwin'):
        ports=glob.glob('/dev/tty.usb*')
    else:
        raise EnvironmentError('Unsupported platform')

    return ports

def get_serial():
    # Get serial port name based on different OS

    # Windows
    if sys.platform.startswith('win'):
        s=serial.Serial('COM3')

    # ubuntu or VM on Windows
    if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # /dev/ttyACM0 if real machine or /dev/ttyS0
        s=serial.Serial('/dev/ttyACM0', 200000)

    # Mac
    if sys.platform.startswith('darwin'):
        ports=serial_ports()
        if len(ports)==0:
            print("ds_teensy.py: No open serial ports detected! Quit.")
            sys.exit()
        else:
            preferred_port = None
            s = None
            for port in ports:
                if "usbmodem" in port or "teensy" in port:
                    preferred_port = port

            if preferred_port:
                # if we have a port with a familiar arduino or teensy name, pick it
                print("Connecting to preferred port: {}".format(preferred_port))
                s = serial.Serial(preferred_port,
                                  9600,
                                  timeout=None,
                                  bytesize=serial.EIGHTBITS,
                                  xonxoff=False,
                                  rtscts=False,
                                  dsrdtr=False)
            else:
                # otherwise, just go with the first port
                print("Connecting to first available port: {}".format(ports[0]))
                s = serial.Serial(serial_ports()[0],
                                  9600,
                                  timeout=None,
                                  bytesize=serial.EIGHTBITS,
                                  xonxoff=False,
                                  rtscts=False,
                                  dsrdtr=False)

    return s


if __name__ == '__main__':
    print('ds_nano33.py: Started')

    # write PID to file
    pidnum=os.getpid()
    f=open("ds_pidnum.txt", "w")
    f.write(str(pidnum))
    f.close()

    # List all ports
    print("All ports:")
    print(serial_ports())

    # Get a serial port
    s=get_serial()

    # Hook up crtl+c to self-define function
    # MAC, linux
    if utils.does_support_signals():
        signal.signal(signal.SIGINT, receive_interrupt)

        # Collect data forever
        while True:
            teensy_data(s)






    s.close()
    sys.exit()

    