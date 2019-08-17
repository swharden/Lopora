# LOPORA-v5a.py(w) (02-11-2018)
# For reception of LOw POwer RAdio signals or QRSS signals
# For Python version 3
# With external module pyaudio; PIL library module; NUMPY module
# Made by Onno Hoekstra (pa2ohh)

import pyaudio
import wave
import sys
import os
import math
import time
import wave
import struct

import ftplib
import numpy.fft

from time import gmtime, strftime

from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog


############################################################################################################################################

# ===== FIXED FILE NAMES USED IN LOPORA CAN BE MODIFIED HERE =====
DEFAULTcfg = "lopora-v5"    # Filename of default configuration
STOREmap = "./savemap/"     # Make this folder to save the pictures
WORKmap = "./workmap/"      # Make this folder for work files 

############################################################################################################################################

# ===== SCREEN SETTINGS AND COLORS CAN BE MODIFIED HERE =====
GRDw = 1050                 # Width of the grid (900-1050-1200 integer of DISPLAYtime 20 and 30)
GRDh = 600                  # Height of the grid
TXTn = 10                   # Space North used for black border
TXTw = 10                   # Space West used for black border
TXTs = 80                   # Space South for time markers and information
TXTe = 60                   # Space East for frequency markers

Buttonwidth = 15            # With of the buttons

CANVASheight = 0            # [DEFAULT=0] The canvas height. Set to 500 for small screens 0=automatically sized
CANVASwidth = 0             # [DEFAULT=0] The canvas width. Set to 600 for small screens 0=automatically sized

COLORframes = "#000080"     # Color = "#rrggbb" rr=red gg=green bb=blue, Hexadecimal values 00 - ff
COLORcanvas = "#000000"     # Background color of the canvas
COLORtext = "#ffffff"       # Text color

############################################################################################################################################

# ===== DEFAULT VALUES THAT DO NOT NEED TO BE MODIFIED =====
FFTwindow = 3               # [DEFAULT=3] FFTwindow: 0=None (rectangular B=1), 1=Cosine (B=1.24), 2=Triangular non-zero endpoints (B=1.33),
                            # 3=Hann (B=1.5), 4=Blackman (B=1.73), 5=Nuttall (B=2.02), 6=Flat top (B=3.77)
IMGformat = 90              # [DEFAULT=90] 0=PNG format, >0=JPEG quality (60-100%)

############################################################################################################################################

# Fixed variables
PABUFFER = 4180000          # Windows=11520000 No Problem, RASPImax: 4180000 Buffer time: (PABUFFER/samplerate/2)sec (2x8 bits)
ZEROpadding = 2             # [DEFAULT=2] Zero padding (2,4,8 power of 2) for extra FFT points

############################################################################################################################################

# Settings that can be stored and modified in a configuration file and are overwritten by the start configuration file "lopora-v5.cfg"

#===== LOPORA CONFIGURATION FILE - STATION NAME FIRST =====
STATIONname = "QTH and Station name plus remarks"

#===== CONFIGURE FTP uploads =====
DOFTP = 2                   # Set to 1 to upload to the FTP site. Set to 2 for EXTERNAL upload
DOFTParchGRABS = 1          # Set to 1 to upload the archive grabs (hf1-0.jpg to hf1-71.jpg)
DOFTPstackAV = 1            # Set to 1 to upload the average stacking grabs (mf1.jpg)
DOFTParchAV = 1             # Set to 1 to upload the average stacking grabs archive (mf1-0.jpg to mf1-71.jpg)
DOFTPstackPK = 1            # Set to 1 to upload the peak stacking grabs (lf1.jpg)
DOFTParchPK = 1             # Set to 1 to upload the peak stacking grabs archive (lf1-0.jpg to lf1-71.jpg)
DOFTPhour = 1               # Set to 1 to upload the hour grabs (vhf1.jpg)
DOFTParchHR = 1             # Set to 1 to upload the hour grabs archive (vhf1-0.jpg to vhf1-2.jpg)
DOFTPdaily = 1              # Set to 1 to upload the daily grab (uhf1.jpg)
DOFTParchDY = 1             # Set to 1 to upload the daily grabs archive (uhf1-1.jpg to uhf1-31.jpg)             

#===== CONFIGURE STORAGE =====
SAVEgrabs = 1               # Set to 1 to save the grabs to the storage (hf1-date.jpg)
SAVEgrabsAV = 0             # Set to 1 to save the average grabs to the storage (mf1-date.jpg)
SAVEgrabsPK = 0             # Set to 1 to save the peak grabs to the storage (lf1-date.jpg)
SAVEgrabsHR = 0             # Set to 1 to save the hour grabs to the storage (vhf1-date.jpg)
SAVEgrabsDY = 0             # Set to 1 to save the daily grabs to the storage (uhf1-date.jpg)

#===== CONFIGURE PARAMETERS =====
STARTfrequency = 10139800.0 # Start frequency at the bottom of screen in Hz
STOPfrequency = 10140110.0  # Stop frequency at the top of screen in Hz 
TUNEDfrequency = 10138500.0 # Tuning frequency of the receiver in Hz

AUDIOdevin = -1             # [DEFAULT=None] audio device for input, set to -1 for asking

STACKING = 6                # Stacking of n pictures
STACKING10m = 1             # Set to 1 to activate 10 minute grabs for 20 and 30 minutes display time only

DISPLAYtime = int(20)       # [Default=20] for 20 minutes, but can be changed to 10 or 30 for normal operation

MARKERfs = 20               # Marker frequency step (Hz per div)
MARKERts = 1                # Marker time step at every N minutes

SAMPLErate = 8820           # [DEFAULT=8820 or 44100 if no downsampling] Sample rate of audio stream (44100/5)
SMPfft = 32768              # [DEFAULT=32768 or 131072 if no downsampling] Number of FFT samples

Contrast = 10               # Contrast (0 to 25) is Power of sqrt(2)
Brightness = 0              # Brightness (-10 to + 10) is Power of 2
DISPLAY = 2                 # Display compression factor 0 - 3

NOISEblankerlevel = 0       # Noise blanker level (0 to 5, 0 is off)

#===== CONFIGURE FILE NAMES =====
FILEname = "hf1"            # The file name of the picture
FILEnameav = "mf1"          # The file name of the averaged stacked picture
FILEnamepk = "lf1"          # The file name of the peak stacked picture
FILEnamehour = "vhf1"       # The file name of the hour grabs
FILEnameday = "uhf1"        # The file name of the daily grabs

#===== CONFIGURE FTP SETTINGS =====
FTPhost = "ftp.qsl.net"     # FTP host
FTPuser = "pa2ohh"          # FTP user
FTPdir = "./test"           # FTP remote directory
FTPpassword = "password"    # FTP password

# ===== CONFIGURE SPECIAL SETTINGS =====
FTPdelay = 0                # [DEFAULT=0] Delay (s) to avoid FTP upload collisions
HOURgrab = 8                # [DEFAULT=8] Hour grab time. Can be 2, 4, 6, 8 or 12 hours
ADDhourlines = 1            # [DEFAULT=1] 1=Take max of n FFT scans for hour grabs, 0=Take average, -1=Take minimum

############################################################################################################################################

# Initialisation of global variables required in various routines (DO NOT MODIFY THEM!)
ARCHIVEnumber = 0                       # The number of the current archive file
ARCHIVEsize = 72                        # The size of the archive

AUDIObuffer = 0                         # The maximum of the buffer value of PAaudio
AUDIOlevel = 0.0                        # Level of audio input 0 to 1
AUDIOlevelmax = 0.0                     # The maximum audio input level

AUDIOsignal1 = []                       # Audio trace channel

if CANVASheight == 0:
    CANVASheight = GRDh + TXTn + TXTs   # The canvas height calculated if != 0
if CANVASwidth == 0:
    CANVASwidth = GRDw + TXTw + TXTe    # The canvas width calculated if != 0

COMBf = 1.0                             # Combine vertical frequency pixels

DISPLAYred = numpy.ones(1001)           # The red display curve
DISPLAYgreen = numpy.ones(1001)         # The green display curve
DISPLAYblue = numpy.ones(1001)          # The blue display curve

FFTline = -1                            # Display line of the screen (-1 means undefined)
FFTlineHR = -1
FFTlineDY = -1

FFTbandwidth = 0                        # The FFT bandwidth
FFTresult = []                          # FFT result
FFTresultHR = []                        # FFT result for hour scan
FFTresultDY = []                        # FFT result for daily scan

FFTwindowname = "--"                    # The FFT window name
FFTwindowshape = numpy.ones(SMPfft)     # The FFT window curve

FTPfiles = []                           # The list with FTPfiles

FTPflag = False                         # FTP upload required when True

GRABlinesHR = 1                         # Grab lines together for hour grabs
GRABlinesHRcnt = 0                      # Counter for hour line grabbing function

GRABlinesDY = 1                         # Grab lines together for day grabs
GRABlinesDYcnt = 0                      # Counter for day line grabbing function

NOISEblankeractive = False              # Noise blanker has not detected any spikes yet

PA = pyaudio.PyAudio()
PAFORMAT = pyaudio.paInt16              # Audio format 16 levels

PrintTenabled = True                    # Print to terminal if True

RUNstatus = 0                           # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart
DATAbuffer = 0.0                        # Data contained in input buffer in %
DATAbuffermax = 0.0                     # The maximum value

SAVEsettings = False                    # Save settings after a change
SCREENnr = 1                            # Screen number 1, 2, 3 or 4
SMPfftpwrTwo = 1.0                      # The nearest higher power of two of SMPfft
SMPfftstep=int(1) 
STARTsample = 0                         # The start sample used for the display, be calculated on initialize
STOPsample = 0                          # The stop sample used for the display, be calculated on initialize

Tbuffer = time.time()                   # The time that the buffer is read from the audio device (epoch time in seconds, float)
Tsynch = time.time()                    # Start of the synchronisation period
TsynchHR = time.time()                  # Start of the hour synchronisation period
TsynchDY = time.time()                  # Start of the daily synchronisation period
Tstamp = Tsynch                         # Time stamp for names of files


############################################################################################################################################

# =================================== Start widgets routines ========================================
def BNot():
    print("Routine not made yet")


def BCompression():
    global DISPLAY
    global SAVEsettings
    
    DISPLAY = DISPLAY + 1
    if DISPLAY > 3:
        DISPLAY = 0

    CALCDISPLAYshape()          # Make the DISPLAY shapes for the display colors
    SAVEsettings = True
    PrintInfo()                 # Process info


def BContrast1():
    global Contrast
    global SAVEsettings

    Contrast = Contrast - 1
    if (Contrast < 0):
        Contrast = 0

    SAVEsettings = True
    PrintInfo()                 # Process info


def BContrast2():
    global Contrast
    global SAVEsettings
    
    Contrast = Contrast + 1
    if (Contrast > 25):
        Contrast = 25

    SAVEsettings = True
    PrintInfo()                 # Process info


def BBrightness1():
    global Brightness
    global SAVEsettings
    
    Brightness = Brightness - 1
    if (Brightness < -10):
        Brightness = -10

    CALCDISPLAYshape()          # Make the DISPLAY shapes for the display colors
    SAVEsettings = True
    PrintInfo()                 # Process info


def BBrightness2():
    global Brightness
    global SAVEsettings
    
    Brightness = Brightness + 1
    if (Brightness > 10):
        Brightness = 10

    CALCDISPLAYshape()          # Make the DISPLAY shapes for the display colors
    SAVEsettings = True
    PrintInfo()                 # Process info


def BNBlevel1():
    global NOISEblankerlevel
    global SAVEsettings
    
    NOISEblankerlevel = NOISEblankerlevel - 1
    if (NOISEblankerlevel < 0):
        NOISEblankerlevel = 0
    SAVEsettings = True
    PrintInfo()                 # Process info


def BNBlevel2():
    global NOISEblankerlevel
    global SAVEsettings
    
    NOISEblankerlevel = NOISEblankerlevel + 1
    if (NOISEblankerlevel > 5):
        NOISEblankerlevel = 5
    SAVEsettings = True
    PrintInfo()                 # Process info


def BCalibrate1():
    global TUNEDfrequency
    global SAVEsettings

    TUNEDfrequency = TUNEDfrequency + 0.5

    if STARTfrequency < TUNEDfrequency:
        TUNEDfrequency = TUNEDfrequency - 0.5                   # Reset to old value if outside FFT range
        print("ERROR: CALIBRATION not possible, START frequency lower than TUNED frequency")
        return()

    CALCsrange()
    
    SAVEsettings = True
    PrintInfo()                 # Process info


def BCalibrate2():
    global TUNEDfrequency
    global SAVEsettings
    
    TUNEDfrequency = TUNEDfrequency - 0.5

    if STOPfrequency > (TUNEDfrequency + SAMPLErate / 2 - 1):
        TUNEDfrequency = TUNEDfrequency + 0.5                   # Reset to old value if outside FFT range
        print("ERROR: CALIBRATION not possible, STOP frequency too high")
        return()

    CALCsrange()
    
    SAVEsettings = True
    PrintInfo()                 # Process info


