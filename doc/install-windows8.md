# Install Lopora on Windows
_This guide was written with Windows 8 in mind_

## Install Python
I use Python3.6, because there was an error message when I installed pyaudio with Python 3.7: Microsoft Visual C++ is required. The given link did not work anymore. And the version from https://visualstudio.microsoft.com/thank-you-for-downloading-visual-studio/ geve the same error message again.

* Go to: https://www.python.org/downloads/windows
* Download Windows x86 executable installer and Run it.
* IMPORTANT: Select "Add Python 3.6 to PATH"
* Then select "Install Now"

Python is installed in c:users/onno1/AppData/Local/Programs/Python/Python36-32

Installation is done with `pip` as follows. 
(The message when I used pip the first time: Upgrade pip and I did that as was explained in the same message.)

Open a terminal screen (Menu --> Windows System --> Command Prompt)

```bash
pip install numpy
pip install pillow
pip install pyaudio
```

## Install Lopora

Make a new folder `Documents/lopora` and save all the (unzipped) files in this ZIP file into this directory.

Make two extra folders `Documents/lopora/savemap` and `./lopora/workmap`

On your Menu at the Taskbar under Programming  you will find the "Python 3 (IDLE)" and you can open and modify the Lopora program with it. But all normal settings are done in the configuration file. Modify the settings in the example configuration file `lopora-V5.cfg` and copy it with a name like `grabber30meter.cfg`. When Lopora starts, it loads the default configuration `lopora-V5.cfg`.

You can start Lopora when opened with IDLE by selecting "run module".
Or:
* Open the folder with Lopora with the Windows Explorer.
* Select in the Windows Explorer --> File --> Open command prompt
* Type: `python LOPORA-v5a.py`












