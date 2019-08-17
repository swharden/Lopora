
# Lopora Instructions

* Install Python and the modules
  * [Installation instructions for Windows](install-windows8.md)
  * [Installation instructions for Raspberry Pi](install-raspi.md)
  * [Installation instructions for Linux Mint](install-linux.md)
* Make a new folder `/home/python/lopora` and extract [source files](/src/) into it
* Make a new folder `/home/python/lopora/savemap` 
* Make a new folder `/home/python/lopora/workmap`

> **Customizing settings:** On your Menu at the Taskbar under Programming you will find the "Python 3 (IDLE)" and you can open and modify the Lopora program with it. But all normal settings are done in the configuration file. Modify the settings in the example configuration file `lopora-V5.cfg` and copy it with a name like `grabber30meter.cfg`. When Lopora starts, it loads the default configuration `lopora-V5.cfg`.

* Start Lopora and you will see the screen filled with the QRSS signals. Information is printed in the Terminal screen.
* Do not start Lopora when opened with IDLE by selecting "run module", that gives problems after running a few days!
* Open the Folder with lopora in a Terminal and type `python3 LOPORA-vxx.py` (xx is the version number).
* And also `python3 LOPEXTftp-v1a.py` if you have chosen the external upload solution 2. This program checks every 30 seconds if an upload is required.

## Configuration

**Station Name:**
The 2nd line in the configuration file is the Station name and information about the station

**FTP uploads:**
In this section you can select what you want to upload to the FTP site

**Storage:**
In this section you can select what you want to save

**Parameters:**
Configuration of the parameters.
The TUNED frequency has to be lower than the START frequency and the START frequency lower than the STOP frequency

**File Names:**
Configure the file names of the pictures without .jpg or without .png. The extensions will be added automatically

**FTP Settings:**
The FTP settings, needed to upload files

**Special Settings:**
With the FTP delay you can set a delay in seconds after the end of the scan when the FTP upload will start. It is intended to prevent that more grabbers are uploading at the same moment.

**Hour Lines:**
The last setting is for the hour lines. Many points are combined to one point for the hour grab. You can select here if the combination of points should be a maximum of the points, an average of the points of a minimum

**Settings in Python:** use IDLE to set these options.
* Fixed file names
* screen settings and colors:
  * The width and height of the screen and borders used for text can be modified and also the colors.
  * When you use a small monitor, you can give `CANVASheight` and `CANVASwidth` a value and you can use the scrollbars to see the whole picture. Otherwise the canvas will be the same size as the picture.

## Buttons

**Compression:**
Strong signals are more or less compressed and weak signals just the opposite, more or less enhanced.

**Contrast / Brightness:**
To adjust the Contrast and Brightness.

**Noise Blanker:**
For suppressing interference peaks from electric fences.

**Select Screen:**
The next of the four screens is selected: 1=normal grab, 2=hour grab, 3=daily grab, 4=ten minute grab used for stacking.

**PrintOnOff:**
Normally, information like audio level, filled buffer, contrast and brightness settings, FTP uploads,is printed to the Terminal screen.
But sometimes you want to check this Terminal screen without that new information is printed.
With this button, you can disable or enable the printing to the Terminal screen.

**Calibrate:**
When the calibration signal of my GPS receiver is shown on the display, I can adjust the TUNE frequency till the signal is displayed at the correct frequency. Calibration is only possible if the displayed frequency range is within the FFT range.

**Audio device:**
Select the audio device to be used.

Save setting / Load setting:
The coniguration can be saved or loaded. During start-up, the configuration "lopora-V5.cfg" will be loaded.

**FTP Status:**
The FTP upload can be disabled, enabled or set to External Upload required. When an External Upload is required, the filenames and FTP parameters
are stored in "FTPuploads.txt". A second FTP upload program can read this file and do the FTP upload while Lopora continues.

**Go Offline:**
The text "OFFLINE" is added to the picture, the picture is uploaded to the FTP site and Lopora stopped.