def BScreenselect():
    global SCREENnr

    SCREENnr = SCREENnr + 1
    if SCREENnr > 4:
        SCREENnr = 1

    SCREENrefresh()
    

def BPrintTcontrol():
    global PrintTenabled

    if PrintTenabled == True:
        PrintInfo()
        PrintT(" == PRINTING TO TERMINAL INACTIVE ==")
        PrintTenabled = False
    else:
        PrintTenabled = True
        PrintT(" == PRINTING TO TERMINAL ACTIVATED ==")
        PrintInfo()                 # Process info

   
def BAudiodevice():
    global RUNstatus
    global AUDIOdevin

    old = AUDIOdevin

    SELECTaudiodevice()         # Select an audio device

    if old !=  AUDIOdevin:      # Restart if other audio device
        if (RUNstatus != 0):    # Stop the scan
            RUNstatus = 3
            AUDIOin()

    STARTshow()                 # Start the show


def BSave():
    global RUNstatus 
        
    filename = filedialog.asksaveasfilename(filetypes=[("Setting","*.cfg"),("allfiles","*")])

    if (filename == None):              # No input, cancel pressed or an error
        filename = ""

    if (filename == ""):
        return()
    if filename[-4:] != ".cfg":
        filename = filename + ".cfg"
    Saveconfig(filename)                # Save the settings


def BRecall():
    global RUNstatus 

    filename = filedialog.askopenfilename(filetypes=[("Setting","*.cfg"),("allfiles","*")])

    if (filename == None):              # No input, cancel pressed or an error
        filename = ""

    if (filename == ""):
        return()
  
    if (RUNstatus != 0):                # Stop the scan if running
        RUNstatus = 3
        AUDIOin()

    Recallconfig(filename)              # Load configuration
    SaveDefault()                       # Save configuration also as default that will be reloaded when the program starts

    STARTshow()


def BFTPstatus():
    global DOFTP
    global SAVEsettings
    
    DOFTP = DOFTP + 1
    if DOFTP > 2:
        DOFTP = 0

    SAVEsettings = True
    PrintInfo()                         # Process info


def BOFFline():
    global RUNstatus
    OFFline()                           # Upload OFFLINE status to FTP
    SaveDefault()                       # Save Default configuration at exit

    if (RUNstatus != 0):                # Stop the scan if running
        RUNstatus = 3
        AUDIOin()

    RUNstatus = 9                       # And stop the program in the mainloop


# ============================================ Main routine ====================================================

def CONTROL():          # Control of the whole process
    global ARCHIVEnumber
    global ARCHIVEsize
    global AUDIOdevin
    global AUDIOsignal1
    global DEFAULTcfg
    global DISPLAYtime
    global DOFTP
    global FFTline
    global FFTlineHR
    global FFTlineDY
    global FTPdelay
    global FTPflag
    global GRDw
    global RUNstatus
    global SAMPLErate
    global SMPfft
    global SMPfftstep
    global STACKING
    global STACKING10m
    global Tbuffer
    global Tstamp
    global Tsynch
    global TsynchHR
    global TsynchDY

     # ================ CONTROL ================================================
    txt = TimeLabelS(time.time())
    PrintT("=== START RUNNING: " + txt + " ===")

    filename = DEFAULTcfg + ".cfg"
    Recallconfig(filename)                                  # Try to load the config file

    INITIALIZEstart()                                       # Initialize the variables before SCREENclear
    SCREENclear()

    Pinfocnt = 0
    Screenrefreshcnt = 0
    FTPflag = False                                         # True when FTP upload required

    if AUDIOdevin == -1:
        SELECTaudiodevice()                                 # Select an audio device if AUDIOdevin == -1

    STARTshow()
    while RUNstatus != 2:
        SELECTaudiodevice()                                 # Select another audio device if not possible to open it
        STARTshow()                                         # Start the show

    # Initialize the ARCHIVEnumber for first 10 minutes stacks
    t = Tbuffer - DISPLAYtime * 60                          # The ARCHIVE number of the previous scan, not the current scan!
    T=time.gmtime(t)
    uu = strftime("%H", T)
    mm = strftime("%M", T)
    t = 60 * int(uu) + int(mm)
    ARCHIVEnumber = int(t / DISPLAYtime) % ARCHIVEsize      # Make the number 0 - size

    # Running loop forever, think about an escape
    while(1):
        time.sleep(0.01)                                    # Less CPU load
        if RUNstatus == 9:                                  # Stop the program
            sys.exit()
        AUDIOin()

        if len(AUDIOsignal1) > SMPfft and len(AUDIOsignal1) > SMPfftstep:
            DoFFT()                                         # Fast Fourier transformation
            MakeTrace(1)                                    # Make the trace
            MakeHRtrace()                                   # Make the hour trace and daily trace afterwards

            t1 = Tbuffer - len(AUDIOsignal1) / SAMPLErate   # Tbuffer is end t1 is start of audio buffer
            tn = Tsynch + DISPLAYtime * 60                  # Is the start time of the next display interval
            th = TsynchHR + HOURgrab * 3600                 # Is the start time of the next hour grab
            td = TsynchDY + 86400                           # Is the start time of the next daily grab

            Pinfocnt = Pinfocnt - 1                         # Reduce PrintInfo, only if Pinfocnt == 0
            if Pinfocnt < 1:
                Pinfocnt = 10                               # Display after n scans
                txt = str(int(tn - t1))                     # Count down
                PrintT(txt)
                PrintInfo()                                 # Print information

            if t1 >= th:
                FFTlineHR = 0                               # Reset the FFT line

            if t1 >= td:
                FFTlineDY = 0                               # Reset the FFT line

            if (STACKING > 0) and (STACKING10m == 1):       # Do the extra savings for the 10 minute grabs
                if DISPLAYtime == 20:
                    if FFTline == int(GRDw / 2):            # Extra save during 1/2 of the scan
                        Save10mgrabs(1)                     
                if DISPLAYtime == 30:
                    if FFTline == int(GRDw / 3):            # Extra save during 1/3 of the scan
                        Save10mgrabs(1)        
                    if FFTline == int(GRDw * 2 / 3):        # Extra save during 2/3 of the scan
                        Save10mgrabs(2)                     

            if t1 >= tn:
                FFTline = 0                                 # Reset the FFT line
                Tstamp = Tsynch                             # Save Tstamp

                t = float(SAMPLErate) * (tn - t1)           # The samples that have to be removed to synchronize exactly in time
                if t < 0:
                    t = 0
                AUDIOsignal1 = AUDIOsignal1[int(t):]        # Delete the samples upto the next synchronisation interval
                CALCtsynch(Tbuffer)                         # And calculate Tsynch, TsynchHR, TsynchDY

                DOtasks()                                   # DO tasks, here also a new timestamp (Tstamp)
                PrintTimescale()                            # Print time scale if all done

                if DOFTP > 0:                               # FTP upload requested: 1=FTPupload, 2=StoreFTPnames to txt file
                    FTPflag = True                          # Do FTP upload after FTPdelay
                else:
                    FTPflag = False

            else:
                AUDIOsignal1 = AUDIOsignal1[SMPfftstep:]    # Delete the first n samples, n depends on FFToverlap

            if t1 >= th:
                PrintTimescaleHR()                          # Print time scale hour

            if t1 >= td:
                PrintTimescaleDY()                          # Print time scale hour
 
            Screenrefreshcnt = Screenrefreshcnt - 1         # Less SCREENrefresh is less CPU power
            if Screenrefreshcnt < 1:
                Screenrefreshcnt = 3
                SCREENrefresh()                 

        DoRootUpdate()

        if FTPflag == True:                                 # Check for FTP upload
            t = time.time()
            if (t - Tsynch) > FTPdelay:
                FTPflag = False
                FTPupload()
    

def INITIALIZEstart():
    global ARCHIVEsize
    global DISPLAYtime
    global GRDw
    global SAMPLErate
    global SMPfftstep
    
    CHECKparameters()

    SMPfftstep = int(60.0 * DISPLAYtime * SAMPLErate / GRDw)

    ARCHIVEsize = int(24 * 60 / DISPLAYtime)
    if ARCHIVEsize > 72:                                                # Maximum 72
        ARCHIVEsize = 72

    # And some subroutines to set specific variables
    CALCSMPfftpwrTwo()
    CALCFFTwindowshape()
    CALCDISPLAYshape()
    CALCsrange()


def CHECKparameters():
    global AUDIOdevin
    global Brightness
    global Contrast
    global DISPLAY
    global DISPLAYtime
    global FTPdelay
    global FFTwindow
    global FILEname
    global FILEnameav
    global FILEnamepk
    global FILEnamehour
    global FILEnameday
    global HOURgrab
    global IMGformat
    global NOISEblankerlevel
    global PABUFFER
    global RUNstatus
    global SAMPLErate
    global SMPfft
    global STACKING
    global STACKING10m
    global STARTfrequency
    global STOPfrequency
    global TUNEDfrequency
    global ZEROpadding


    if SAMPLErate < 1200:
        SAMPLErate = 1200
    if SAMPLErate > 48000:
        SAMPLErate = 48000

    if SMPfft < 1024:
        SMPfft = 1024

    if STOPfrequency < (TUNEDfrequency + 10):
        STOPfrequeny =(TUNEDfrequency + 10)             # Minimum stopfrequency
        print("ERROR: Minimum STOP frequency is 10 Hz above TUNED frequency, corrected.")
    if STOPfrequency > (TUNEDfrequency + SAMPLErate / 2 - 1):
        STOPfrequency = (TUNEDfrequency + SAMPLErate / 2 - 1)
        print("ERROR: STOP frequency too high, corrected.")

    if STARTfrequency > (STOPfrequency - 10):
        STARTfrequency =  (STOPfrequency - 10)
        print("ERROR: START frequency too high, corrected.")
    if STARTfrequency < TUNEDfrequency:
        STARTfrequency = TUNEDfrequency
        print("ERROR: START frequency lower than TUNED frequency, corrected.")

    if AUDIOdevin == 0:
        AUDIOdevin = None

    if STACKING10m == 1:
        if DISPLAYtime != 20 and DISPLAYtime != 30:     # Only for DISPLAYtime 20 or 30
            STACKING10m = 0
        if STACKING < 1:                                # Only for STACKING > 0 
            STACKING10m = 0
            
    if Contrast < -25:
        Contrast = -25
    if Contrast > 25:
        Contrast = 25

    if Brightness < -10:
        Brightness = -10
    if Brightness > 10:
        Brightness = 10

    if DISPLAY < 0:
        DISPLAY = 0
    if DISPLAY > 3:
        DISPLAY = 3

    if NOISEblankerlevel < 0:
        NOISEblankerlevel = 0
    if NOISEblankerlevel > 5:
        NOISEblankerlevel = 5

    if FILEname == "":
        FILEname = "hfx"

    if FILEnameav == "":
        FILEnameav = "mfx"

    if FILEnamepk == "":
        FILEnamepk = "lfx"

    if FILEnamehour == "":
        FILEnamehour = "vhfx"

    if FILEnameday == "":
        FILEnameday = "vdfx"

    if FTPdelay < 0:
        FTPdelay = 0
    if FTPdelay > int((DISPLAYtime - 2) * 60):  
        FTPdelay = int((DISPLAYtime - 2) * 60)

    if HOURgrab < 1:
        HOURgrab = 1
    HOURgrab = int(24 / int(24 / HOURgrab))             # Integer division of 24

    if FFTwindow < 0:
        FFTwindow = 0
    if FFTwindow > 6:
        FFTwindow = 6

    ZEROpadding = int(ZEROpadding)
    if ZEROpadding < 1:
        ZEROpadding = 1 
    if ZEROpadding > 4:
        ZEROpadding = 4

    if PABUFFER < 120 * SAMPLErate * 2:
        PABUFFER = 120 * SAMPLErate * 2                 # Buffer time: (PABUFFER = TIME * samplerate / 2) seconds, (16bits = 2x8bits)

    if IMGformat != 0 and IMGformat < 60:               # Minimum quality 60%                    
        IMGformat = 60
    if IMGformat > 100:                                 # Maximum quality 100%       
        IMGformat = 100


def CALCtsynch(t):                              # Return the start time (s) of the current synchronisation interval
    global HOURgrab
    global Tsynch
    global TsynchHR
    global TsynchDY

    Tsynch = int(int(t / (DISPLAYtime * 60)) * (DISPLAYtime * 60) +0.1)
    TsynchHR = int(int(t / (HOURgrab * 3600)) * (HOURgrab * 3600) +0.1)
    TsynchDY = int(int(t / 86400) * 86400 +0.1)     


def CALCSMPfftpwrTwo():                         # Calculate SMPfftpwrTwo that is the nearest higher power of two or equal than SMPfft
    global SMPfft
    global SMPfftpwrTwo 

    v = math.log(float(SMPfft)) / math.log(2)   # Power of 2
    v = math.ceil(v)                            # Nearest integer
    SMPfftpwrTwo = 2 ** int(v)                  # Rounded to power of 2 that is nearest to SMPfft


