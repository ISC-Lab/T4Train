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
import utils


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    # Windows
    # DVS: need to sub this with gtabbing actual port in windows
    if sys.platform.startswith('win'):
        ports=['COM%s' % (i+1) for i in range(6)]
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
    global BAUD_RATE

    # Get serial port name based on different OS
    ports=serial_ports()
    if len(ports)==0:
        print("ds_nano33.py: No open serial ports detected! Quit.")
        sys.exit()

    use_port=None
    # Windows
    if sys.platform.startswith('win'):
        use_port='COM5'

    # ubuntu or VM on Windows
    if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # /dev/ttyACM0 if real machine or /dev/ttyS0
        use_port='/dev/ttyACM0'

    # DVS: need to test on MAC
    # Mac
    if sys.platform.startswith('darwin'):
        # Search for port
        for port in ports:
            if "usbmodem" in port or "teensy" in port:
                use_port = port

        if use_port==None:
            use_port=serial_ports()[0]

    
    print("Connecting to port: {}".format(use_port))
    s=serial.Serial(use_port,
                    BAUD_RATE,
                    timeout=None,
                    bytesize=serial.EIGHTBITS,
                    xonxoff=False,
                    rtscts=False,
                    dsrdtr=False)

    return s

def receive_interrupt(signum, stack):
    read_message()

def read_message():
    global tmp_path

    # Read command
    try:
        with open(tmp_path+"ds_cmd.txt", "r") as f:
            cmd=f.read()
    except Exception as e:
        print("error:", str(e))
        return

    print("cmd:", cmd)

    # Check command
    if cmd.find('SPACEBAR')!=-1:
        global is_collecting_dataset
        is_collecting_dataset=True
        print("ds_nano33.py: Collecting training data...")
    elif cmd.find('BYE')!=-1:
        global s
        print("ds_nano33.py: BYE!")
        s.close()
        sys.exit()

    # Clear command
    with open(tmp_path+"ds_cmd.txt", "w") as f:
        f.write("")

def resync():
    global s

    res=bytearray()
    while 1:
        b=s.read(1) 
        if not b:
            raise EOFError()
        res += b
        if res.endswith(b'\xde\xad\xbe\xef'):
            break
    return res

# Read a certain number of bytes from a data stream
def readall(s, n):
    res = bytearray()
    while len(res) < n:
        chunk = s.read(n - len(res))
        if not chunk:
            raise EOFError()
        res += chunk
    return res

def read_once(s):
    global FRAME_LENGTH
    global CHANNELS
    global INSTANCES
    global tmp_path

    global tmp_frame
    global training_data
    global training_data_frame_counter
    global is_collecting_dataset

    # DVS: need to test this with multiple channels
    frame_complete=0

    try:
        # Find first end symbol, discard everything before it
        discarded=resync()
        # Get one frame of data
        # Times 2 because each data point is 2 bytes
        # Plus 2 for channel number
        #      2 for frame complete
        arr=np.frombuffer(readall(s, FRAME_LENGTH*2+4), dtype='uint16')

        # Check frame complete
        if arr[-1]==0:
            tmp_frame.append(arr)
        if arr[-1]==1:
            tmp_frame.append(arr)
            frame_complete=1
        
        if frame_complete==1 and np.shape(tmp_frame)[0]==CHANNELS:
            tmp_frame=np.asarray(tmp_frame)

            # -2 because channel number and frame complete
            # DVS: why argsort?
            tmp_frame=tmp_frame[tmp_frame[:, -2].argsort()]
            np.save(tmp_path+"tmp_frame.npy", tmp_frame)

            # SPACEBAR pressed
            if is_collecting_dataset:
                if training_data_frame_counter<INSTANCES:
                    training_data[0].append(tmp_frame)
                    training_data_frame_counter+=1
                    print("training_data_frame_counter:", training_data_frame_counter)

                # Store the data
                if training_data_frame_counter==INSTANCES:
                    training_data_frame_counter=0   # Reset counter

                    # Get label
                    with open(tmp_path+"current_label.txt", "r") as f:
                        current_label=f.read().strip()
                    # Filename
                    # cwd_path=os.getcwd()
                    training_data_file_name=tmp_path+'training_data_{}.npy'.format(current_label)

                    print('Saving Training Data to:', training_data_file_name)
                    # DVS: need to check this
                    if os.path.exists(training_data_file_name):
                        existing_training_data=np.load(training_data_file_name)
                        np.save(training_data_file_name,
                                np.append(existing_training_data, training_data, axis=0))
                    else:
                        np.save(training_data_file_name, training_data)

                    training_data=[[]]
                    is_collecting_dataset=False
                    print('Training Data SAVED!!!')

            tmp_frame=[]

    except Exception as e:
        print('ds_nano33.py:', e)
        s.close()
        sys.exit()

    return


if __name__ == '__main__':
    # For get_serial, receive_interrupt
    global s

    # For get_serial
    global BAUD_RATE

    # For receive_interrupt, get_once
    global is_collecting_dataset

    # For read_once
    global INSTANCES
    global FRAME_LENGTH
    global CHANNELS

    # For get_once
    global tmp_frame
    global training_data
    global training_data_frame_counter

    print('ds_nano33.py: Started')

    global tmp_path
    tmp_path="tmp/"
    if sys.platform.startswith('win'):
        tmp_path=os.path.join("tmp", "")

    # Write PID to file
    pidnum=os.getpid()
    with open(tmp_path+"ds_pidnum.txt", "w") as f:
        f.write(str(pidnum))

    # Clear command txt
    with open(tmp_path+"ds_cmd.txt", "w") as f:
        f.write("")

    # Read configurations
    config=configparser.ConfigParser()
    config.read('config.ini')

    INSTANCES   =int(config['GLOBAL'   ]['INSTANCES'   ])  # Number of instances recorded when spacebar is hit
    FRAME_LENGTH=int(config['GLOBAL'   ]['FRAME_LENGTH'])  # Fixed size 
    CHANNELS    =int(config['GLOBAL'   ]['CHANNELS'    ])  # Number of input channels
    BAUD_RATE   =int(config['DS_nano33']['BAUD_RATE'])

    # Shared global variables
    is_collecting_dataset      =False   # Enabled when spacebar hit
    tmp_frame                  =[]      # One frame
    training_data              =[[]]    # Store training data (multiple frames)
    training_data_frame_counter=0       #

    # List all ports
    print("All ports:")
    print(serial_ports())

    # Get a serial port
    s=get_serial()

    # Setup crtl+c catch function
    signal.signal(signal.SIGINT, receive_interrupt)

    print("ds_nano33.py: Start receive data for loop")
    while True:
        read_once(s)

    s.close()
    sys.exit()