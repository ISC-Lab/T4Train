#!/usr/bin/env python3
# ============================================================================
""" 
setup.py is a file for the first set of setting up T4Train and is dependencies.
It upgrades pip and then installs PyAudio for Windows. PyAudio is installed in
requirements.txt for MacOS & Linux.
"""
# ============================================================================


import os
from sys import platform


if platform == 'darwin':
    conda_version = os.popen("conda --version").read().split(' ')[1].split(".")[0]
    if conda_version == "23":
        print('Good job, you have conda correctly installed!\n')
    else:
        print("Install conda per the instructions.")
        exit()
    brew_version = os.popen("brew --version").read().split(' ')[1].split('\n')[0].split('.')
    if brew_version[0]=="3" and brew_version[1]=="6":
        print("Good job, you have brew correctly installed!\n") 

        print("Installing portaudio \n")
        os.system("brew install portaudio")
    else:
        print("Install brew per the instructions")
        exit()

    print("Upgrading pip\n")
    os.system("pip install --upgrade pip")
    print("Instaling requirements")
    os.system("pip install --upgrade --force-reinstall -r requirements.txt")
    print("Installing pyaudio separately for Macs")
    os.system("pip install --upgrade --force-reinstall pyaudio")

if platform.startswith('win'):
    os.system("echo You are using Windows, WHY?? WHHHHYYYYYY????")
    print("Upgrading pip\n")
    os.system("pip install --upgrade pip")
    print("Instaling requirements")
    os.system("pip install --upgrade --force-reinstall -r requirements.txt")
    print("Installing pyaudio separately for Windows")
    os.system("pip install --user readme_assets\PyAudio-0.2.11-cp39-cp39-win_amd64.whl")

if platform.startswith('linux'):
    os.system("echo You are using Linux, GOOD BOIII!!!")
    conda_version = os.popen("conda --version").read().split(' ')[1].split(".")[0]
    if conda_version == "23":
        print('Good job, you have conda correctly installed!\n')
    else:
        print("Install conda per the instructions.")
        exit()

    print("Upgrading pip\n")
    os.system("pip install --upgrade pip")
    print("Instaling requirements")
    os.system("pip install --upgrade --force-reinstall -r requirements.txt")
    print("Installing pyaudio separately for Linux")
    os.system("pip install --upgrade --force-reinstall pyaudio")
    
# upgrading pip
# os.system("python -m pip install --user --upgrade pip")
# os.system("pip install --user -r requirements.txt")

# os.system("echo ~")
# os.system("echo ~")
# os.system("echo ~")
# os.system("echo ~")
# os.system("echo ~")
# os.system("echo = = = = = = = = = = = = = = = = = = = = = = =")
# os.system("echo Installing pyaudio...")
# if platform == "win32":
#     os.system("echo You are using Windows, WHY?? WHHHHYYYYYY????")
#     os.system("pip install --user readme_assets\PyAudio-0.2.11-cp39-cp39-win_amd64.whl")
# else:
#     os.system("echo You are using Linux, GOOD BOIII!!!")
#     os.system("pip install --user pyaudio")
# os.system("echo = = = = = = = = = = = = = = = = = = = = = = =")
