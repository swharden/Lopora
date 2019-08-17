# Installing Linux and Lopora

### Set up Linux Mint

Download the ISO file from https://www.linuxmint.com/

Burn it to a bootable USB stick (with Rufus or see the description on the site).
Insert the USB stick into the PC and find "Advanced Setup" and restart from the bootable USB stick.
It boots with Linux and select "Install Linux Mint"

User: `onno` Password: `pa2ohh `

Open the Software Manager:
Python3.6 is already installed, also with the name python3:
Installation of Numpy, pil.imagetk and pyaudio, type the following commands in the Software Manager in the Search window:

python3 numpy           and install it
python3 pil.imagetk     and install it (PIL is already installed)
python3 pyaudio         and install it

Installation of Python's integrated Developement and Learning Environment (Idle), 
type the following commands in the Software Manager in the Search window:

python3.6 idle          and install it.
 
You can find Idle in the Menu --> Programming

If there are no significant signals or noise from your receiver above 4410 Hz (half the sample rate), then we are finished. But it is better to change the resample method, less aliasing (no interference from signals above 4410 Hz or half the sample rate) and better performance:

Open the File Manager at the bottom taskbar (somewhere at the left side).
Go to the folder `/etc/pulse/` and click the right mouse key and select "Open as Root".
Open the configuration file `daemon.conf` with the text editor and find the line:

```conf
;resample-method = speex-float-1
```

and change it to:

```conf
resample-method = speex-float-3 (remove the semicolon!)
```

Then reboot to cause changes to take effect.

### Set up Lopora

Make a new folder `/home/python/lopora` and save all the (unzipped) files in this ZIP file into this directory. Use an USB memory stick to transfer the files.

Make two extra folders `home/python/lopora/savemap` and `home/python/lopora/workmap`

On your Menu at the Taskbar under Programming you will find the "Python 3 (IDLE)" and you can open and modify the Lopora program with it. But all normal settings are done in the configuration file. Modify the settings in the example configuration file `lopora-V5.cfg` and copy it with a name like `grabber30meter.cfg`. When Lopora starts, it loads the default configuration `lopora-V5.cfg`.

You can start Lopora when opened with IDLE by selecting "run module". Or open the Folder lopora in a Terminal and type `python3 LOPORA-vxx.py` (xx is the version number).

But it is also possible to have the scriptfile with the name `startlopora.sh` on your Desktop, you can find it in the ZIP file.

Make it executable (click the file with the right mouse button, select "Properties" --> "Permissions" --> "Execute" and set it to "Anyone"). And of course you have to modify the script file a little depending on your Directory and program names.