def CALCFFTwindowshape():                       # Make the FFTwindowshape for the windowing function
    global FFTbandwidth                         # The FFT bandwidth
    global FFTwindow                            # Which FFT window number is selected
    global FFTwindowname                        # The name of the FFT window function
    global FFTwindowshape                       # The window shape
    global SAMPLErate                           # The sample rate
    global SMPfft                               # Number of FFT samples

    PrintT("Calculate FFT window shapes")

    # FFTname and FFTbandwidth in milliHz
    FFTwindowname = "No such window"
    FFTbw = 0
    
    if FFTwindow == 0:
        FFTwindowname = "0-Rectangular (no) window (B=1) "
        FFTbw = 1.0

    if FFTwindow == 1:
        FFTwindowname = "1-Cosine window (B=1.24) "
        FFTbw = 1.24

    if FFTwindow == 2:
        FFTwindowname = "2-Triangular window (B=1.33) "
        FFTbw = 1.33

    if FFTwindow == 3:
        FFTwindowname = "3-Hann window (B=1.5) "
        FFTbw = 1.5

    if FFTwindow == 4:
        FFTwindowname = "4-Blackman window (B=1.73) "
        FFTbw = 1.73

    if FFTwindow == 5:
        FFTwindowname = "5-Nuttall window (B=2.02) "
        FFTbw = 2.02

    if FFTwindow == 6:
        FFTwindowname = "6-Flat top window (B=3.77) "
        FFTbw = 3.77

    FFTbandwidth = int(1000.0 * FFTbw * SAMPLErate / float(SMPfft)) 

    # Calculate the shape
    FFTwindowshape = numpy.ones(SMPfft)         # Initialize with ones

    # m = 0                                     # For calculation of correction factor, furhter no function

    n = 0
    while n < SMPfft:

        # Cosine window function
        # medium-dynamic range B=1.24
        if FFTwindow == 1:
            w = math.sin(math.pi * n / (SMPfft - 1))
            FFTwindowshape[n] = w * 1.571

        # Triangular non-zero endpoints
        # medium-dynamic range B=1.33
        if FFTwindow == 2:
            w = (2.0 / SMPfft) * ((SMPfft/ 2.0) - abs(n - (SMPfft - 1) / 2.0))
            FFTwindowshape[n] = w * 2.0

        # Hann window function
        # medium-dynamic range B=1.5
        if FFTwindow == 3:
            w = 0.5 - 0.5 * math.cos(2 * math.pi * n / (SMPfft - 1))
            FFTwindowshape[n] = w * 2.000

        # Blackman window, continuous first derivate function
        # medium-dynamic range B=1.73
        if FFTwindow == 4:
            w = 0.42 - 0.5 * math.cos(2 * math.pi * n / (SMPfft - 1)) + 0.08 * math.cos(4 * math.pi * n / (SMPfft - 1))
            FFTwindowshape[n] = w * 2.381

        # Nuttall window, continuous first derivate function
        # high-dynamic range B=2.02
        if FFTwindow == 5:
            w = 0.355768 - 0.487396 * math.cos(2 * math.pi * n / (SMPfft - 1)) + 0.144232 * math.cos(4 * math.pi * n / (SMPfft - 1))- 0.012604 * math.cos(6 * math.pi * n / (SMPfft - 1))
            FFTwindowshape[n] = w * 2.811

        # Flat top window, 
        # medium-dynamic range, extra wide bandwidth B=3.77
        if FFTwindow == 6:
            w = 1.0 - 1.93 * math.cos(2 * math.pi * n / (SMPfft - 1)) + 1.29 * math.cos(4 * math.pi * n / (SMPfft - 1))- 0.388 * math.cos(6 * math.pi * n / (SMPfft - 1)) + 0.032 * math.cos(8 * math.pi * n / (SMPfft - 1))
            FFTwindowshape[n] = w * 1.000
        
        # m = m + w / SMPfft                          # For calculation of correction factor
        n = n + 1

    # if m > 0:                                     # For calculation of correction factor
    #     print("correction 1/m: " + str(1/m))      # For calculation of correction factor


def CALCDISPLAYshape():                             # Make the DISPLAY shapes for the display colors
    global Brightness                               # Brightness
    global DISPLAY                                  # Which display mode is selected
    global DISPLAYblue                              # The blue display curve
    global DISPLAYgreen                             # The green display curve
    global DISPLAYred                               # The red display curve
              
    PrintT("Calculate Display brightness curves")
              
    Bvalue = 2.0 ** abs(float(Brightness))
    Bvalue = int(Bvalue)                            # Max + or -64 as Brightness is max 6 or -6
    
    if Brightness < 0:                              # If negative, substract, else add
        Bvalue = -Bvalue

    n = 0
    while n < 1000:
        v = float(n) / 999.0
        v = v ** (1.0 / (1.0 + float(DISPLAY) / 2.0))

        R = float(v * v) * 255 + Bvalue            # Red starts at higher levels due to v * v
        R = int(R + 0.5)
        if R > 255:
            R = 255
        if R < 0:
            R = 0
        DISPLAYred[n] = int(R)

        G = v * 255 + Bvalue                       # Green is linear with the output of the FFT
        G = int(G + 0.5)
        if G > 255:
            G = 255
        if G < 0:
            G = 0
        DISPLAYgreen[n] = int(G)

        B = 255 * math.sqrt(v) + Bvalue            # Blue starts already at lower levels due to sqrt(v)
        B = int(B + 0.5)
        if B > 255:
            B = 255
        if B < 0:
            B = 0
        DISPLAYblue[n] = int(B)
        
        n = n + 1


def CALCsrange():                                           # Calculate the FFT sample range
    global GRDh
    global STARTfrequency
    global STOPfrequency
    global STARTsample
    global STOPsample
    global TUNEDfrequency
    global ZEROpadding
    global COMBf

    # Calculate start and stop sample that will be displayed and delete the unused samples
    fftsamples = ZEROpadding * SMPfftpwrTwo                 # Add zero's to the arrays SMPfftpwrTwo is nearest power of two of SMPfft 

    Fsample = float(SAMPLErate/2) / (fftsamples/2 - 1)      # Frequency step per FFT sample 
    Flo = STARTfrequency - TUNEDfrequency                   # The audio frequency to start with
    Fhi = STOPfrequency - TUNEDfrequency                    # The audio frequency to stop with
    STARTsample = Flo / Fsample                             # First sample in FFTresult[] that is used
    STARTsample = int(STARTsample)

    STOPsample = Fhi / Fsample                              # Last sample in FFTresult[] that is used             
    STOPsample = int(STOPsample)

    MAXsample = fftsamples / 2                              # Just an out of range check
    if STARTsample > (MAXsample - 1):
        STARTsample = MAXsample - 1

    if STOPsample > MAXsample:
        STOPsample = MAXsample

    # Calculation of COMBf
    COMBf = float(STOPsample - STARTsample) / float(GRDh)
    
    txt ="COMBINE lines: " + str(COMBf)
    PrintT(txt)


def STARTshow():
    global AUDIOsignal1
    global DISPLAYtime
    global FFTresults
    global FFTresultsHR
    global FFTresultsDY
    global GRABlinesHR
    global GRABlinesHRcnt
    global GRABlinesDY
    global GRABlinesDYcnt
    global GRDw
    global HOURgrab
    global FFTline
    global FFTlineHR
    global FFTlineDY
    global RUNstatus
    global Tbuffer
    global Tsynch
    global TsynchHR
    global TsynchDY


    INITIALIZEstart()                   # Initialize the variables

    AUDIOsignal1 = []                   # Clear audio buffer
    FFTresult = []                      # Clear the FFTresult
    FFTresultsHR = []
    FFTresultsDY = []

    GRABlinesHRcnt = 0                  # Counter for hour line grabbing function
    GRABlinesDYcnt = 0                  # Counter for day line grabbing function

    if RUNstatus != 0:
        RUNstatus = 3                   # Stop the show if still running
        AUDIOin()                       # Stop audio stream with RUNstatus == 3

    RUNstatus = 1                       # Start the show
    AUDIOin()                           # Start audio stream to set Tbuffer
    
    # Calculate FFTline positions at start time
    tg = time.time()
    Tbuffer = tg                        # Initialize Tbuffer with a start value
    Tsynch = tg                         # And also Tsynch, TsynchHR and TsynchDY
    TsynchHR = tg
    TsynchDY = tg

    FFTline = 0                         # And reset the lines
    FFTlineHR = 0
    FFTlineDY = 0
    
    CALCtsynch(tg)                      # Set the start of the synchronization intervals Tsynch, TsynchHR, TsynchDY
    t = tg - Tsynch
    t = GRDw * t / (DISPLAYtime * 60)
    FFTline = int(t + 0.5)

    t = tg - TsynchHR
    t = GRDw * t / (HOURgrab * 3600)
    FFTlineHR = int(t + 0.5)

    t = tg - TsynchDY
    t = GRDw * t / 86400
    FFTlineDY = int(t + 0.5)

    GRABlinesHR = int(HOURgrab * 60 / DISPLAYtime)
    txt = "GRABlinesHR: " + str(GRABlinesHR)
    PrintT(txt)
    
    GRABlinesDY = int(24 / HOURgrab)
    txt = "GRABlinesDY: " + str(GRABlinesDY)
    PrintT(txt)

    SCREENclear()


def Save10mgrabs(nr):                               # Save the  Half time grabs (used for 10 minute stacks)
    global ARCHIVEnumber
    global DISPLAYtime
    global FILename
    global IMGformat
    global THEimage4
    global Tstamp
    global STACKING

    if STACKING < 1 or STACKING10m == 0:            # Extra test for synchronized reception
        return
    if DISPLAYtime != 20 and DISPLAYtime != 30:     # Extra test for only 20 and 30 minutes display time
        return

    if IMGformat == 0:
        Fext = ".png"
    else:
        Fext = ".jpg"

    # Save the 10 minute grabs to the working directory
    filename = FILEname + "-tm"                     # hfx-tm.jpg
    SaveImg(THEimage4, WORKmap, filename) 

    # Save the 10 minute grabs to the working directory with number
    if DISPLAYtime == 20:
        number = ARCHIVEnumber * 2 + nr
    if DISPLAYtime == 30:
        number = ARCHIVEnumber * 3 + nr
    filename = FILEname + "-tm-" + str(number)      # hfx-tm-n.jpg
    SaveImg(THEimage4, WORKmap, filename) 

   
def AUDIOin():                          # Read the audio from the stream and store the data into the arrays
    global AUDIObuffer
    global AUDIOdevin
    global AUDIOsignal1
    global AUDIOstatus
    global PA
    global PABUFFER
    global PAFORMAT
    global PAstream
    global RUNstatus
    global SAMPLErate
    global SMPfft
    global SMPfftstep
    global STACKING
    global Tbuffer
    global Tsynch
    global DISPLAYtime
    
        
    # RUNstatus == 1 : Open Stream
    if (RUNstatus == 1):
        AUDIOsignal1 = []

        try:
            PAstream = PA.open(format = PAFORMAT,
                channels = 1, 
                rate = SAMPLErate, 
                input = True,
                output = False,
                frames_per_buffer = PABUFFER,           
                input_device_index = AUDIOdevin)
            RUNstatus = 2
            Tbuffer = time.time()                           # Init Tbuffer
            txt = "Maximum Audio Buffer length (seconds): "
            txt = txt + str(int(PABUFFER / SAMPLErate / 2)) # 2 bytes per audio sample
            PrintT(txt)
        except:                                             # If error in opening audio stream, show error
            RUNstatus = 0
            txt = "ERROR: Cannot open Audio Stream. Try a different Audio Device or Sample Rate."
            PrintT(txt)
        return        

    # RUNstatus == 2: Reading audio data from soundcard
    if RUNstatus == 2:
        try:
            buffervalue = PAstream.get_read_available()     # Buffer value reading and set AUDIObuffer
            # PrintT("Audiobuffer: " +str(buffervalue))     # TESTTESTTESTTESTTESTTESTTESTTEST for buffer tests
            if buffervalue > AUDIObuffer:
                AUDIObuffer = buffervalue
        except:
            PrintT("ERROR: Cannot read PAstream buffer length")
        try:
            if buffervalue > 1024:                          # >1024 to avoid problems. Do 10000000 for TESTTEST
                # PrintT("Audiobuffer: " +str(buffervalue)) # TESTTESTTESTTESTTESTTESTTESTTEST for buffer tests
                Tbuffer = time.time()
                signals = PAstream.read(buffervalue)        # Read samples from the buffer

                # Conversion audio samples to values -32762 to +32767 (ones complement) and add to AUDIOsignal1
                AUDIOsignal1.extend(numpy.fromstring(signals, "Int16"))
        except:
            RUNstatus = 4
            PrintT("ERROR: Audio buffer reset, cannot read input audio data.")


    # RUNstatus == 3: Stop
    # RUNstatus == 4: Stop and restart
    if (RUNstatus == 3) or (RUNstatus == 4):
        try:
            PAstream.stop_stream()
        except:
            pass
        try:
            PAstream.close()
        except:
            pass
        # PA.terminate()
        if RUNstatus == 3:
            RUNstatus = 0                                   # Status is stopped 
        if RUNstatus == 4:
            RUNstatus = 1                                   # Status is (re)start

        AUDIOsignal1 = []                                   # Clear audio buffer

  
