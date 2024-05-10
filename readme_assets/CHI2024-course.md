We expect the conference WiFi to be slow (and we have a limited number of loaner laptops with preinstalled Arduino and T4Train), so we highly recommend downloading and installing the prerequisite software before the start of the course. Please feel free to reach out if you have any questions.


1) Install Anaconda as your python distribution.
Anaconda Links:
[Anaconda3-2022.10-Windows-x86_64 (Windows)](https://repo.anaconda.com/archive/Anaconda3-2022.10-Windows-x86_64.exe)
[Anaconda3-2022.10-Linux-x86_64 (Linux x86-64)](https://repo.anaconda.com/archive/Anaconda3-2022.10-Linux-x86_64.sh)
[Anaconda3-2022.10-MacOSX-x86_64 (Mac Intel)](https://repo.anaconda.com/archive/Anaconda3-2022.10-MacOSX-x86_64.pkg)
[Anaconda3-2022.10-MacOSX-arm64 (Mac M1/M2/M3)](https://repo.anaconda.com/archive/Anaconda3-2022.10-MacOSX-arm64.pkg)
While T4Train can run on other Python 3.9 distributions, our setup.py file assumes the above Anaconda release. More information can be found in the T4Train Setup information below.

2) Clone the T4Train repo and follow T4Train Setup directions to install required packages.
T4Train GitHub Repo:
https://github.com/ISC-Lab/T4Train
[T4Train Setup Information](https://github.com/ISC-Lab/T4Train/blob/master/readme_assets/setup-README.md)
If you run into any issues running "setup.py" after installing the above release of Anaconda, feel free to reach out. For Mac M1/M2/M3 users, there is a separate set of directions.

3) Install Arduino IDE, Nano 33 Sense Board, and Nano 33 Sense Libraries
Arduino Links:
[arduino-ide_2.3.2_Windows_64bit](https://downloads.arduino.cc/arduino-ide/arduino-ide_2.3.2_Windows_64bit.exe)
[arduino-ide_2.3.2_Linux_64bit](https://downloads.arduino.cc/arduino-ide/arduino-ide_2.3.2_Linux_64bit.AppImage)
[arduino-ide_2.3.2_macOS_64bit (Mac Intel)](https://downloads.arduino.cc/arduino-ide/arduino-ide_2.3.2_macOS_64bit.dmg)
[arduino-ide_2.3.2_macOS_arm64 (Mac M1/M2/M3)](https://downloads.arduino.cc/arduino-ide/arduino-ide_2.3.2_macOS_arm64.dmg)

After installing Arduino IDE, please go into the Boards Manager (`Tools->Board->Boards Manager`) and install `Arduino Mbed OS Nano Boards`. Then, please go into `Tools->Manage Libraries...` and install `Arduino_ScienceJournal` which should install all of the libraries for the Nano 33 Sense.