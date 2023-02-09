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

# upgrading pip
os.system("python -m pip install --user --upgrade pip")
os.system("pip install --user -r requirements.txt")

os.system("echo ~")
os.system("echo ~")
os.system("echo ~")
os.system("echo ~")
os.system("echo ~")
os.system("echo = = = = = = = = = = = = = = = = = = = = = = =")
os.system("echo Installing pyaudio...")
if platform == "win32":
    os.system("echo You are using Windows, WHY?? WHHHHYYYYYY????")
    os.system("pip install --user readme_assets\PyAudio-0.2.11-cp39-cp39-win_amd64.whl")
else:
    os.system("echo You are using Linux, GOOD BOIII!!!")
    os.system("pip install --user pyaudio")
os.system("echo = = = = = = = = = = = = = = = = = = = = = = =")