def DoFFT():                            # Fast Fourier transformation and others like noise blanker and level for audio meter and time markers
    global AUDIOlevel
    global AUDIOlevelmax
    global AUDIOsignal1
    global FFTline
    global FFTresult
    global FFTwindowshape
    global GRDh
    global NOISEblankeractive
    global NOISEblankerlevel
    global PABUFFER
    global DATAbuffer
    global DATAbuffermax
    global RUNstatus
    global SAMPLErate
    global SMPfft
    global SMPfftpwrTwo
    global SMPfftstep
    global STACKING
    global DISPLAYtime
    global STARTfrequency
    global STARTsample
    global STOPsample
    global TUNEDfrequency
    global Tupload
    global ZEROpadding
    global ZEROpadding
    global COMBf

     
   # Initialisation of variables
    MAXaudio = 32000.0                                      # MAXaudio is 32000 for a good soundcard, lower for one with a lower dynamic range

    DATAbuffer = (len(AUDIOsignal1))                        # Data Buffer length
    if DATAbuffer > DATAbuffermax:
        DATAbuffermax = DATAbuffer

    FFTsignal = AUDIOsignal1[:SMPfft]                       # Take the first SMPfft samples from the stream

    # Convert list to numpy array REX for faster Numpy calculations
    REX = numpy.array(FFTsignal)                            # Make an arry of the list

    # Set Audio level display value
    AUDIOlevel = numpy.amax(REX) / MAXaudio                 # First check for maximum positive value
    MINlvl = abs(numpy.amin(REX) / MAXaudio)                # Then check for minimum positive value and make absolute
    
    if MINlvl > AUDIOlevel:
        AUDIOlevel = MINlvl

    AUDIOlevel = 20.0 * math.log10(float(AUDIOlevel)+1e-6)  # To dB's +1e-6 is divide by zero prevention

    if AUDIOlevel < -99:
        AUDIOlevel = -99

    if AUDIOlevel > AUDIOlevelmax:
        AUDIOlevelmax = AUDIOlevel
        
    # Noise blanker routine on REX before the FFT calculation. Delete the peaks in REX
    NOISEblankeractive = False                              # Reset Noiseblankeractive
    if NOISEblankerlevel > 0:                               # if > 0 then active
        S1 = int(0.002 * SAMPLErate)                        # Suppress 2 ms before the pulse
        S2 = int(0.005 * SAMPLErate)                        # Suppress 5 ms after the pulse

        NBpeaks = 0
        MAXpeaks = int(2 * len(REX) / SAMPLErate)           # Max 2 peaks per second
        if MAXpeaks < 1:                                    # But not less than 1
            MAXpeaks = 1

        NBlevel = MAXaudio / (2 ** NOISEblankerlevel)       # Noise blanker level

        NBposready = False                                  # For positive peaks
        NBnegready = False                                  # For negative peaks
        
        while NBposready == False or NBnegready == False:
            if NBposready == False:

                i = numpy.argmax(REX)                       # Find the sample number with the maximum
                Max = REX[i]

                if Max > NBlevel:
                    NBpeaks = NBpeaks + 1                   # A Noise Blanker peak
                    NOISEblankeractive = True               # The noise blanker is active
                    
                    m1 = i - S1                             # The first sample that has to be made zero
                    if m1 < 0:                              # Check if in the range of REX length
                        m1 = 0

                    m2 = i + S2                             # The last sample that has to be made zero
                    if m2 > len(REX):                       # Check if in the range of REX length
                        m2 = len(REX)

                    while m1 < m2:                          # Make all samples between m1 and m2 zero
                        REX[m1] = 0
                        m1 = m1 + 1
                else:
                    NBposready = True
            
            if NBpeaks >= MAXpeaks:
                NBposready = True
                NBnegready = True

            if NBnegready == False:

                i = numpy.argmin(REX)                       # Find the sample number with the minimum
                Min = REX[i]
                
                if Min < (-1*NBlevel):
                    NBpeaks = NBpeaks + 1                   # A Noise Blanker peak
                    NOISEblankeractive = True               # The noise blanker is active
 
                    m1 = i - S1                             # The first sample that has to be made zero
                    if m1 < 0:                              # Check if in the range of REX length
                        m1 = 0

                    m2 = i + S2                             # The last sample that has to be made zero
                    if m2 > len(REX):                       # Check if in the range of REX length
                        m2 = len(REX)

                    while m1 < m2:                          # Make all samples between m1 and m2 zero
                        REX[m1] = 0
                        m1 = m1 + 1
                else:
                    NBnegready = True

            if NBpeaks >= MAXpeaks:
                NBposready = True
                NBnegready = True


    # Do the FFT window function
    REX = REX * FFTwindowshape                              # The windowing shape function only over the samples


    # Zero padding of array for better interpolation of peak level of signals
    fftsamples = ZEROpadding * SMPfftpwrTwo                 # Add zero's to the arrays


    # FFT with numpy 
    fftresult = numpy.fft.fft(REX, n=fftsamples)            # Do FFT+zeropadding till n=fftsamples with NUMPY
    ALL = fftresult                                         # ALL = Real + Imaginary part
    ALL = ALL[STARTsample:STOPsample]                       # Delete the unused samples that will not be displayed
    ALL = numpy.absolute(ALL)                               # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!

    Totalcorr = float(ZEROpadding) / fftsamples             # Make an amplitude correction for the zero padding and FFT samples used
    Totalcorr = float(SMPfftpwrTwo) / SMPfft * Totalcorr    # Make an amplitude correction for rounding the samples to the nearest power of 2
    FFTresult = Totalcorr * ALL


def MakeHRtrace():
    global ADDhourlines
    global FFTresult
    global FFTresultHR
    global GRABlinesHR
    global GRABlinesDY
    global GRABlinesHRcnt
    global GRABlinesDYcnt

    if len(FFTresultHR) != len(FFTresult):          # Can happen during calibration
        FFTresultHR = FFTresult
        
    if GRABlinesHRcnt == 0:                         # Just copy to FFTresult to FFTresultHR
        FFTresultHR = FFTresult
        GRABlinesHRcnt = GRABlinesHRcnt + 1
        return

    if ADDhourlines > 0:
        FFTresultHR = numpy.maximum(FFTresultHR, FFTresult)

    if ADDhourlines < 0:
        FFTresultHR = numpy.minimum(FFTresultHR, FFTresult)

    if ADDhourlines == 0:
        FFTresultHR = FFTresultHR + FFTresult
    
    GRABlinesHRcnt = GRABlinesHRcnt + 1

    if GRABlinesHRcnt < GRABlinesHR:
        return
    else:
        if ADDhourlines == 0:
            FFTresultHR = FFTresultHR / GRABlinesHRcnt
        GRABlinesHRcnt = 0
        MakeTrace(2)                                # Make the trace
        MakeDYtrace()                               # Make the day trace


def MakeDYtrace():
    global FFTresult
    global FFTresultHR
    global FFTresultDY
    global GRABlinesHR
    global GRABlinesDY
    global GRABlinesHRcnt
    global GRABlinesDYcnt

    if len(FFTresultDY) != len(FFTresultHR):        # Can happen during calibration
        FFTresultDY = FFTresultHR

    if GRABlinesDYcnt == 0:                         # Just copy to FFTresult to FFTresultHR
        FFTresultDY = FFTresultHR
        GRABlinesDYcnt = GRABlinesDYcnt + 1
        return

    FFTresultDY = numpy.maximum(FFTresultDY, FFTresultHR)
  
    GRABlinesDYcnt = GRABlinesDYcnt + 1
    if GRABlinesDYcnt < GRABlinesDY:
        return
    else:
        GRABlinesDYcnt = 0
        MakeTrace(3)                                # Make the trace


def MakeTrace(screen):
    global COMBf
    global Contrast
    global DISPLAYblue
    global DISPLAYgreen
    global DISPLAYred
    global DISPLAYtime
    global FFTline
    global FFTlineHR
    global FFTlineDY
    global FFTresult
    global FFTresultHR
    global FFTresuldDY
    global GRDh                                                     # Screenheight
    global GRDw                                                     # Screenwidth
    global SCREENupdate
    global STACKING
    global STACKING10m
    global THEimage1
    global THEimage2
    global THEimage3
    global THEimage4
    global TXTw                                                     # Left top X value
    global TXTn                                                     # Left top Y value
    
   
    # Open a draw item for THEimage
    if screen == 1:
        draw = ImageDraw.Draw(THEimage1)
        draw4 = ImageDraw.Draw(THEimage4)
        FFTdata = FFTresult
        X1 = int(TXTw + FFTline)
        if DISPLAYtime == 20:
            X2 = int(TXTw + (2 * FFTline) % GRDw)
            LineP = 2                                               # 2 pixels
        if DISPLAYtime == 30:
            X2 = int(TXTw + (3 * FFTline) % GRDw)
            LineP = 3                                               # 3 pixels
                    
    if screen == 2:
        draw = ImageDraw.Draw(THEimage2)
        FFTdata = FFTresultHR
        X1 = int(TXTw + FFTlineHR)

    if screen == 3:
        draw = ImageDraw.Draw(THEimage3)
        FFTdata = FFTresultDY
        X1 = int(TXTw + FFTlineDY)

    Cvalue = 2.0 ** (float(Contrast) / 2)                           # Multiply with contrast (contast max. 1024)
    FFTdata = FFTdata * Cvalue
 
    LineT = 0                                                       # Line Thickness
    if DISPLAYtime == 20:
        LineT = 2
    if DISPLAYtime == 30:
        LineT = 3

    # Set the TRACEsize variable
    TRACEsize = len(FFTdata)                                        # Set the trace length, last two values are line and marker type

    Y1 = TXTn + GRDh                                                # Start at bottom
        
    Dsample = 0.0                                                   # Pointer in FFTresult[]
    n = 0
    while n < (GRDh-1):
        if (Dsample + COMBf) < TRACEsize:
            v = FFTdata[int(Dsample)]
            
            s1 = Dsample + 1.0
            s2 = Dsample + COMBf
            while s1 < s2:                                          # Peak value from more samples if zero padding or zoom active
                try:                                                # Try for boundary overload error catching
                    v1 = FFTdata[int(s1)]
                except:
                    v1 = 0
                if v1 > v:
                    v = v1
                s1 = s1 + 1.0

            if v > 999.0:
                v = 999.0

            i = int(v)
            clred = int(DISPLAYred[i])
            clgreen = int(DISPLAYgreen[i])
            clblue = int(DISPLAYblue[i])

            rgb = "#%02x%02x%02x" % (clred, clgreen, clblue)

            draw.rectangle((X1, Y1, (X1+1), (Y1-1)), fill=rgb)                  # In frequency range
            if screen == 1 and STACKING10m > 0:
                draw4.rectangle((X2, Y1, (X2+LineP), (Y1-1)), fill=rgb)         # In frequency range 10m scans

        else:
            draw.rectangle((X1, Y1, (X1+1), (Y1-1)), fill="#606060")            # Out of frequency range
            if screen == 1 and STACKING10m > 0:
                draw4.rectangle((X2, Y1, (X2+LineP), (Y1-1)), fill="#606060")   # Out of frequency range 10m scan

        Y1 = Y1 - 1
        Dsample = Dsample + COMBf

        n = n + 1

    del draw                                                        # Delete the draw items
    if screen == 1:
        del draw4

    # Cursor line
    CURSOR(screen, X1+2, 4)                                         # Make cursor line width

    if screen == 1:
        FFTline = FFTline + 1
        
    if screen == 2:
        FFTlineHR = FFTlineHR + 1

    if screen == 3:
        FFTlineDY = FFTlineDY + 1


