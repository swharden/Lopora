# Installing Lopora on a Raspberry Pi

## Installing NOOBS_v2.8.2

Download from https://www.raspberrypi.org/ the NOOBS package. This will take quite a long time. 
Follow the instructions in the "software setup guide" to format your card and to install the operating system. Installation is done with the NOOBS package.

Insert the SD card into the Raspberry, connect it to the internet with an UTP cable and 5 volt power supply.

Select for the installation the first choice "Raspbian [RECOMMENDED]" and press install.

After a while, the file system will be extracted and a message will be displayed that the Operating System is installed successfully.
Press OK and the Raspberry Pi will be booted.

The country has to be selected and the software is updated. This will take quite a long time.

Open the Terminal window ("Terminal" on the Taskbar or "Menu" --> "Accesories" or "File Manager" --> "Tools") and give the following command (+ Enter of course):
 
```bash
sudo raspi-config
```

Select 1 if you really want to change the default password `raspberry` to one that you do not forget!
Select 3 to choose the boot option B4 to Desktop GUI automatically logged in as `pi` user.
Select 4 to choose Localisation Options
  Leave I1 for what it is
  I2 Change Time Zone to your time zone
  I3 Change Keyboard Layout to "Microsoft Natural" and "English (US with euro on 5)" etc. or you country + keyboard.
  I4 Wi-fi County if you have Wifi
Select 7 Advanced Options and then A1 Overscan and "Disable" the overscan so that you will have the maximum screen size on your flat screen monitor

Press "Finish" and "Reboot"

Press with your right mouse button on the taskbar at the top and select "Panel Settings" and "Position at Bottom" if you want to have the Taskbar at the bottom as with older versions of the software.

Press with your right mouse button on the taskbar and select "Add / Remove Panel Items" press "Add" and add the "CPUFreq frontend" and also "Temperature Monitor"

Change the Default view of the file manager. Otherwise you will have to wait ages till a directory with many files is displayed.
Open the file manager and select "Edit" --> "Preferences" and set the "Default view" to "Detailed list view"
And show hidden files and folders by selecting: []

If you want to make an update of the system: Open the Terminal window ("Monitor" on the Taskbar) and give the following command (+ Enter of course):

```bash
sudo apt-get update
```

If you want to have root access rights everywhere: Open the Terminal window ("Monitor" on the Taskbar) and give the following command:

```bash
sudo pcmanfm
```

or:

```bash
sudo leafpad  
```

to have Root Acces when you want to edit a script or configuration file.

Select in the Menu --> Preferences --> Recommended Software --> Geany. It is a nice "Programmers Editor" for us (Technical People) to edit bash scripts, C-programs, HTML and others Programmers files.

## Setup Python, Lopora, and Audio

Now we have to do the installation and configuration for use with Python, Lopora and Audio.

`/usr/lib/pythonX/dist-packages` is the location for external modules like numpy and pyaudio, X is the Python version number.

(The command `sudo` will give you the required rights to install the software as administrator, `apt-get install` is the command to download and install the software.)

Open the Terminal window ("Monitor" on the Taskbar) and type the next commands:

Installation of Numpy, type the following commands:

```bash
sudo apt-get install python3-numpy
```

Installation of the PIL library has been changed, type the following commands:

```bash
sudo apt-get install python3-pillow
sudo apt-get install python3-pil.imagetk
```

Installation of pyaudio type the following commands:

```bash
sudo apt-get install python3-pyaudio
```

## Extend the Audio Buffer
On the Raspberry Pi, pyAudio displays a maximum buffer value of only 262000 and that is only a few seconds. Not enough for the FTPupload. Use one of these two solutions to fix this problem.

### Option 1: Use PulseAudio

It can be solved by the installation of PulseAudio. With Pulseaudio, the maximum buffer size is 2.090.000 and we can do downsampling from 44100 S/sec to 8820 S/sec. And then we do have a buffer of almost 4 minutes, plenty of time for all the jobs.

We can use PulseAudio for the audio buffer and the downsampling of the audio stream from 44100 samples/s to 8820 samples/s.
Installation of pulseaudio and its volume control, type the following commands:

```bash
sudo apt-get install pulseaudio
sudo apt-get install pavucontrol
```

You can find the volume control in the Menu --> Sound & Video. You can also find there the selection of input the recording devices. The volume control requires much CPU power, so close it if you are finished.

If there are no significant signals or noise from your receiver above 4410 Hz (half the sample rate), then we are finished yet with PulseAudio.
But it is better to change the resample method, less aliasing (no interference from signals above 4410 Hz or half the sample rate) and better performance:

