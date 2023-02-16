# T4Train Setup

## Contents

- [Requirements](#requirements)
	- [Windows](#windows-users)
	- [MacOS & Linux](#maclinux-users)
- [Setup](#setup)
	- [Setting up a virtual environment](#setting-up-a-virtual-environment)
	- [Installing dependencies](#dependencies)
- [Troubleshooting](#troubleshooting)
- [Appendix for pure venv-based install](#appendix-for-pure-venv-based-install)


## Requirements

T4Train requires Python 3.8 or 3.9.
[Anaconda](https://www.anaconda.com/distribution/) or
[Miniconda](https://docs.conda.io/en/latest/miniconda.html) is strongly
recommended as your Python environment for environment and package management to
make setup easier. It includes several of the packages needed for T4Train. 

This repo has confirmed compatibility with the Anaconda3-2022.10 (Python 3.9) release.

If you do not install conda for Python, T4Train may still work, but package
installation could be more difficult.

Mac users will need [Homebrew](https://brew.sh/) installed to install
[portaudio](https://formulae.brew.sh/formula/portaudio), which is required to
pip install pyaudio. Apple silicon Macs are not officially supported (yet!)

#### Windows Users

Once installed, verify Anaconda is your Python interpreter by opening Anaconda
Prompt from the Start Menu and entering:
    
    where python

It should respond with something like:

    C:\Users\[user]\AppData\Local\Continuum\anaconda3\python.exe

#### Mac/Linux Users

Once installed, verify that your terminal is using Anaconda by entering:
    
    which python

It should respond with something like:

    /home/[user]/anaconda3/bin/python

After you've verified that Anaconda is being used as your python environment,
set up your [virtual environment](#setting-up-a-virtual-environment).

## Setup

### Setting Up a Virtual Environment

We strongly recommend setting up a conda virtual environment to avoid clashing
with your current environment and making setup easier. If you insist on using
Python's vanilla venv, try following
[appendix for pure venv-based install](#appendix-for-pure-venv-based-install).

If using Anaconda, update your environment before installing dependencies with:

    $ conda update -n base conda
    $ conda update -n base --all

Navigate to the T4Train directory in Terminal or Anaconda Prompt and create an
environment with a name such as "t4train-env" and activate it:

	$ conda create -n <name-of-the-env> python=3.9
	$ conda activate <name-of-the-env>

Press y to proceed.

To leave the environment after you no longer need it:

	$ conda deactivate

After you have created your virtual environment, install the [dependencies](#Dependencies).

## Dependencies

All of the dependencies are listed in `requirements.txt`. To reduce the
likelihood of environment errors, install the dependencies inside a virtual
environment with the following steps.

Navigate to the T4Train directory **and activate the virtual environment in your
terminal**. Run the following commands in terminal:

	$ python setup.py

All of the T4Train dependencies should now be installed.

## Troubleshooting

### Pyaudio did not install properly

#### Windows Users

`cd` to the T4Train root folder run the following command **inside a conda
 or vanilla Python virtual environment**:

    $ pip install --force-reinstall readme_assets\PyAudio-0.2.11-cp39-cp39-win_amd64.whl 

#### Linux Users

If you are using Ubuntu or other Debian-based distro, run the follow command in
terminal:

    $ sudo apt-get install libportaudio2 portaudio19-dev

For other Linux distros, search for portaudio in your distro's package
repository and install the corresponding packages.

Then **activate your virtual environment** and install Pyaudio:

    $ pip install pyaudio

## Appendix for pure venv-based install

**Use pure venv-based install is only likely to work when you are using Python
3.9.** Even if your system is bundled with Python 3.9, it is still recommended
to use conda to create a separate environment with an independent Python
interpreter other than your system's Python interpreter.

After creating an venv using the methods below, go back to the
[Dependencies](#dependencies) section to install the dependencies.

### Windows Users

Without Anaconda, you can get up a virtual environment in the T4Train directory
in Command Prompt or Powershell like this:

    $ python -m venv <name-of-the-env>

To activate the virtual environment:

    $ .\<name-of-the-env>\Scripts\activate

To confirm you're in the virtual environment, check the location of your Python
interpreter.

    $ where python
    ...\<name-of-the-env>\bin\python.exe

To leave the environment after you no longer need it:

	$ deactivate

### Mac/Linux Users

Without Anaconda, you can get up a virtual environment in the T4Train directory
in terminal like this:

    $ python3 -m venv <name-of-the-env>

To activate the virtual environment:

    $ source <name-of-the-env>/bin/activate

To confirm you're in the virtual environment, check the location of your Python interpreter.

    $ which python
    .../<name-of-the-env>/bin/python

To leave the environment after you no longer need it:

	$ deactivate