def DOtasks():                                              # Do this tasks when a scan is finished
    global ARCHIVEnumber
    global ARCHIVEsize
    global DISPLAYtime
    global DOFTParchGRABS
    global DOFTPhour
    global DOFTParchHR
    global DOFTPdaily
    global DOFTParchDY
    global DOFTPstacking
    global DOFTPstackingarch
    global DOFTPhourgrabs
    global DOFTPdailygrabs
    global SAVEgrabs
    global FILEname
    global FILEnamehour
    global FILEnameday
    global FFTlineHR
    global FFTlineDY
    global FTPfiles
    global IMGformat
    global SAVEgrabs
    global SAVEgrabsHR
    global SAVEgrabsDY
    global STACKING
    global STACKING10m
    global STOREmap
    global WORKmap
    global THEimage1
    global THEimage2
    global THEimage3
    global THEimage4
    global Tstamp

    AUDIOin()
 
    PrintT(" ") 
    txt = TimeLabelS(time.time()) + "-Do Tasks"
    PrintT(txt)

    if SAVEsettings == True:                                # Save the settings to the default .cfg
        SaveDefault()

    if IMGformat == 0:
        Fext = ".png"
    else:
        Fext = ".jpg"
        
    ##### DO the grab:
    # Always save the picture to the working directory
    filename = FILEname
    FTPfiles = [filename + Fext]                            # Always the first to the FTP file list
    SaveImg(THEimage1, WORKmap, filename) 

    # Save the picture with time+date stamp if SAVEgrabs > 0
    if SAVEgrabs > 0:
        filename = FILEname + "-" + TimeLabel(Tstamp)
        SaveImg(THEimage1, STOREmap, filename) 

    # Always save the archive file
    T=time.gmtime(Tstamp)
    uu = strftime("%H", T)
    mm = strftime("%M", T)
    t = 60 * int(uu) + int(mm)
    ARCHIVEnumber = int(t / DISPLAYtime) % ARCHIVEsize      # Make the number 0 - size
    filename = FILEname + "-" + str(ARCHIVEnumber)          # hfx-n.jpg
    SaveImg(THEimage1, WORKmap, filename) 
    if DOFTParchGRABS > 0:                                  # In the FTP file list
        FTPfiles.append(filename + Fext)
    #####

    ##### DO the Stacking grabs
    AUDIOin()

    if STACKING > 1:
        MAKEstacks()                                        # Make the stacks

    if STACKING > 0 and STACKING10m == 1:                   # The Stacking archive with 10 minutes scans
        Save10mgrabs(0)                                     # Saving of 10 minute stacking grabs at the end of the scan
        MAKEstacks10m()
    #####

    ##### DO the Hour grabs:
    AUDIOin()

    # Save the current running hour grab
    filename = FILEnamehour
    if DOFTPhour > 0: 
        FTPfiles.append(filename + Fext)
    SaveImg(THEimage2, WORKmap, filename) 

    # Save the hour picture with time+date stamp if SAVEgrabsHR > 0
    if FFTlineHR == 0 and SAVEgrabsHR > 0:
        filename =  FILEnamehour + "-" + TimeLabel(Tstamp)
        SaveImg(THEimage2, STOREmap, filename) 

    # Always save the hour archive file
    if FFTlineHR == 0:
        T=time.gmtime(Tstamp)
        uu = strftime("%H", T)
        mm = strftime("%M", T)
        t = 60 * int(uu) + int(mm)
        number = int(t / (HOURgrab * 60))                   # Make the number
        filename = FILEnamehour + "-" + str(number)         # vhfx-n.jpg"
        if DOFTParchHR > 0:
            FTPfiles.append(filename + Fext)
        SaveImg(THEimage2, WORKmap, filename) 
    #####

    ##### DO the Daily grabs:
    AUDIOin()
        
    # Save the current running daily grab
    filename = FILEnameday
    if DOFTPdaily > 0: 
        FTPfiles.append(filename + Fext)
    SaveImg(THEimage3, WORKmap, filename) 

    # Save the picture with time+date stamp if SAVEgrabsDY > 0
    if FFTlineDY == 0 and SAVEgrabsDY > 0:
        filename = FILEnameday + "-" + TimeLabel(Tstamp)
        SaveImg(THEimage3, STOREmap, filename) 

    # Always save the daily archive file
    if FFTlineDY == 0:
        T=time.gmtime(Tstamp)
        dt = strftime("%d", T)                              # Make the number
        filename = FILEnameday + "-" + dt                   # vdfx-n.jpg n is the day of the month
        if DOFTParchDY > 0:
            FTPfiles.append(filename + Fext)
        SaveImg(THEimage3, WORKmap, filename) 
    #####
 

def MAKEstacks():                                               # Make the stacking picturesof the NORMAL grabs
    global ARCHIVEnumber
    global ARCHIVEsize
    global DISPLAYtime
    global SAVEgrabsAV
    global SAVEgrabsPK
    global DOFTPstackAV
    global DOFTPstackPK
    global FILEname
    global FILEnameav
    global FILEnamepk
    global FTPfiles
    global IMGformat
    global STACKING
    global Tstamp
    global WORKmap

    if STACKING < 2:                                            # Extra check
        PrintT("ERROR: MAKEstacks() called with STACKING < 2")
        return

    if IMGformat == 0:
        Fext = ".png"
    else:
        Fext = ".jpg"

    ###### First read the pictures in the image array im
    im = []
    n = 0
    p = ARCHIVEnumber
    while n < STACKING:                                         # Make a list with the pictures to be stacked
        filename = WORKmap + FILEname + "-" + str(p) + Fext
        try:
            im.append(Image.open(filename))                     # Floating point not supported by Chops
        except:
            im.append(Image.open(WORKmap + FILEname + Fext))    # If not possible, append the standard picture
        n = n + 1

        p = p - 1
        if p < 0:
            p = ARCHIVEsize - 1                                 # From the first to the last picture
    #####
            
    ##### Do the average stacking
    imav = im[0].copy()                                         # Make an image imav from im[0] for the average function

    n = 1
    while n < STACKING:                                         # The average function for the stacking
        AUDIOin()
        alpha = 1.0 / (n + 1)                                   # Blend factor, n + 1 as picture 1 = im[0]!
        try:
            imav = Image.blend(imav, im[n], alpha)              # Blend the pictures for average function
        except:
            pass
        n = n + 1
   
    # Save the average stack
    filename = FILEnameav
    if DOFTPstackAV > 0:                                        # Add this one, use the 10m stack only for the archive
        FTPfiles.append(filename + Fext)

    SaveImg(imav, WORKmap, filename) 

    # Save the AV picture with time+date stamp if SAVEgrabsAV > 0 and STACKING10m == 0
    if SAVEgrabsAV > 0 and STACKING10m == 0:
        filename =  FILEnameav + "-" + TimeLabel(Tstamp)
        SaveImg(imav, STOREmap, filename)

    # Always save the AV archive file if STACKING10m == 0
    AUDIOin()
    if STACKING10m == 0:
        # Make filename
        filename = FILEnameav + "-" + str(ARCHIVEnumber)        # vhfx-n.jpg"
        if DOFTParchAV > 0:
            FTPfiles.append(filename + Fext)
        SaveImg(imav, WORKmap, filename)
    #####

    ##### Do the peak stacking
    impk = im[0].copy()                                         # Make an image immpk from im[1] for the peak function

    n = 1
    while n < STACKING:                                         # The peak and average function for the stacking
        AUDIOin()
        try:
            impk = ImageChops.lighter(im[n], impk)              # Add the pictures for lighter, peak funtion
        except:
            pass
        n = n + 1

    # Save the peak stack
    filename = FILEnamepk
    if DOFTPstackPK > 0:
        FTPfiles.append(filename + Fext)
    SaveImg(impk, WORKmap, filename)

    # Save the PK picture with time+date stamp if SAVEgrabsPK > 0 and STACKING10m == 0
    if SAVEgrabsPK > 0  and STACKING10m == 0:
        filename = STOREmap + FILEnamepk + "-" + TimeLabel(Tstamp)
        SaveImg(impk, STOREmap, filename)

    # Always save the PK archive file if STACKING10m == 0
    if STACKING10m == 0:
        # Make filename
        filename = FILEnamepk + "-" + str(ARCHIVEnumber)        # vhfx-n.jpg"
        if DOFTParchPK > 0:
            FTPfiles.append(filename + Fext)
        SaveImg(impk, WORKmap, filename)
    #####
    

def MAKEstacks10m():                                                    # Make the stacking Half Time archive stacking pictures
    global ARCHIVEnumber
    global ARCHIVEsize
    global DISPLAYtime
    global SAVEgrabsAV
    global SAVEgrabsPK
    global DOFTPstackAV
    global DOFTPstackPK
    global FILEname
    global FILEnameav
    global FILEnamepk
    global FTPfiles
    global STACKING
    global STACKING10m
    global Tstamp
    global WORKmap


    if STACKING10m == 0:                                                # Extra check
        PrintT("Error: Routine 10 minute stacks called while STACKING10m == 0")
        return

    if DISPLAYtime != 20 and DISPLAYtime != 30:                         # Extra check
        PrintT("Error: Routine 10 minute stacks called with incorrect DISPLAYtime")
        return

    if IMGformat == 0:
        Fext = ".png"
    else:
        Fext = ".jpg"

    if DISPLAYtime == 20:
        dv = 2
    if DISPLAYtime == 30:
        dv = 3

    ###### First read the pictures in the image array im
    im = []
    n = 0
    pdv = ARCHIVEnumber * dv
    while n < dv  * STACKING:                                           # Open the 10 minute scans
        filename = WORKmap + FILEname + "-tm-" + str(pdv) + Fext        # Name <mfx-tm-n.jpg>
        try:
            im.append(Image.open(filename))                             # Floating point not supported by Chops
        except:
            im.append(Image.open(WORKmap + FILEname + "-tm" + Fext))    # If not possible, append the standard picture
        n = n + 1

        pdv = pdv - 1
        if pdv < 0:
            pdv = ARCHIVEsize * dv - 1                                  # From the first to the last grab
    #####
            
    ##### Do the average stacking
    imav = im[0].copy()                                                 # Make an image immav from im[0] for the average function

    n = 1
    while n < (dv * STACKING):                                          # The average function for the stacking
        AUDIOin()
        alpha = 1.0 / (n + 1)                                           # Blend factor, n + 1 as picture 1 = im[0]!
        try:
            imav = Image.blend(imav, im[n], alpha)                      # Blend the pictures for average function
        except:
            pass
        n = n + 1

    # Add date and time stamp
    draw = ImageDraw.Draw(imav)
    txt = TimeLabel(Tstamp) + "   Average stacks: " + str(dv * STACKING)
    lstep = float(TXTs) / 5.0                                           # 5 = 2 tmarkers + 1 space + 2 info
    x = TXTw
    y = int(GRDh+TXTn + 1 * lstep + 0.5)
    draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)
    del draw

    # Save the average stack
    filename = FILEnameav
    if STACKING > 1:
        filename = filename + "-tm"
    if DOFTPstackAV > 0:
        FTPfiles.append(filename + Fext)
    SaveImg(imav, WORKmap, filename)
    
    # Save the AV picture with time+date stamp
    if SAVEgrabsAV > 0:
        filename =  FILEnameav + "-" + TimeLabel(Tstamp)
        SaveImg(imav, STOREmap, filename)
        
    # Always save the AV archive file
    # Make filename
    filename = FILEnameav + "-" + str(ARCHIVEnumber)                    # mfx-n.jpg
    if DOFTParchAV > 0:
        FTPfiles.append(filename + Fext)
    SaveImg(imav, WORKmap, filename)    #####

    ##### Do the peak stacking
    impk = im[0].copy()                                                 # Make an image immpk from im[0] for the peak function

    n = 1
    while n < (dv * STACKING):                                          # The peak and average function for the stacking
        AUDIOin()
        try:
            impk = ImageChops.lighter(im[n], impk)                      # Add the pictures for lighter, peak funtion
        except:
            pass
        n = n + 1

    # Add date and time stamp
    draw = ImageDraw.Draw(impk)
    txt = TimeLabel(Tstamp) + "   Peak stacks: " + str(dv * STACKING)

    lstep = float(TXTs) / 5.0                                           # 5 = 2 tmarkers + 1 space + 2 info
    x = TXTw
    y = int(GRDh+TXTn + 1 * lstep + 0.5)
    draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)
    del draw

    # Save the peak stack
    filename = FILEnamepk
    if STACKING > 1:
        filename = filename + "-tm"
    if DOFTPstackPK > 0:
        FTPfiles.append(filename + Fext)
    SaveImg(impk, WORKmap, filename)
    
    # Save the PK picture with time+date stamp
    if SAVEgrabsPK > 0:
        filename = FILEnamepk + "-" + TimeLabel(Tstamp)
        SaveImg(impk, STOREmap, filename)

    # Always save the PK archive file
    filename = FILEnamepk + "-" + str(ARCHIVEnumber)                    # lfx-n.jpg
    if DOFTParchPK > 0:
        FTPfiles.append(filename + Fext)
    SaveImg(impk, WORKmap, filename)
    #####


def TimeLabel(t):
    T = time.gmtime(t)
    label = strftime("%Y%m%d-%H%M", T)
    return(label)


def TimeLabelS(t):
    T = time.gmtime(t)
    label = strftime("%Y%m%d-%H%M%S", T)
    return(label)
   

def SaveImg(img, folder, name):                                         # Save the image
    global IMGformat
    name = folder + name
    
    try:
        if IMGformat < 1:
            name = name + ".png"
            img.save(name, "PNG")
        else:
            name = name + ".jpg"
            img.save(name, "JPEG", quality=IMGformat)                   # Quality between 0-100
        txt = name + " saved"
        PrintT(txt)
    except:
        txt = name + "ERROR: Saving FAILED"
        PrintT(txt)