Open the File Manager at the bottom taskbar (somewhere at the left side).
Go to the folder /etc/pulse/ and do at the taskbar "Tools" --> "OpenCurrent Folder in Terminal" and type "sudo leafpad" to open the text editor Leafpad with Root privileges.
Open the configuration file "daemon.conf" with the text editor Leafpad and find the line:

```conf
;resample-method = speex-float-1
```

and change it to:

```conf
resample-method = speex-float-3 (remove the semicolon!)
```

Then reboot to cause changes to take effect.

### Option 2: Use Default Sample Rate

Use the default sample rate of 44100 samples/sec and an FFT sample array of 131072 and set the FTP upload in the configuration file to "2" EXTERNAL upload.

When you start Lopora, also start the program `LOPEXTftp-v1a.py`. 

Every 30 seconds, this program checks if the file `FTPuploads.txt` with the file names to be uploaded exists. If yes, it does the FTP upload an deletes the file `FTPuploads.txt` afterwards.

## Run Lopora

DO NOT COPY ANY OF THE SCRIPTFILES FROM THIS ZIP FILE, TYPE THEM OVER!!!

Make a new folder `/home/pi/lopora` and save all the (unzipped) files in this ZIP file into this directory. Use an USB memory stick to transfer the files.

Make two extra folders `home/pi/lopora/savemap` and `home/pi/lopora/workmap`

On your Menu at the Taskbar under Programming  you will find the "Python 3 (IDLE)" and you can open and modify the Lopora program with it. But all normal settings are done in the configuration file. Modify the settings in the example configuration file `lopora-V5.cfg` and copy it with a name like `grabber30meter.cfg`. When Lopora starts, it loads the default configuration `lopora-V5.cfg`.

Do not start Lopora when opened with IDLE by selecting `run module`, that gives problems after running a few days!
Open the Folder lopora in a Terminal and type `python3 LOPORA-vxx.py` (xx is the version number).
And also `python3 LOPEXTftp-v1a.py` if you have chosen the external upload solution 2.
But it is also possible to have the scriptfile with the name `startlopora.sh` on your Desktop, you can find it in the ZIP file.

Make it executable (click the file with the right mouse button, select "Properties" --> "Permissions" --> "Execute" and set it to "Anyone"). And of course you have to modify the script file a little depending on your Directory and program names.

We will use the Raspberry Pi 2B in "normal" mode without Overclock and a sample rate of the audio stream of 8820 samples/sec.

## Automatically Start Lopora on Boot

Autostart in Desktop mode is easy! Lopora starts here automatically after a power failure!

Open with the File Manager the folder `/home/pi/.config` (Activate in the File Manager: View: Show Hidden!)

Make a new directory (folder) `autostart` and make a desktop file in this directory `/home/pi/.config/autostart`

The name of the Desktop file is `lopora.desktop` and you can find it in the ZIP file.

But it takes approximately 2 minutes to start Lopora with this script file due to the following reasons:

My Raspberry Pi starts much faster than my Internet modem. And when the modem is not rebooted, it cannot get the right time via the time server and does start to run with a wrong time. So in the script file, there is a long pause to give the Internet modem enough time to reboot. Then the Raspberry Pi will start with the correct time, obtained from a Time Server.

In my case, the scriptfile `startlopora.sh` is located on the Desktop and is called. Of course you have to modify the Exec=.. so that it runs your scriptfile.

Make the Desktopfile `lopora.desktop` executable (click the file with the right mouse button, select "Properties" --> "Permissions" --> "Execute" and set it to "Anyone") and when the Raspberry Pi reboots, Lopora will start after the mentioned 2 minutes. Just wait, it looks as if nothing happens.

## Misc

And I did something that everybody does once and could not change the desktop background anymore. 
When right-clicking the desktop, I selected under Desktop Preferences - Advanced the "Show menus provided by window managers when desktop is clicked". From that moment, I had a strange menu when right clicking the desktop and could not change the Desktop Appearance anymore... Is a problem when you want to have a black desktop background. Was solved as follows:

Launch a terminal and enter `pcmanfm --desktop-pref`. 
When the desktop preferences window pops up, click on the "Advanced" tab and deselect "Show menus provided by window managers when desktop is clicked".

Copying the grabber pictures can be done with an USB stick. Enough USB ports on the Raspberry Pi 2B. 

Only with special software, it is possible to read the SD card in a Windows PC. More can be found on the internet. Also about how to make an image of your SD card.