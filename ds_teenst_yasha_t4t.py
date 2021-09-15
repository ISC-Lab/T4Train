#!/usr/bin/env python3
# ============================================================================
"""
The teensy data handler receives data via serial from a teensy, reshapes the
data by channels, and hands a complete data frame to T4Train. This data
handler compared to the Arduino data handler, is optimized to maximize the
data throughput for the Teensy 3.6 and Teensy 4.0.


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
import utils

# write PID to file
pidnum = os.getpid()
f = open("ds_pidnum.txt", "w")
f.write(str(pidnum))
f.close()

f = open("ds_cmd.txt", "w")
f.write("")
f.close()
#================================================================
# read in configurations
config=configparser.ConfigParser()
config.read('config.ini')

INSTANCES   =  int(config['GLOBAL'    ]['INSTANCES'   ])  # number of instances recorded when spacebar is hit
FRAME_LENGTH=  int(config['GLOBAL'    ]['FRAME_LENGTH'])  # fixed size, need to adjust
CHANNELS   =  int(config['GLOBAL'    ]['CHANNELS'   ])
#================================================================

# Global variables
is_collecting_dataset      =False   # enabled when spacebar hit

# Static variables
t_start_collect            =0       # act as static for func
training_data_frame_counter=0       # counter for spacebar hits, act as static for func
tmpframe                   =[]      # place to store current data
previousframe              =[]      # place to store previous data
training_data              =[[]]    # Store training data



print("Starting Teensy")


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(6)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.usb*')
    else:
        raise EnvironmentError('Unsupported platform')

    return ports
    
def get_serial():
    # Get serial port name based on different OS

    # Mac
    if sys.platform.startswith('darwin'):
        ports = serial_ports()
        if len(ports) == 0:
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

    # ubuntu or VM on Windows
    if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # /dev/ttyACM0 if real machine or /dev/ttyS0
        s = serial.Serial('/dev/ttyACM0', 200000)

    # Windows
    if sys.platform.startswith('win'):
        s = serial.Serial('COM3')

    return s



# read a certain number of bytes from a data stream
def readall(s, n):
    res = bytearray()
    while len(res) < n:
        chunk = s.read(n - len(res))
        if not chunk:
            raise EOFError()
        res += chunk
    return res


def resync():
    res = bytearray()
    while 1:
        b = s.read(1)  # Should make s a parameter to stay consistent with readall function
        if not b:
            raise EOFError()
        res += b
        if res.endswith(b'\xde\xad\xbe\xef'):
            break
    return res



def teensy_data(s):
    """Getting data from teensy, saving # of instances of data as tmpframe"""
    global is_collecting_dataset,       \
           tmpframe,                    \
           T_RECORD,                    \
           T_OVERLAP,                   \
           training_data_frame_counter, \
           t_start_collect,             \
           previousframe,               \
           FRAME_LENGTH,                \
           training_data,               \
           frame_complete
    instances = INSTANCES
    frame_complete = 0
    save_frames = 0
    numchannels=CHANNELS
    frame=[]
    try:
        # print("Try")
        now = time.time()
        discarded = resync()
        arr = np.frombuffer(readall(s, FRAME_LENGTH*2+4), dtype='uint16')
        #why is the FRAME_LENGTH*2+4

        if arr[-1] == 0:
            tmpframe.append(arr)
        if arr[-1] == 1:
            tmpframe.append(arr)
            frame_complete = 1
        
        if frame_complete == 1 and np.shape(tmpframe)[0] == numchannels:
            tmpframe = np.asarray(tmpframe)

            tmpframe = tmpframe[tmpframe[:, -2].argsort()]
            # print("Got tmp")
            np.save('tmpframe', tmpframe)

            if is_collecting_dataset:
                if training_data_frame_counter < instances:
                    training_data[0].append(tmpframe)
                    training_data_frame_counter += 1

                if training_data_frame_counter == instances:
                    print('Done collecting training data, saving NOW')
                    training_data_frame_counter = 0

                    # get label
                    f = open("current_label.txt", "r")
                    current_label = f.read().strip()
                    f.close()

                    training_data_file_name = 'training_data_{}.npy'.format(current_label)

                    print('Saving Training Data...')

                    if os.path.exists(os.path.join(os.getcwd(), training_data_file_name)):
                        existing_training_data = np.load(training_data_file_name)

                        np.save(training_data_file_name,
                                np.append(existing_training_data, training_data, axis=0))
                    else:
                        np.save(training_data_file_name, training_data)
                    training_data = [[]]
                    is_collecting_dataset = False

                    print('Training Data SAVED!!!')

            if save_frames == 1 and np.shape(frame)[0] < instances:
                frame.append(tmpframe)

            elif np.shape(frame)[0] == instances:
                dataset.append(frame)
                save_frames = 0
                frame = []
            tmpframe = []
            #end = time.time()
            t_start_collect=time.time()

    except Exception as e:
        print('ds_teensy:', e)
        s.close()
        sys.exit()

    end=time.time()
    return





def read_message():
    # Read command
    try:
        f = open("ds_cmd.txt", "r")
        cmd = f.read()
        f.close()
    except Exception as e:
        return

    # Check command
    if cmd == 'SPACEBAR':
        global is_collecting_dataset, t_start_collect
        is_collecting_dataset = True
        t_start_collect=time.time()
    elif cmd == 'BYE':
        s.close()
        f.close()
        sys.exit()

    # Clear command
    f = open("ds_cmd.txt", "w")
    f.write("")
    f.close()

# MAC/LINUX
def receive_interrupt(signum, stack):
    read_message()

#if __name__ == '__main__':
    #print('ds_teensy.py: Started')

    # write PID to file
    #pidnum = os.getpid()
    #f = open("ds_pidnum.txt", "w")
    #f.write(str(pidnum))
    #f.close()

    # print("All ports:")
    # print(serial_ports())

s=get_serial()


# Hook up crtl+c to self-define function
if utils.does_support_signals():
    signal.signal(signal.SIGINT, receive_interrupt)

    # Collect data forever
    while True:
        teensy_data(s)

#For Windows
timeloop = Timeloop()

# add timeloop job to handle commands
@timeloop.job(interval=timedelta(seconds=0.3))
def read_message_wrapper():
    read_message()


# add timeloop job to collect and write teensy data
@timeloop.job(interval=timedelta(seconds=0.0000001))
def teensy_data_wrapper():
    teensy_data(s)


if not utils.does_support_signals():
    timeloop.start(block=True)


print("Teensy Closing")


s.close()
sys.exit()