def SCREENclear():                      # Clear screen, make lines and reset FFTline
    global AUDIOsignal1
    global FFTline
    global FFTresults
    global GRDh
    global GRDw
    global RUNstatus
    global THEimage1
    global THEimage2
    global THEimage3
    global THEimage4
    global TXTn
    global TXTw
    global TXTs
    global TXTe    

    
    # Clear data
    AUDIOsignal1 = []
    FFTresults = []

    # Open a draw item for THEimage and Delete all items on the screen
    draw = ImageDraw.Draw(THEimage1)
    draw.rectangle((0, 0, GRDw+TXTw+TXTe+2,GRDh+TXTn+TXTs+2), fill="#000000")
    del draw

    draw = ImageDraw.Draw(THEimage2)
    draw.rectangle((0, 0, GRDw+TXTw+TXTe+2,GRDh+TXTn+TXTs+2), fill="#000000")
    del draw

    draw = ImageDraw.Draw(THEimage3)
    draw.rectangle((0, 0, GRDw+TXTw+TXTe+2,GRDh+TXTn+TXTs+2), fill="#000000")
    del draw

    draw = ImageDraw.Draw(THEimage4)
    draw.rectangle((0, 0, GRDw+TXTw+TXTe+2,GRDh+TXTn+TXTs+2), fill="#000000")
    del draw

    CURSOR(1,0, GRDw+TXTw+TXTe)         # Make the whole screen equal to the cursor content
    CURSOR(2,0, GRDw+TXTw+TXTe)         # Make the whole screen equal to the cursor content
    CURSOR(3,0, GRDw+TXTw+TXTe)         # Make the whole screen equal to the cursor content
    CURSOR(4,0, GRDw+TXTw+TXTe)         # Make the whole screen equal to the cursor content
    
    PrintAllText()                      # Update the text on all screens
    PrintTimescale()                    # Print the standard time scale
    PrintTimescaleHR()                  # Print the hour time scale
    PrintTimescaleDY()                  # Print the daily time scale
    PrintTimescale10m()                 # Print the half size time scale (for stacking 10 minute grabs)
    
    SCREENrefresh()


def SCREENrefresh():                    # Refresh the screen
    global DISPLAYimg
    global SCREENnr
    global THEimage1
    global THEimage2
    global THEimage3
    global THEimage4
    
    if SCREENnr == 1:
        DISPLAYimg.paste(THEimage1)     # Save screen 1 to the Desktop
    if SCREENnr == 2:
        DISPLAYimg.paste(THEimage2)     # Save screen 2 to the Desktop
    if SCREENnr == 3:
        DISPLAYimg.paste(THEimage3)     # Save screen 3 to the Desktop
    if SCREENnr == 4:
        DISPLAYimg.paste(THEimage4)     # Save screen 4 to the Desktop
        
    DoRootUpdate()    


def DoRootUpdate():                     # Update idle tasks etc.
    ca.update_idletasks()
    ca.update()
    root.update_idletasks()             # Check controls etc.             
    root.update()


def PrintInfo():                        # Process information
    global AUDIObuffer
    global AUDIOdevin
    global AUDIOlevelmax
    global Brightness
    global Contrast
    global DATAbuffermax
    global DISPLAY
    global DOFTP
    global FILEname
    global FTPflag
    global FTPdelay
    global NOISEblankeractive
    global NOISEblankerlevel
    global RUNstatus
    global SAMPLErate
    global Tsynch

    # Runstatus and level information
    if (RUNstatus == 0) or (RUNstatus == 3):
        txt = FILEname + " STOPPED"
    else:
        txt = FILEname + " RUNNING"

    txt = txt + "   Audio Device=" + str(AUDIOdevin) 
    
    if DOFTP == 0:
        txt = txt + "  FTP upload disabled"        

    if DOFTP == 1:
        txt = txt + "  FTP upload enabled"
        if FTPflag == True:
            t = FTPdelay - (time.time() - Tsynch)
            txt = txt + ": " + str(int(t))
    
    if DOFTP == 2:
        txt = txt + "  External FTP upload required"        
        if FTPflag == True:
            t = FTPdelay - (time.time() - Tsynch)
            txt = txt + ": " + str(int(t))
    
    PrintT(txt)
        
    txt = "Compression=" + str(DISPLAY) + "  C=" + str(Contrast) + "  B=" + str(Brightness)
    txt = txt + "  FFTsample step: " + str(SMPfftstep)

    PrintT(txt)

    txt = "Audio level(dB): " + str(int(AUDIOlevelmax)) + "  Audio Buffer(s): " + str(int(AUDIObuffer / SAMPLErate))
    txt = txt + "  Data Buffer(s): " + str(int(DATAbuffermax / SAMPLErate))
    
    if NOISEblankerlevel == 0:
        txt = txt + "  NB off(0)"
    else:
        txt = txt + "  NB lvl(1-5): " + str(NOISEblankerlevel)
        if NOISEblankeractive == True:                      # Noise blanker active, spike detected
            txt = txt + "*"
    
    PrintT(txt)

    # Reset the max values
    AUDIOlevelmax = -99
    DATAbuffermax = 0
    AUDIObuffer = 0


def CURSOR(screen, thisline, thiswidth):                                # Make a cursor on this line with this width
    global GRDh
    global GRDw
    global MARKERfs
    global STARTfrequency
    global STOPfrequency
    global THEimage
    global TXTn
    global TXTw
    global TXTs
    global TXTe    


    # Open a draw item for THEimage
    if screen == 1:
        draw = ImageDraw.Draw(THEimage1)
    if screen == 2:
        draw = ImageDraw.Draw(THEimage2)
    if screen == 3:
        draw = ImageDraw.Draw(THEimage3)
    if screen == 4:
        draw = ImageDraw.Draw(THEimage4)

    # Cursor line black background
    X1 = thisline
    X2 = thisline + thiswidth

    if X2 > GRDw+TXTw+TXTe:
        X2 = GRDw+TXTw+TXTe
  
    draw.rectangle((X1, TXTn, X2, (TXTn+GRDh)), fill="#000000")

    # Draw horizontal grid lines
    Pdiv = float(GRDh) / ((STOPfrequency - STARTfrequency) / MARKERfs)  # Pixels per division

    i = float(GRDh)
    while (i > 0):
        y = TXTn + int(i + 0.5) - 1                                     # -1 for correction thickness lowest line
        draw.rectangle((X1, y-1, X2,y+1), fill="red") 
        i = i - Pdiv

    del draw


def PrintAllText():                                                     # Print the text on all 3 screens
    n = 1
    while n <= 4:
        PrintText(n)
        n = n + 1


def PrintText(screen):                                              # Print the text only on screen n
    global AUDIOlevel
    global AUDIOstatus
    global Brightness
    global COLORcanvas
    global COLORtext
    global Contrast
    global FFTbandwidth
    global GRDh
    global GRDw
    global LoporaName
    global MARKERfs
    global SAMPLErate
    global SMPfft
    global STACKING
    global STACKING10m
    global STATIONname
    global STARTfrequency
    global STOPfrequency
    global THEimage1
    global THEimage2
    global THEimage3
    global THEimage4
    global MARKERfs
    global TXTn
    global TXTw
    global TXTs
    global TXTe
    

    # Open a draw item for THEimage
    if screen == 1:
        draw = ImageDraw.Draw(THEimage1)

    if screen == 2:
        draw = ImageDraw.Draw(THEimage2)

    if screen == 3:
        draw = ImageDraw.Draw(THEimage3)
    
    if screen == 4:
        if STACKING10m == 0:                                        # Not if 10 minute scan is disabled
            return
        draw = ImageDraw.Draw(THEimage4)
    
    lstep = float(TXTs) / 5.0                                       # 5 = 2 tmarkers + 1 space + 2 info

    # Delete text items
    draw.rectangle((0,GRDh+TXTn+int(2.0*lstep),GRDw+TXTw+TXTe+2,GRDh+TXTn+TXTs+2), fill=COLORcanvas)
    
    # Trace information
    txt = STATIONname
    x = TXTw
    y = int(GRDh + TXTn + 3 * lstep + 0.5)
    draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)

    # Technical information
    txt = "Sample rate: " + str(SAMPLErate) + "    FFTsamples: " + str(SMPfft) +  "    Bandwidth (mHz): " + str(FFTbandwidth) 

    x = TXTw
    y = int(GRDh+TXTn + 4 * lstep + 0.5)
    draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)
    
    # Program version
    w = TEXTfont.getsize(LoporaName)
    x = TXTw + GRDw + TXTe - w[0] - 10
    y = int(GRDh+TXTn + 4 * lstep + 0.5)
    draw.text((x,y),LoporaName, font=TEXTfont, fill=COLORtext)
    
    # Frequency scale #
    Pdiv = GRDh / ((STOPfrequency - STARTfrequency) / MARKERfs)     # Pixels per division
    FR = STARTfrequency
    
    y = TXTn + GRDh
    i = 0
    while (y > TXTn):
        txt = str(int(FR))
        w = TEXTfont.getsize(txt)
        x = TXTw + GRDw + TXTe - w[0]  
        y = TXTn + GRDh - int(Pdiv * i) - w[1] - 2                  # 2 extra pixels margin
        draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)
        FR = FR + MARKERfs
        i = i + 1         

    del draw                                                        # Delete the draw item


def PrintTimescale():                                               # Print the standard time scale
    global COLORtext
    global DISPLAYtime
    global GRDh
    global GRDw
    global MARKERts
    global STACKING
    global THEimage1
    global THEimage2
    global THEimage3
    global Tsynch
    global TXTn
    global TXTw
    global TXTs
    global TXTe

 
    # Open a draw item for THEimage
    draw = ImageDraw.Draw(THEimage1)

    # Delete text items on the screen
    lstep = float(TXTs) / 5.0        # 5 = 2 tmarkers + 1 space + 2 info
    draw.rectangle((0,TXTn+GRDh+1,GRDw+TXTw+TXTe+2,TXTn+GRDh+int(2.0*lstep)), fill=COLORcanvas)
        
    ts = float(GRDw) / (DISPLAYtime / MARKERts)                     # Pixels per marker step

    tm = Tsynch
    n = 0.0
    while (n <= GRDw):
        X1 = int(float(TXTw) + n + 0.5)
        Y1 = int(TXTn + GRDh)                                       # Start at bottom
        
        draw.rectangle((X1, Y1, X1+1, Y1+10), fill="red")           # Draw the marker

        T=time.gmtime(tm)
        txt = strftime("%H:%M", T)
        draw.text((X1+3,Y1+3),txt, font=TEXTfont, fill=COLORtext)

        tm = tm + MARKERts * 60
        n = n + ts

    # Add the date
    T=time.gmtime(Tsynch)
    txt = strftime("(%Y-%m-%d)", T)

    x = TXTw
    y = int(GRDh+TXTn + 1 * lstep)
    draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)
  
    del draw                                                        # Delete the draw item


def PrintTimescaleHR():                                             # Print the Hour time scale
    global COLORtext
    global GRDh
    global GRDw
    global HOURgrab
    global STACKING
    global THEimage2
    global TsynchHR
    global TXTn
    global TXTw
    global TXTs
    global TXTe

 
    # Open a draw item for THEimage
    draw = ImageDraw.Draw(THEimage2)

    # Delete text items on the screen
    lstep = float(TXTs) / 5.0                                       # 5 = 2 tmarkers + 1 space + 2 info
    draw.rectangle((0,TXTn+GRDh+1,GRDw+TXTw+TXTe+2,TXTn+GRDh+int(2.0*lstep)), fill=COLORcanvas)

    if HOURgrab <= 8:
        markertime = 30
    else:
        markertime = 60

    ts = float(GRDw) / ((HOURgrab * 60) / markertime) 

    tm = TsynchHR
    n = 0.0
    while (n <= GRDw):
        X1 = int(float(TXTw) + n + 0.5)
        Y1 = int(TXTn + GRDh)                                       # Start at bottom
        
        draw.rectangle((X1, Y1, X1+1, Y1+10), fill="red")           # Draw the marker

        T=time.gmtime(tm)
        txt = strftime("%H:%M", T)
        draw.text((X1+3,Y1+3),txt, font=TEXTfont, fill=COLORtext)

        tm = tm + markertime * 60
        n = n + ts

    # Add the date
    T=time.gmtime(TsynchHR)
    txt = strftime("(%Y-%m-%d)", T)

    x = TXTw
    y = int(GRDh+TXTn + 1 * lstep + 0.5)
    draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)
  
    del draw                                                        # Delete the draw item


def PrintTimescaleDY():                                             # Print the Daily time scale
    global COLORtext
    global DISPLAYtime
    global GRDh
    global GRDw
    global STACKING
    global THEimage3
    global TsynchDY
    global TXTn
    global TXTw
    global TXTs
    global TXTe    

 
    # Open a draw item for THEimage
    draw = ImageDraw.Draw(THEimage3)

    # Delete text items on the screen
    lstep = float(TXTs) / 5.0                                        # 5 = 2 tmarkers + 1 space + 2 info
    draw.rectangle((0,TXTn+GRDh+1,GRDw+TXTw+TXTe+2,TXTn+GRDh+int(2.0*lstep)), fill=COLORcanvas)

    markertime = 60

    ts = float(GRDw) / (1440 / markertime) 

    tm = TsynchDY
    n = 0.0
    while (n <= GRDw):
        X1 = int(float(TXTw) + n + 0.5)
        Y1 = int(TXTn + GRDh)                                       # Start at bottom
        
        draw.rectangle((X1, Y1, X1+1, Y1+10), fill="red")           # Draw the marker

        T=time.gmtime(tm)
        txt = strftime("%H:%M", T)
            
        draw.text((X1+3,Y1+3),txt, font=TEXTfont, fill=COLORtext)

        tm = tm + markertime * 60
        n = n + ts

    # Add the date
    T=time.gmtime(TsynchDY)
    txt = strftime("(%Y-%m-%d)", T)

    x = TXTw
    y = int(GRDh+TXTn + 1 * lstep + 0.5)
    draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)
  
    del draw                                                        # Delete the draw item


def PrintTimescale10m():                                            # Print the 10 minutes time scale (only markers)
    global COLORtext
    global GRDh
    global GRDw
    global HOURgrab
    global STACKING
    global THEimage4
    global Tstamp
    global TXTn
    global TXTw
    global TXTs
    global TXTe

 
    # Open a draw item for THEimage
    draw = ImageDraw.Draw(THEimage4)

    # Delete text items on the screen
    lstep = float(TXTs) / 5.0                                       # 5 = 2 tmarkers + 1 space + 2 info
    draw.rectangle((0,TXTn+GRDh+1,GRDw+TXTw+TXTe+2,TXTn+GRDh+int(2.0*lstep)), fill=COLORcanvas)

    n = 0
    while (n <= GRDw):
        X1 = int(float(TXTw) + n + 0.5)
        Y1 = int(TXTn + GRDh)                                       # Start at bottom
        draw.rectangle((X1, Y1, X1+1, Y1+10), fill="red")           # Draw the marker
        n = n + GRDw / 10

    # Add the date
    T=time.gmtime(Tstamp)
    txt = strftime("%Y-%m-%d  %H:%M", T)
 
    del draw                                                        # Delete the draw item


def SaveDefault():
    global DEFAULTcfg
    global SAVEsettings

    filename = DEFAULTcfg + ".cfg"
    Saveconfig(filename)
    SAVEsettings = False
    
    
def Saveconfig(filename):                                           # Save the configuration
    global STATIONname
    global DOFTP
    global DOFTParchGRABS
    global DOFTPstackAV
    global DOFTParchAV
    global DOFTPstackPK
    global DOFTParchPK
    global DOFTPhour
    global DOFTParchHR
    global DOFTPdaily
    global DOFTParchDY
    global SAVEgrabs
    global SAVEgrabsAV
    global SAVEgrabsPK
    global SAVEgrabsHR
    global SAVEgrabsDY
    global STARTfrequency
    global STOPfrequency
    global TUNEDfrequency
    global AUDIOdevin
    global STACKING
    global STACKING10m
    global DISPLAYtime
    global MARKERfs
    global MARKERts
    global SAMPLErate
    global SMPfft
    global Contrast    
    global Brightness
    global DISPLAY
    global NOISEblankerlevel
    global FILEname
    global FILEnameav
    global FILEnamepk
    global FILEnamehour
    global FILEnameday
    global FTPhost
    global FTPuser
    global FTPdir
    global FTPpassword
    global FTPdelay
    global HOURgrab
    global ADDhourlines
    global FFTwindow
    global ZEROpadding
    global PABUFFER
    global IMGformat

    Wfile = open(filename,'w')                                          # output file setting

    S = ""
    while len(S) < 30:
        S = S + " "

    txt = "LOPORA-V5 CONFIGURATION\n"
    Wfile.write(txt)

    # Fixed
    txt = STATIONname + "\n"
    Wfile.write(txt)

    txt = "===== CONFIGURE FTP uploads =====\n"
    Wfile.write(txt)

    txt = str(DOFTP)
    txt = txt + S[len(txt):] + "Set to 1 to upload to the FTP site. Set to 2 for EXTERNAL upload (save to FTPuploads.txt)\n"
    Wfile.write(txt)
    
    txt = str(DOFTParchGRABS)
    txt = txt + S[len(txt):] + "Set to 1 to upload the archive grabs (hf1-0.jpg to hf1-71.jpg)\n"
    Wfile.write(txt)

    txt = str(DOFTPstackAV)
    txt = txt + S[len(txt):] + "Set to 1 to upload the average stacking grabs (mf1.jpg)\n"
    Wfile.write(txt)
    
    txt = str(DOFTParchAV)
    txt = txt + S[len(txt):] + "Set to 1 to upload the average stacking grabs archive (mf1-0.jpg to mf1-71.jpg)\n"
    Wfile.write(txt)
    
    txt = str(DOFTPstackPK)
    txt = txt + S[len(txt):] + "Set to 1 to upload the peak stacking grabs (lf1.jpg)\n"
    Wfile.write(txt)

    txt = str(DOFTParchPK)
    txt = txt + S[len(txt):] + "Set to 1 to upload the peak stacking grabs archive (lf1-0.jpg to lf1-71.jpg)\n"
    Wfile.write(txt)
    
    txt = str(DOFTPhour)
    txt = txt + S[len(txt):] + "Set to 1 to upload the hour grabs (vhf1.jpg)\n"
    Wfile.write(txt)
    
    txt = str(DOFTParchHR)
    txt = txt + S[len(txt):] + "Set to 1 to upload the hour grabs archive (vhf1-0.jpg to vhf1-2.jpg)\n"
    Wfile.write(txt)
    
    txt = str(DOFTPdaily)
    txt = txt + S[len(txt):] + "Set to 1 to upload the daily grab (uhf1.jpg)\n"
    Wfile.write(txt)

    txt = str(DOFTParchDY)
    txt = txt + S[len(txt):] + "Set to 1 to upload the daily grabs archive (uhf1-1.jpg to uhf1-31.jpg)\n"
    Wfile.write(txt)
    
    txt = "===== CONFIGURE STORAGE =====\n"
    Wfile.write(txt)

    txt = str(SAVEgrabs)
    txt = txt + S[len(txt):] + "Set to 1 to save the grabs to the storage (hf1-date.jpg)\n"
    Wfile.write(txt)
    
    txt = str(SAVEgrabsAV)
    txt = txt + S[len(txt):] + "Set to 1 to save the average grabs to the storage (mf1-date.jpg)\n"
    Wfile.write(txt)
    
    txt = str(SAVEgrabsPK)
    txt = txt + S[len(txt):] + "Set to 1 to save the peak grabs to the storage (lf1-date.jpg)\n"
    Wfile.write(txt)
    
    txt = str(SAVEgrabsHR)
    txt = txt + S[len(txt):] + "Set to 1 to save the hour grabs to the storage (vhf1-date.jpg)\n"
    Wfile.write(txt)
    
    txt = str(SAVEgrabsDY)
    txt = txt + S[len(txt):] + "Set to 1 to save the daily grabs to the storage (uhf1-date.jpg)\n"
    Wfile.write(txt)

    txt = "===== CONFIGURE PARAMETERS =====\n"
    Wfile.write(txt)

    txt = str(STARTfrequency)
    txt = txt + S[len(txt):] + "Start frequency at the bottom of screen in Hz\n"
    Wfile.write(txt)

    txt = str(STOPfrequency)
    txt = txt + S[len(txt):] + "Stop frequency at the top of screen in Hz\n"
    Wfile.write(txt)

    txt = str(TUNEDfrequency)
    txt = txt + S[len(txt):] + "Tuning frequency of the receiver in Hz\n"
    Wfile.write(txt)

    txt = str(AUDIOdevin)
    txt = txt + S[len(txt):] + "[DEFAULT=None] audio device for input, set to -1 to ask\n"
    Wfile.write(txt)

    txt = str(STACKING)
    txt = txt + S[len(txt):] + "Stacking of n+ pictures\n"
    Wfile.write(txt)

    txt = str(STACKING10m)
    txt = txt + S[len(txt):] + "Set to 1 to activate 10 minute grabs for 20 and 30 minutes display time only\n"
    Wfile.write(txt)

    txt = str(DISPLAYtime)
    txt = txt + S[len(txt):] + "[Default=20] for 20 minutes, but can be changed to 10 or 30 for normal operation\n"
    Wfile.write(txt)

    txt = str(MARKERfs)
    txt = txt + S[len(txt):] + "Marker frequency step (Hz per div)\n"
    Wfile.write(txt)

    txt = str(MARKERts)
    txt = txt + S[len(txt):] + "Marker time step at every N minutes\n"
    Wfile.write(txt)

    txt = str(SAMPLErate)
    txt = txt + S[len(txt):] + "[DEFAULT=8820 or 44100 without downsampling] Audio Sample Rate (44100/5)\n"
    Wfile.write(txt)

    txt = str(SMPfft)
    txt = txt + S[len(txt):] + "[DEFAULT=32768 or 131072 without downsampling] Number of FFT samples\n"
    Wfile.write(txt)

    txt = str(Contrast)
    txt = txt + S[len(txt):] + "Contrast (0 to 25) is Power of sqrt(2)\n"
    Wfile.write(txt)

    txt = str(Brightness)
    txt = txt + S[len(txt):] + "Brightness (-10 to + 10) is Power of 2\n"
    Wfile.write(txt)

    txt = str(DISPLAY)
    txt = txt + S[len(txt):] + "Display compression factor 0 - 3\n"
    Wfile.write(txt)

    txt = str(NOISEblankerlevel)
    txt = txt + S[len(txt):] + "Noise blanker level (0 to 5, 0 is off)\n"
    Wfile.write(txt)

    txt = "===== CONFIGURE FILE NAMES =====\n"
    Wfile.write(txt)

    txt = FILEname
    txt = txt + S[len(txt):] + "The file name of the picture\n"
    Wfile.write(txt)

    txt = FILEnameav
    txt = txt + S[len(txt):] + "The file name of the averaged stacked picture\n"
    Wfile.write(txt)

    txt = FILEnamepk
    txt = txt + S[len(txt):] + "The file name of the peak stacked picture\n"
    Wfile.write(txt)

    txt = FILEnamehour
    txt = txt + S[len(txt):] + "The file name of the hour grabs\n"
    Wfile.write(txt)

    txt = FILEnameday
    txt = txt + S[len(txt):] + "The file name of the daily grabs\n"
    Wfile.write(txt)

    txt = "===== CONFIGURE FTP SETTINGS =====\n"
    Wfile.write(txt)

    txt = FTPhost
    txt = txt + S[len(txt):] + "FTP host\n"
    Wfile.write(txt)

    txt = FTPuser
    txt = txt + S[len(txt):] + "FTP user\n"
    Wfile.write(txt)

    txt = FTPdir
    txt = txt + S[len(txt):] + "FTP remote directory\n"
    Wfile.write(txt)

    txt = FTPpassword
    txt = txt + S[len(txt):] + "FTP password\n"
    Wfile.write(txt)

    txt = "===== CONFIGURE SPECIAL SETTINGS =====\n"
    Wfile.write(txt)

    txt = str(FTPdelay)
    txt = txt + S[len(txt):] + "[DEFAULT=0] Delay (s) to avoid FTP upload collisions\n"
    Wfile.write(txt)

    txt = str(HOURgrab)
    txt = txt + S[len(txt):] + "[DEFAULT=8] Hour grab time. Can be 2, 4, 6, 8 or 12 hours\n"
    Wfile.write(txt)

    txt = str(ADDhourlines)
    txt = txt + S[len(txt):] + "[DEFAULT=1] 1=Take max of n FFT scans for hour grabs, 0=Take average, -1=Take minimum\n"
    Wfile.write(txt)

    txt = "# ===== DEFAULT VALUES THAT DO NOT NEED TO BE MODIFIED =====\n"
    Wfile.write(txt)

    txt = str(FFTwindow)
    txt = txt + S[len(txt):] + "[DEFAULT=3] FFTwindow 0=None(B=1) 1=Cos(B=1.24) 2=Tri(B=1.33) 3=Han(B=1.5) 4=Bla(B=1.73) 5=Nut(B=2.02) 6=Flat(B=3.77)\n"
    Wfile.write(txt)

    txt = str(IMGformat)
    txt = txt + S[len(txt):] + "[DEFAULT=90] 0=PNG picture format, >0=JPEG quality (60-100%)\n"
    Wfile.write(txt)

    Wfile.close()                                                       # Close the file

    txt = "Saved config: " + filename
    PrintT(txt)



def Recallconfig(filename):
    global STATIONname
    global DOFTP
    global DOFTParchGRABS
    global DOFTPstackAV
    global DOFTParchAV
    global DOFTPstackPK
    global DOFTParchPK
    global DOFTPhour
    global DOFTParchHR
    global DOFTPdaily
    global DOFTParchDY
    global SAVEgrabs
    global SAVEgrabsAV
    global SAVEgrabsPK
    global SAVEgrabsHR
    global SAVEgrabsDY
    global STARTfrequency
    global STOPfrequency
    global TUNEDfrequency
    global AUDIOdevin
    global STACKING
    global STACKING10m
    global DISPLAYtime
    global MARKERfs
    global MARKERts
    global SAMPLErate
    global SMPfft
    global Contrast    
    global Brightness
    global DISPLAY
    global NOISEblankerlevel
    global FILEname
    global FILEnameav
    global FILEnamepk
    global FILEnamehour
    global FILEnameday
    global FTPhost
    global FTPuser
    global FTPdir
    global FTPpassword
    global FTPdelay
    global HOURgrab
    global ADDhourlines
    global FFTwindow
    global ZEROpadding
    global PABUFFER
    global IMGformat

    txt = "Recall config: " + filename
    PrintT(txt)
              
    try:
        Rfile = open(filename,'r')      # open the input file with settings
    except:
        return()

    try:
        txt = Rfile.readline()          # read the line, do nothing with it, it is just a description
    except:
        pass
        
    try:
        txt = Rfile.readline()          # read the next line
        txt = txt[0:-1]                 # delete carriage return by [0:-1] addition
        STATIONname = txt.strip()
        PrintT(STATIONname)
    except:
        pass

    try:
        txt = Rfile.readline()          # read the line, do nothing with it, it is just a description
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        DOFTP = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        DOFTParchGRABS = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        DOFTPstackAV = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        DOFTParchAV = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        DOFTPstackPK = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        DOFTParchPK = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        DOFTPhour = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        DOFTParchHR = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        DOFTPdaily = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        DOFTParchDY = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the line, do nothing with it, it is just a description
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        SAVEgrabs = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        SAVEgrabsAV = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        SAVEgrabsPK = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        SAVEgrabsHR = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        SAVEgrabsDY = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the line, do nothing with it, it is just a description
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        STARTfrequency = float(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        STOPfrequency = float(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        TUNEDfrequency = float(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        AUDIOdevin = int(striptxt(txt))
    except:
        AUDIOdevin = 0

    try:
        txt = Rfile.readline()          # read the next line
        STACKING = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        STACKING10m = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        DISPLAYtime = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        MARKERfs = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        MARKERts = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        SAMPLErate = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        SMPfft = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        Contrast = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        Brightness = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        DISPLAY = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        NOISEblankerlevel = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the line, do nothing with it, it is just a description
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        FILEname = striptxt(txt)
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        FILEnameav = striptxt(txt)
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        FILEnamepk = striptxt(txt)
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        FILEnamehour = striptxt(txt)
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        FILEnameday = striptxt(txt)
    except:
        pass

    try:
        txt = Rfile.readline()          # read the line, do nothing with it, it is just a description
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        FTPhost = striptxt(txt)
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        FTPuser = striptxt(txt)
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        FTPdir = striptxt(txt)
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        FTPpassword = striptxt(txt)
    except:
        pass

    try:
        txt = Rfile.readline()          # read the line, do nothing with it, it is just a description
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        FTPdelay = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        HOURgrab = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        ADDhourlines = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the line, do nothing with it, it is just a description
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        FFTwindow = int(striptxt(txt))
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        IMGformat = int(striptxt(txt))
    except:
        pass

    Rfile.close()                       # Close the file

    INITIALIZEstart()
    SCREENclear()


def striptxt(txtin):
    if len(txtin) < 20:
        return("0")
    
    txtout = ""
    n = 0
    while txtin[n] == " " and n < 20:
        n = n + 1

    while txtin[n] != " " and n < 20:
        txtout = txtout + txtin[n]
        n = n + 1

    if txtout == "":
        txtout = "0"
    return(txtout)


def OFFline():                                      # Go offline
    global FILEname
    global FTPfiles
    global IMGformat
    global RUNstatus
    global THEimage1
    global WORKmap

    draw = ImageDraw.Draw(THEimage1)
    
    # print offline text to THEimage1
    txt = "OFFLINE - OFFLINE - OFFLINE - OFFLINE - OFFLINE - OFFLINE - OFFLINE - OFFLINE - OFFLINE - OFFLINE"
    x = TXTw
    y = TXTn
    draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)

    del draw                                        # Delete the draw item

    if IMGformat == 0:
        Fext = ".png"
    else:
        Fext = ".jpg"
        
    # Save the picture to the working directory
    filename = FILEname
    FTPfiles = [filename + Fext]                    # Always the first to the FTP file list
    SaveImg(THEimage1, WORKmap, filename)           # Save the grab with the OFFLINE text

    FTPupload()                                     # Do the FTP upload of

    # Save the screens for you own purposes  
    filename = "screen1"
    SaveImg(THEimage1, "./", filename)



def SELECTaudiodevice():                            # Select an audio device
    global AUDIOdevin

    PS = pyaudio.PyAudio()
    ndev = PS.get_device_count()

    n = 0
    ai = ""
    ao = ""
    while n < ndev:
        s = PS.get_device_info_by_index(n)
        # print(n, s)
        if s['maxInputChannels'] > 0:
            ai = ai + str(s['index']) + ": " + s['name'] + "\n"
        if s['maxOutputChannels'] > 0:
            ao = ao + str(s['index']) + ": " + s['name'] + "\n"
        n = n + 1
    PS.terminate()

    AUDIOdevin = None
    
    s = simpledialog.askstring("Device","Select audio INPUT device:\nPress Cancel for Windows Default\n\n" + ai + "\n\nNumber: ")
    if (s != None):                                 # If Cancel pressed, then None
        try:                                        # Error if for example no numeric characters or OK pressed without input (s = "")
            v = int(s)
        except:
            s = "error"

        if s != "error":
            if v < 0 or v > ndev:
                v = 0
            AUDIOdevin = v


def PrintT(text):
    global PrintTenabled

    if PrintTenabled == False:
        return
    else:
        print(text)



def FTPupload():
    global DOFTP
    global FTPfiles
    global FTPhost                      # FTP host
    global FTPuser                      # FTP user
    global FTPdir                       # FTP remote directory
    global FTPpassword                  # FTP password
    global WORKmap                      # The map where the files are

    
    if DOFTP == 0:                      # Extra test
        return

    AUDIOin()
    
    txt = TimeLabelS(time.time()) + "-start FTP upload"
    PrintT(txt)

    PrintT("Files to be uploaded to FTP:")
    n = 0
    while n < len(FTPfiles):            # Print the file names to the Terminal screen for information
        filename = FTPfiles[n]
        PrintT(filename)
        n = n + 1

    if DOFTP > 1:                       # No FTP upload, save WORKmap name, FTP settings and FTPfiles to FTPuploads.txt
        name = "FTPuploads.txt"
        Wfile = open(name,'w')          # Open the file with settings and FTP files for the External FTP upload program

        Wfile.write(WORKmap + "\n")     # Save the workmap
        Wfile.write(FTPhost + "\n")     # Save the FTP settings
        Wfile.write(FTPuser + "\n")
        Wfile.write(FTPdir + "\n")        
        Wfile.write(FTPpassword + "\n")        

        n = 0
        while n < len(FTPfiles):        # Save the FTP file names
            filename = FTPfiles[n]
            Wfile.write(filename + "\n")
            n = n + 1

        Wfile.close()                   # Close the file
        PrintT("No FTP upload, FTP files stored in: " + name)
        return                          # No FTP upload, return from this routine

    ##### Start FTP upload routine if DOFTP == 1
    AUDIOin()

    ftp = None
 
    try:
        # ftp = ftplib.FTP(FTPhost, FTPuser, FTPpassword)           # Open the FTP connection for file uploading with the default time out, works OK for me
        ftp = ftplib.FTP(FTPhost, FTPuser, FTPpassword, "", 10)     # Open the FTP connection for file uploading with a time out, did avoid some problems for others
        PrintT("Connected and logged in to FTP host")
    except:
        PrintT("ERROR: Cannot connected and log in to FTP host")

    if (ftp):
        AUDIOin()
        # Change FTP directory
        try:    
            if FTPdir != "":
                ftp.cwd(FTPdir)
                txt = "Changed to remote directory: " + FTPdir
                PrintT(txt)
        except:
            PrintT("ERROR: Cannot change to remote directory: " + FTPdir)
            
        # Upload the files
        n = 0
        while n < len(FTPfiles):
            AUDIOin()
            filename = FTPfiles[n]
            storedname = WORKmap + filename

            try:            
                fup = open(storedname, 'rb')                        # Open the file of the picture to be uploaded
                ftp.storbinary("STOR " + filename, fup, 8192)       # Store the file (picture)
                fup.close()
                PrintT(filename + " uploaded")
            except:
                PrintT("ERROR: " + filename + " upload FAILED")
            n = n + 1
    try:
        if ftp:
            ftp.close()
    except:
        pass

    AUDIOin()

    txt = TimeLabelS(time.time()) + "-end FTP upload"
    PrintT(txt)
  

# ================ Make Screen ==========================
LoporaName = "LOPORA-v5a.py (02-11-2018): QRSS reception"

root=Tk()
root.title(LoporaName)

frame2 = Frame(root, background="blue", borderwidth=5, relief=RIDGE)
frame2.pack(side=LEFT, expand=1, fill=Y)

frame1 = Frame(root, background="blue", borderwidth=5, relief=RIDGE)
frame1.pack(side=LEFT, expand=1, fill=X, anchor=NW)

scrollbarV = Scrollbar(frame1, orient=VERTICAL)
scrollbarV.pack(side=RIGHT, expand=NO, fill=Y)

scrollbarH = Scrollbar(frame1, orient=HORIZONTAL)
scrollbarH.pack(side=BOTTOM, expand=NO, fill=X)

ca = Canvas(frame1, width=CANVASwidth, height=CANVASheight, background = COLORcanvas, scrollregion=(0,0,GRDw+TXTw+TXTe,GRDh+TXTn+TXTs))
ca.config(xscrollcommand=scrollbarH.set, yscrollcommand=scrollbarV.set)
ca.pack(side=TOP)

scrollbarV.config(command=ca.yview)
scrollbarH.config(command=ca.xview)

# Top buttons
b = Button(frame2, text="Compression", width=Buttonwidth, command=BCompression)
b.pack(side=TOP, padx=1, pady=2)

b = Button(frame2, text="Contrast+", width=Buttonwidth, command=BContrast2)
b.pack(side=TOP, padx=1, pady=2)

b = Button(frame2, text="Contrast-", width=Buttonwidth, command=BContrast1)
b.pack(side=TOP, padx=1, pady=2)

b = Button(frame2, text="Brightness+", width=Buttonwidth, command=BBrightness2)
b.pack(side=TOP, padx=1, pady=2)

b = Button(frame2, text="Brightness-", width=Buttonwidth, command=BBrightness1)
b.pack(side=TOP, padx=1, pady=2)

b = Button(frame2, text="Noise blanker+", width=Buttonwidth, command=BNBlevel2)
b.pack(side=TOP, padx=1, pady=2)

b = Button(frame2, text="Noise blanker-", width=Buttonwidth, command=BNBlevel1)
b.pack(side=TOP, padx=1, pady=2)

b = Button(frame2, text="Select Screen", width=Buttonwidth, command=BScreenselect)
b.pack(side=TOP, padx=1, pady=2)

# Bottom buttons
b = Button(frame2, text="GO OFFLINE", width=Buttonwidth, background="red", command=BOFFline)
b.pack(side=BOTTOM, padx=1, pady=2)

b = Button(frame2, text="FTP status", width=Buttonwidth, background="red", command=BFTPstatus)
b.pack(side=BOTTOM, padx=1, pady=2)

b = Button(frame2, text="Load setting", width=Buttonwidth, command=BRecall)
b.pack(side=BOTTOM, padx=1, pady=2)

b = Button(frame2, text="Save setting", width=Buttonwidth, command=BSave)
b.pack(side=BOTTOM, padx=1, pady=2)

b = Button(frame2, text="Audio device", width=Buttonwidth, command=BAudiodevice)
b.pack(side=BOTTOM, padx=1, pady=2)

b = Button(frame2, text="Calibrate-", width=Buttonwidth, command=BCalibrate2)
b.pack(side=BOTTOM, padx=1, pady=2)

b = Button(frame2, text="Calibrate+", width=Buttonwidth, command=BCalibrate1)
b.pack(side=BOTTOM, padx=1, pady=2)

b = Button(frame2, text="PrintOnOff", width=Buttonwidth, command=BPrintTcontrol)
b.pack(side=BOTTOM, padx=1, pady=2)

# ================ Initialize the screen picture ===============================

from PIL import Image
from PIL import ImageChops
from PIL import ImageTk
from PIL import ImageDraw
from PIL import ImageFont

THEimage1 = Image.new("RGB",(GRDw+TXTw+TXTe+2,GRDh+TXTn+TXTs+2),color="blue")
THEimage2 = Image.new("RGB",(GRDw+TXTw+TXTe+2,GRDh+TXTn+TXTs+2),color="blue")
THEimage3 = Image.new("RGB",(GRDw+TXTw+TXTe+2,GRDh+TXTn+TXTs+2),color="blue")
THEimage4 = Image.new("RGB",(GRDw+TXTw+TXTe+2,GRDh+TXTn+TXTs+2),color="blue")

DISPLAYimg = ImageTk.PhotoImage(THEimage1)                  # Desktopmode, make DISPLAYimg
Pid = ca.create_image(0, 0, anchor=NW, image=DISPLAYimg)    # Desktopmode, display the image

# Select one of the fonts here below for the text
# This font should be in the same directory as the Lopora program
# You can find other .pil fonts on the internet
# =============================================

# TEXTfont = ImageFont.load("helvR08.pil")
TEXTfont = ImageFont.load("helvB08.pil")
# TEXTfont = ImageFont.load("helvR10.pil")
# TEXTfont = ImageFont.load("helvB10.pil")

CONTROL()                       # Start the main routine loop
