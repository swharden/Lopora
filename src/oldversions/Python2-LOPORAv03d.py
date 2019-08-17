# LOPORAv03d.py(w) (25-08-2017)
# For reception of LOw POwer RAdio signals or QRSS signals
# For Python version 2.6 or 2.7
# With external module pyaudio (for used Python version); PIL library module (for used Python version); NUMPY module (for used Python version)
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

from Tkinter import *
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename 
from tkSimpleDialog import askstring
from tkMessageBox import *

############################################################################################################################################

# Settings that are fixed in the program and can be modified in accordance with your preferences
DEBUG = 0                   # Print information to shell. Limited if DEBUG = 1, detailed if 2

AUTORUN = False             # Default is False. True for Automatic Run.

FTPenabled = False          # If True, upload snapshot. Can be modified with the Snapshot button.
FTPhost = "FTPhostname"     # FTP host
FTPuser = "FTPusername"     # FTP user
FTPdir = "FTPdirectory"     # FTP remote directory, if none ("") then the remote directory will be asked
FTPpassword = "FTPpassword" # FTP password, if none ("") then the password will be asked

SNAPshotenabled = False     # If True, save snapshot. Can be modified with the Snapshot button.
WAVenabled = False          # A WAV audio snapshot is made and uploaded just after the FTP snapshot
Remote = False              # Remote control by file lopnew.cfg enabled

AUDIOdevin = None           # Audio device for input. None = Windows default. Can be modified with the Audio device button.
AUDIOdevout = None          # Audio device for output. None = Windows default. Can be modified with the Audio device button.
WAVinput = 0                # DEFAULT 0 for Audio device input, 1 for WAV file channel 1 input, 2 for WAV file channel 2 input

STACKinterval = int(20)     # Default 20 for 20 minutes, but can be changed to 10 or 30 
ARCHIVEfiles = True         # Make 12 / 24 hour archive files but only when time synchronized reception (STACKING > 0)
HOURmarkers = False         # If True then HOUR markers instead of minute markers
LOPshotnow = False          # If True then a file lopshotnow.jpg is saved at each screen update for screen checks via remote connections
############################################################################################################################################

# Specific Raspberry Pi settings
RASPIterminalmode = False   # True for use in terminal mode without desktop
RASPIterminalinfo = False   # True for printing info about run status to terminal window
RASPIcputemperature = False # True for printing the CPU temperature of the Raspberry Pi
############################################################################################################################################

# Settings that can be stored and modified in a configuration file and are overwritten by the start configuration file "lopora.cfg"
STATIONname = "QTH and Station name plus remarks" 
SAMPLErate = 6000           # Sample rate of down sampled audio stream
ZEROpadding = 1             # Zero padding for interpolation between FFT points (power of 2, default 1, 0 for slow PC's, 2 for faster PC's)
ZOOMfactor = 1.1            # Zoom-out factor default 1, 2 for larger frequency range on screen
SMPfft = 16384              # Number of FFT samples, will be rounded off to nearest higher power of 2, (4096, 8192, 16384, 32768, 65536, 131072...)
FFTaverage = 1              # Average n traces, (2 to 10, 1 is off)
TUNEDfrequency = 10138467.0 # Tuning frequency of the receiver in Hz
SCREENupdate = 5            # Screen update per n FFT traces (3 to 10 to save processing time for screen update)
Vdiv = 20                   # Hz per division
FFToverlap = 2.7            # FFT overlap (default=2, 3 for fast PC's), overlap of arrays of samples for detailed display of dots
Dwidth = 1                  # Speed control by setting the width of a pixel (integer, default=1, set to 2 or 3 for wider screen pixels)
Contrast = 10               # Contrast (0 to 25) is Power of sqrt(2)
Brightness = 5              # Brightness (-6 to + 6) is Power of 2
FFTwindow = 1               # FFTwindow 0=None (rectangular B=1), 1=Cosine (B=1.24), 2=Triangular non-zero endpoints (B=1.33),
                            # 3=Hann (B=1.5), 4=Blackman (B=1.73), 5=Nuttall (B=2.02), 6=Flat top (B=3.77)
STARTfrequency = 10139860.0 # Start frequency, reception frequency at bottom of screen in Hz
NOISEblankerlevel = 0       # Noise blanker level (0 to 5, 0 is off)
DISPLAY = 0                 # Display compression factor 0 - 3
STACKING = 0                # Receive in 10 minute time synchronized intervals if STACKING > 0 and stack STACKING screens if > 1
############################################################################################################################################

# Screen settings and colors that can be modified in accordance with your preferences
GRW = 1130                  # Width of the grid
GRH = 600                   # Height of the grid
X0L = 10                    # Left top X value of grid
Y0T = 5                     # Left top Y value of grid

Buttonwidth = 15            # With of the buttons

COLORframes = "#000080"     # Color = "#rrggbb" rr=red gg=green bb=blue, Hexadecimal values 00 - ff
COLORcanvas = "#000000"     # Background color of the canvas
COLORtext = "#ffffff"       # Text color
COLORfrequency = "#ffffff"  # Color of the frequency text
COLORaudiobar = "#606060"   # Color of the audio bar
COLORaudiook = "#00ff00"    # Green if audio not clipped
COLORaudiomax = "#ff0000"   # Red if audio clipped

FREQmargin = 0              # Optional space for the frequency scale outside the picture
############################################################################################################################################

# Initialisation of global variables required in various routines (DO NOT MODIFY THEM!)
AUDIOlevel = 0.0                        # Level of audio input 0 to 1
AUDIOsignal1 = []                       # Audio trace channel
AUDIOstatus = 0                         # 0 Audio off, 1 Audio on

CANVASheight = GRH + 100                # The canvas height
CANVASwidth = GRW + 2*X0L + FREQmargin  # The canvas width

RUNstatus = 0                           # 0 stopped, 1 start, 2 running, 3 stop now, 4 stop and restart

DISPLAYred = numpy.ones(1001)           # The red display curve
DISPLAYgreen = numpy.ones(1001)         # The green display curve
DISPLAYblue = numpy.ones(1001)          # The blue display curve

FFTline = 0                             # Display line of the screen
FFTbandwidth = 0                        # The FFT bandwidth
FFTresult = []                          # FFT result
FFTwindowname = "--"                    # The FFT window name
FFTwindowshape = numpy.ones(SMPfft)     # The FFT window curve
FFTmemory = numpy.ones(1)               # The memory for averaging
FTPmessage = "-"                        # FTP upload status message

MARKERtype = 0                          # The type of marker that will be displayed

NOISEblankeractive = False              # Noise blanker has not detected any spikes yet

RXbuffer = 0.0                          # Data contained in input buffer in %
RXbuffermin = 0.0
RXbuffermax = 0.0
RXbufferoverflow = False

SCREENupdatecounter = 0                 # Counter for update display
SNAPshotmessage = "-"                   # Snapshot status message
SMPfftpwrTwo = 1.0                      # The nearest higher power of two of SMPfft
STARTsample = 0                         # The start sample used for the display, be calculated on initialize
STOPsample = 0                          # The stop sample used for the display, be calculated on initialize

TRACEtime = 0                           # The trace time necessary to print the time markers
TIMEmarkercnt = 0                       # Counts to 10 for extra long 10 minute markers
TRACEdate = "-"                         # The start date and time of the scree
TRACEh = 0                              # The trace hour time
TRACEm = 0                              # The trace minute time

ZEROpaddingvalue = 1                    # The zero padding value 2 ** ZERO padding, calculated on initialize
############################################################################################################################################

# Upload time
Tupload = 60                            # Time (s) reserved for image creation, WAV record and FTP upload
############################################################################################################################################

# =================================== Start widgets routines ========================================
def BNot():
    print("Routine not made yet")


def BDisplay():
    global DISPLAY
    
    DISPLAY = DISPLAY + 1
    if DISPLAY > 3:
        DISPLAY = 0

    CALCDISPLAYshape()          # Make the DISPLAY shapes for the display colors
    UpdateText()                # Always Update


def BAudiostatus():
    global AUDIOstatus
    
    if (AUDIOstatus == 0):
        AUDIOstatus = 1
    else:
        AUDIOstatus = 0
    UpdateText()                # Always Update


def BFFTwindow():
    global FFTwindow
    
    FFTwindow = FFTwindow + 1
    if FFTwindow > 6:
        FFTwindow = 0

    CALCFFTwindowshape()        # Make the FFTwindowshape for the windowing function
    
    UpdateText()                # Always Update


def BStart():
    global FFTresults
    global RUNstatus
   
    if (RUNstatus == 0):
        RUNstatus = 1

    FFTresults = []
    UpdateText()                # Always Update


def BStop():
    global RUNstatus
    
    if (RUNstatus == 1):
        RUNstatus = 0
    elif (RUNstatus == 2):
        RUNstatus = 3
    elif (RUNstatus == 3):
        RUNstatus = 3
    elif (RUNstatus == 4):
        RUNstatus = 3
    Saveconfig("lopora.cfg")
    UpdateText()                # Always Update


def BContrast1():
    global Contrast

    Contrast = Contrast - 1
    if (Contrast < 0):
        Contrast = 0
    UpdateText()


def BContrast2():
    global Contrast
    
    Contrast = Contrast + 1
    if (Contrast > 25):
        Contrast = 25
    UpdateText()


def BBrightness1():
    global Brightness
    
    Brightness = Brightness - 1
    if (Brightness < -10):
        Brightness = -10

    CALCDISPLAYshape()          # Make the DISPLAY shapes for the display colors
    UpdateText()


def BBrightness2():
    global Brightness
    
    Brightness = Brightness + 1
    if (Brightness > 10):
        Brightness = 10

    CALCDISPLAYshape()          # Make the DISPLAY shapes for the display colors
    UpdateText()


def BAverage1():
    global FFTaverage

    FFTaverage = FFTaverage - 1
    if (FFTaverage < 1):
        FFTaverage = 1
    UpdateText()


def BAverage2():
    global FFTaverage

    FFTaverage = FFTaverage + 1
    if (FFTaverage > 10):
        FFTaverage = 10
    UpdateText()


def BNBlevel1():
    global NOISEblankerlevel
    
    NOISEblankerlevel = NOISEblankerlevel - 1
    if (NOISEblankerlevel < 0):
        NOISEblankerlevel = 0
    UpdateText()


def BNBlevel2():
    global NOISEblankerlevel
    
    NOISEblankerlevel = NOISEblankerlevel + 1
    if (NOISEblankerlevel > 5):
        NOISEblankerlevel = 5
    UpdateText()

   
def BStartfrequency():
    global RUNstatus
    global STARTfrequency
    
    if (RUNstatus != 0):
        showwarning("WARNING","Stop reception first")
        return()

    s = askstring("Start frequency: ","Value: " + str(STARTfrequency) + " Hz\n\nNew value:\n")
    
    if (s == None):             # If Cancel pressed, then None
        return()

    try:                        # Error if for example no numeric characters or OK pressed without input (s = "")
        v = int(s)
    except:
        s = "error"

    if s != "error":
        STARTfrequency = v
        SCREENclear()
    UpdateText()

   
def BAudiodevice():
    global RUNstatus
    
    if (RUNstatus != 0):
        showwarning("WARNING","Stop reception first")
        return()

    SELECTaudiodevice()         # Select an audio device        


def BSave():
    global RUNstatus 

    if (RUNstatus != 0):
        showwarning("WARNING","Stop reception first")
        return()
        
    filename = asksaveasfilename(filetypes=[("Setting","*.cfg"),("allfiles","*")])

    if (filename == None):              # No input, cancel pressed or an error
        filename = ""

    if (filename == ""):
        return()
    if filename[-4:] != ".cfg":
        filename = filename + ".cfg"
    Saveconfig(filename)                # Save the settings


def BRecall():
    global RUNstatus 
  
    if (RUNstatus != 0):
        showwarning("WARNING","Stop reception first")
        return()

    filename = askopenfilename(filetypes=[("Setting","*.cfg"),("allfiles","*")])

    if (filename == None):              # No input, cancel pressed or an error
        filename = ""

    if (filename == ""):
        return()

    Recallconfig(filename)              # Load configuration
    Saveconfig("lopora.cfg")            # Save configuration also as default that will be reloaded when the program starts
    SHOWtime()                          # Show the reception time per screen


def Bsnapshot():
    global FTPdir
    global FTPenabled
    global FTPhost
    global FTPuser
    global FTPpassword
    global SNAPshotenabled

    if (RUNstatus != 0):
        showwarning("WARNING","Stop reception first")
        return()

    SNAPshotenabled = askyesno("Enable save snapshot", "Enable save snapshot?",default = NO)

    FTPenabled = askyesno("Enable FTP upload", "Enable FTP upload?",default = NO)

    if FTPenabled == True:
        if FTPhost == "":
            FTPhost = askstring("FTP host: ","FTP host name:\n")

        if FTPuser == "":
            FTPuser = askstring("FTP user: ","FTP user name:\n")

        if FTPdir == "":
            FTPdir = askstring("FTP directory: ","FTP remote directory (press enter if none):\n")
                    
        if FTPpassword == "":
            FTPpassword = askstring("FTP password: ","FTP password:\n", show="*")
                    
    SETmessages()                       # Set the SNAPshot and FTPmessage text
    UpdateText()
    

def Btakesnap():
    MakeSnapshot()


# ============================================ Main routine ====================================================
    
def AUDIOin():   # Read the audio from the stream and store the data into the arrays
    global AUDIOdevin
    global AUDIOdevout
    global AUDIOsignal1
    global AUDIOstatus
    global DEBUG
    global RASPIterminalmode
    global RUNstatus
    global RXbuffer
    global RXbufferoverflow
    global SAMPLErate
    global SMPfft
    global STACKING
    global STACKinterval
    
    SCREENclear()
    if DEBUG == 2:
        print("Start AUDIOin()")

    while (True):                                               # MAIN LOOP
        time.sleep(0.01)                                        # Less CPU load
        PA = pyaudio.PyAudio()
        FORMAT = pyaudio.paInt16                                # Audio format 16 levels and 2 channels


        # STACKING > 0, wait for 0, 10, 20 ... 60 minute intervals if RUNstatus == 1
        if STACKING > 0 and RUNstatus == 1:                     # For Stacking, start at 0, 10, 20 ... 60 minute intervals
            minute = gmtime()[4]                                # Minutes

            while (minute % STACKinterval) == 0:                # Wait if minute is zero to prevent start in the middle of a minute
                time.sleep(0.01)                                # Less CPU load
                minute = gmtime()[4]                            # Minutes
                DoRootUpdate()                                  # Check controls etc.

            while (minute % STACKinterval) != 0 and RUNstatus == 1:    # Wait till minute is 0, 10, 20 ... 60 or till RUNstatus changed
                time.sleep(0.01)                                # Less CPU load
                minute = gmtime()[4]                            # Minutes
                DoRootUpdate()                                  # Check controls etc.


        # RUNstatus == 1 : Open Stream
        if (RUNstatus == 1):
            TRACESopened = 1
            AUDIOsignal1 = []
            INITIALIZEstart()                                   # Initialize variables

            try:
                chunkbuffer = int(SAMPLErate * 10)              # Fixed at 5 seconds, one value is 2x8bits=16 bits
                readsamples = int(SAMPLErate)                   # Samples to read, fixed at 0.5 seconds, one value is 2x8bits=16 bits
                
                stream = PA.open(format = FORMAT,
                    channels = TRACESopened, 
                    rate = SAMPLErate, 
                    input = True,
                    output = True,
                    frames_per_buffer = int(chunkbuffer),
                    input_device_index = AUDIOdevin,
                    output_device_index = AUDIOdevout)
                RUNstatus = 2
                RXbufferoverflow = True                         # Force overflow marker as buffer is started
            except:                                             # If error in opening audio stream, show error
                RUNstatus = 0
                txt = "Sample rate: " + str(SAMPLErate) + ", try a different sample rate.\nOr another audio device."
                if RASPIterminalmode == False:
                    showerror("Cannot open Audio Stream", txt)
                else:
                    txt = "ERROR! Cannot open Audio Stream. Sample rate: " + str(SAMPLErate) + ", try a different sample rate or audio device."
                    print(txt)
            

        # RUNstatus == 2: Reading audio data from soundcard
        if RUNstatus == 2:
            buffervalue = stream.get_read_available()           # Buffer reading testroutine

            try:
                if buffervalue > readsamples:                   # ADDED FOR RASPBERRY PI WITH ALSA, PERHAPS NOT NECESSARY WITH PULSE
                    RXbuffer = 100.0 * float(buffervalue) / chunkbuffer # Buffer filled in %. Will go up if PC too slow
                    signals = stream.read(readsamples)          # Read samples from the buffer

                    if (AUDIOstatus == 1):                      # Audio on
                            stream.write(signals, readsamples)
                            
                    # Conversion audio samples to values -32762 to +32767 (ones complement) and add to AUDIOsignal1
                    T1=time.time()                              # For time measurement of routines
                    AUDIOsignal1.extend(numpy.fromstring(signals, "Int16"))

                    if DEBUG == 2:
                        T2=time.time()
                        print("Conversion audio samples: " + str(T2-T1))
            except:
                RUNstatus = 4
                RXbufferoverflow = True                         # Buffer overflow at 2x chunkbuffer
                print("Audio buffer reset! ")


        # RUNstatus == 3: Stop
        # RUNstatus == 4: Stop and restart
        if (RUNstatus == 3) or (RUNstatus == 4):
            stream.stop_stream()
            stream.close()
            PA.terminate()
            if RUNstatus == 3:
                RUNstatus = 0                                   # Status is stopped 
            if RUNstatus == 4:
                RUNstatus = 1                                   # Status is (re)start

            AUDIOsignal1 = []                                   # Clear audio buffer
            
        DoRootUpdate()

        while len(AUDIOsignal1) > SMPfft:
            if DEBUG == 2:
                print("len(AUDIOsignal1): " + str(len(AUDIOsignal1)))

            UpdateAll()


def WAVin():   # Read the audio from the WAV file and store the data into the array and read data from the array
    global AUDIOdevin
    global AUDIOdevout
    global AUDIOsignal1
    global AUDIOstatus
    global DEBUG
    global FTPenabled
    global RUNstatus
    global RXbuffer
    global RXbufferoverflow
    global SAMPLErate
    global SCREENupdate
    global SMPfft
    global SNAPshotenabled
    global STACKING
    global WAVchannels
    global WAVfilename
    global WAVframes
    global WAVframerate
    global WAVinput
    global WAVsamplewidth
    global WAVsignal1
    global WAVsignal2


    STACKING = 0                                            # No stacking for WAV file mode
    FTPenabled = False                                      # No FTP upload for WAV file mode
    SNAPshotenabled = False                                 # No Snapshot savings in WAV file mode
    SCREENupdate = 1                                        # Update after each trace in WAV file mode
    
    while (True):                                           # Main loop

        # RUNstatus = 1 : Open WAV file
        if (RUNstatus == 1):
            
            WAVfilename = ASKWAVfilename()

            if (WAVfilename == ""):
                RUNstatus = 0
            else:
                WAVf = wave.open(WAVfilename, 'rb')
                WAVframes = WAVf.getnframes()
                # print("frames: " + str(WAVframes))
                WAVchannels = WAVf.getnchannels()
                # print("channels: " + str(WAVchannels))
                WAVsamplewidth = WAVf.getsampwidth()
                # print("samplewidth: " + str(WAVsamplewidth))
                WAVframerate = WAVf.getframerate()
                # print("framerate: " + str(WAVframerate))
                SAMPLErate = WAVframerate

                INITIALIZEstart()                           # Initialize variables

                signals = WAVf.readframes(WAVframes)        # Read the data from the WAV file and convert to WAVsignalx[]
                
                i = 0
                f = 0
                s = ""

                WAVsignal1 = []
                WAVsignal2 = []

                if (WAVsamplewidth == 1) and (WAVchannels == 1):
                    while (f < WAVframes):
                        s = str(struct.unpack('B', signals[i:(i+1)]))
                        v = int(s[1:-2]) - 128
                        WAVsignal1.append(v) 
                        WAVsignal2.append(0) 
                        i = i + 1
                        f = f + 1
                    
                if (WAVsamplewidth == 1) and (WAVchannels == 2):
                    while (f < WAVframes):
                        s = str(struct.unpack('B', signals[i:(i+1)]))
                        v = int(s[1:-2]) - 128
                        WAVsignal1.append(v) 
                        s = str(struct.unpack('B', signals[(i+1):(i+2)]))
                        v = int(s[1:-2])
                        WAVsignal2.append(v) 
                        i = i + 2
                        f = f + 1

                if (WAVsamplewidth == 2) and (WAVchannels == 1):
                    while (f < WAVframes):
                        s = str(struct.unpack('h', signals[i:(i+2)]))
                        v = int(s[1:-2])
                        WAVsignal1.append(v) 
                        WAVsignal2.append(0) 
                        i = i + 2
                        f = f + 1

                if (WAVsamplewidth == 2) and (WAVchannels == 2):
                    while (f < WAVframes):
                        s = str(struct.unpack('h', signals[i:(i+2)]))
                        v = int(s[1:-2])
                        WAVsignal1.append(v) 
                        s = str(struct.unpack('h', signals[(i+2):(i+4)]))
                        v = int(s[1:-2])
                        WAVsignal2.append(v) 
                        i = i + 4
                        f = f + 1

            WAVf.close()
            WAVpntr = 0                                     # Pointer to WAV array that has to be read
            SCREENclear()
            UpdateText()

            if RUNstatus == 1:
                RUNstatus = 2

            
        # RUNstatus = 2: Reading audio data from WAVsignalx array
        if (RUNstatus == 2):
            RXbuffer = 0                                    # Buffer filled in %. No overflow for WAV mode
            RXbufferoverflow = False
            readsamples = SAMPLErate
            n = 0

            if WAVinput == 1:
                while n < readsamples:
                    v = WAVsignal1[WAVpntr]
                    AUDIOsignal1.append(v)

                    WAVpntr = WAVpntr + 1
                    if WAVpntr >= len(WAVsignal1):
                        WAVpntr = 0

                    n = n + 1

            if WAVinput == 2:
                while n < readsamples:
                    v = WAVsignal2[WAVpntr]
                    AUDIOsignal1.append(v)

                    WAVpntr = WAVpntr + 1
                    if WAVpntr >= len(WAVsignal2):
                        WAVpntr = 0

                    n = n + 1


        if (RUNstatus == 3):
            RUNstatus = 0                                   # Status is stopped

        if (RUNstatus == 4):
            RUNstatus = 2                                   # Status is run

        # Update tasks and screens by TKinter 
        DoRootUpdate()

        while len(AUDIOsignal1) > SMPfft:
            UpdateAll()


def UpdateAll():        # Update Data, trace and screen
    DoFFT()             # Fast Fourier transformation, calls updatetrace and updatetext
    MakeTrace()         # Make the trace
   

def SCREENclear():      # Clear screen, make lines and reset FFTline
    global AUDIOsignal1
    global CANVASheight
    global CANVASwidth
    global FFTline
    global FFTresults
    global RUNstatus
    global THEimage


    # Clear data
    AUDIOsignal1 = []
    FFTresults = []
    FFTline = 0


    # Open a draw item for THEimage
    draw = ImageDraw.Draw(THEimage)


    # Delete all items on the screen
    draw.rectangle((0, 0, CANVASwidth+2,CANVASheight+2), fill="#000000")
    del draw

    CURSOR(0, CANVASwidth)                                          # Make the whole screen equal to the cursor content
    
    if RUNstatus == 2:
        RUNstatus = 4

    UpdateText()        # Update the text


def SCREENrefresh():    # Refresh the screen
    global DEBUG
    global DISPLAYimg
    global RASPIterminalmode
    global THEimage
    
    T1=time.time()                                                  # For time measurement of routines

    if RASPIterminalmode == False:
           DISPLAYimg.paste(THEimage)                               # Save to the Desktop if Desktop mode

    DoRootUpdate()    
    if DEBUG == 2:
        T2=time.time()
        print("SCREENrefresh: " + str(T2-T1))


def DoRootUpdate():     # Update idle tasks etc.
    global RASPIterminalmode

    if RASPIterminalmode == True:                                   # Exit if terminal mode, else continue
        return()
    ca.update_idletasks()
    ca.update()
    root.update_idletasks()                                         # Check controls etc.             
    root.update()

    
  
def DoFFT():            # Fast Fourier transformation and others like noise blanker and level for audio meter and time markers
    global AUDIOlevel
    global AUDIOsignal1
    global DEBUG
    global FFToverlap
    global FFTaverage
    global FFTline
    global FFTmemory
    global FFTresult
    global FFTwindowshape
    global GRH
    global HOURmarkers
    global MARKERtime
    global MARKERtype
    global NOISEblankeractive
    global NOISEblankerlevel
    global RUNstatus
    global RXbuffer
    global RXbuffermin
    global RXbuffermax
    global RXbufferoverflow
    global SAMPLErate
    global SCREENupdatecounter
    global SMPfft
    global SMPfftpwrTwo
    global STACKING
    global STACKinterval
    global STARTfrequency
    global STARTsample
    global STOPsample
    global TIMEmarkercnt
    global TRACEdate
    global TRACEh
    global TRACEm
    global TUNEDfrequency
    global Tupload
    global ZEROpadding
    global ZEROpaddingvalue
    global ZOOMfactor

    
    if DEBUG == 2:
        print("Start DoFFT()")

    T1=time.time()                                          # For time measurement of routine
    
    # Initialisation of variables
    MAXaudio = 32000.0                                      # MAXaudio is 32000 for a good soundcard, lower for one with a lower dynamic range

    AUDIOstep = float(SMPfft) / FFToverlap                  # Step for start of next FFT array
    AUDIOstep = int(AUDIOstep)

    FFTsignal = AUDIOsignal1[:SMPfft]                       # Take the first SMPfft samples from the stream
    AUDIOsignal1 = AUDIOsignal1[AUDIOstep:]                 # Delete the first n samples, n depends on FFToverlap

    # Time message at start
    if FFTline == 0:
        SCREENupdatecounter = 0
        T = gmtime()
        TRACEdate = strftime("%a, %d %b %Y %H:%M GMT", T)
        # TRACEdate = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
        TRACEh = T[3]
        TRACEm = T[4]
        MARKERtime = 0.0
        TIMEmarkercnt = 0


    # Reset statistics AUDIOlevel, RXbuffermin and RXbuffermax
    if SCREENupdatecounter == 0:                            # Reset if SCREENupdatecounter == 0
        AUDIOlevel = 0.0
        NOISEblankeractive = False                          # Reset Noiseblankeractive
        RXbuffermin = RXbuffer
        RXbuffermax = RXbuffer
    else:
        # Update RXbuffermin and RXbuffermax
        if RXbuffer < RXbuffermin:
            RXbuffermin = RXbuffer
        if RXbuffer > RXbuffermax:
            RXbuffermax = RXbuffer


    # Time markers and overflow markers
    TT = FFTline * float(AUDIOstep) / float(SAMPLErate)     # Trace Time, used for check of end of synchronized time interval
    
    MARKERtype = 0

    if FFTline == 0 or RXbufferoverflow == True:
        MARKERtype = 1                                      # 1 is long marker line as start marker or RX buffer overflow marker
        UpdateText()
        RXbufferoverflow = False                            # Reset RXbufferoverflow
    else:
        # Time markers, start with calculation of the trace time T2
        TM =  TT - MARKERtime                               # Start Time till next marker
        
        if HOURmarkers == True:                             # Hour markers
            if TM >= 1800:  
                MARKERtime = MARKERtime + 1800

                TRACEm = TRACEm + 30                        # Calculation of trace time
                while TRACEm >= 60:
                    TRACEh = TRACEh + 1
                    TRACEm = TRACEm - 60
                while TRACEh >= 24:
                    TRACEh = TRACEh - 24

                TIMEmarkercnt = TIMEmarkercnt + 1
                if (TIMEmarkercnt > 1):
                    TIMEmarkercnt = 0
                    MARKERtype = 2                          # 2 is hour marker
                else:
                    MARKERtype = 3                          # 3 is half hour marker                
        else:                                               # Minute markers
            if TM >= 60:
                MARKERtime = MARKERtime + 60

                TRACEm = TRACEm + 1                        # Calculation of trace time
                while TRACEm >= 60:
                    TRACEh = TRACEh + 1
                    TRACEm = TRACEm - 60
                while TRACEh >= 24:
                    TRACEh = TRACEh - 24
                
                TIMEmarkercnt = TIMEmarkercnt + 1
                if (TIMEmarkercnt > 9):
                    TIMEmarkercnt = 0
                    MARKERtype = 2                          # 2 is 10 minute marker
                else:
                    MARKERtype = 3                          # 3 is 1 minute marker                

    if STACKING > 0:                                        # Receive in time synchronized intervals and add screens for STACKING > 1
        if TT >= (STACKinterval * 60 - Tupload):            # End of synchronized interval for minute markers and 60 sec margin for calculations and upload
            MARKERtype = 9                                  
            

    # Convert list to numpy array REX for faster Numpy calculations
    REX = numpy.array(FFTsignal)                            # Make an arry of the list


    # Set Audio level display value
    MAXlvl = numpy.amax(REX) / MAXaudio                     # First check for maximum positive value
    if MAXlvl > AUDIOlevel:
        AUDIOlevel = MAXlvl

    MINlvl = numpy.amin(REX) / MAXaudio                     # Then check for minimum positive value
    MINlvl = abs(MINlvl)                                    # Make absolute
    if MINlvl > AUDIOlevel:
        AUDIOlevel = MINlvl


    # Noise blanker routine on REX before the FFT calculation. Delete the peaks in REX
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

    if DEBUG == 2:
        T2=time.time()
        print("FFTwindowing + NoiseBlanker: " + str(T2-T1))
    
    T1=time.time()                                          # For time measurement of routines


    # Zero padding of array for better interpolation of peak level of signals
    fftsamples = ZEROpaddingvalue * SMPfftpwrTwo            # Add zero's to the arrays


    # FFT with numpy 
    fftresult = numpy.fft.fft(REX, n=fftsamples)            # Do FFT+zeropadding till n=fftsamples with NUMPY
    ALL = fftresult                                         # ALL = Real + Imaginary part
    ALL = ALL[STARTsample:STOPsample]                       # Delete the unused samples that will not be displayed
    ALL = numpy.absolute(ALL)                               # Make absolute SQR(REX*REX + IMX*IMX) for VOLTAGE!

    Totalcorr = float(ZEROpaddingvalue) / fftsamples        # Make an amplitude correction for the zero padding and FFT samples used
    Totalcorr = float(SMPfftpwrTwo) / SMPfft * Totalcorr    # Make an amplitude correction for rounding the samples to the nearest power of 2
    FFTresult = Totalcorr * ALL

    if FFTaverage > 1:
        if FFTmemory[0] == -1:                              # Memory cleared
            FFTmemory = FFTresult               
        else:
            FFTresult = FFTmemory + (FFTresult - FFTmemory) / FFTaverage
            FFTmemory = FFTresult          
   
    if DEBUG == 2:
        T2=time.time()
        print("FFT calculation: " + str(T2-T1))
        

def UpdateText():
    global AUDIOlevel
    global AUDIOstatus
    global Brightness
    global CANVASheight
    global CANVASwidth
    global COLORaudiobar
    global COLORaudiomax
    global COLORaudiook
    global COLORfrequency
    global COLORcanvas
    global COLORtext
    global Contrast
    global DEBUG
    global DISPLAY
    global FFTaverage
    global FFTwindow
    global FFTbandwidth
    global FFTwindowname
    global FTPmessage
    global GRH
    global HOURmarkers
    global LoporaName
    global NOISEblankeractive
    global NOISEblankerlevel
    global RASPIcputemperature
    global RASPIterminalinfo
    global RUNstatus
    global RXbuffer
    global RXbuffermax
    global RXbuffermin
    global SAMPLErate
    global SMPfft
    global SMPfftpwrTwo
    global SNAPshotmessage
    global STARTfrequency
    global STATIONname
    global THEimage
    global TRACEdate
    global TUNEDfrequency
    global Vdiv
    global X0L
    global Y0T
    global ZOOMfactor

    
    T1=time.time()

    # Open a draw item for THEimage
    draw = ImageDraw.Draw(THEimage)


     # Delete text items on the screen
    draw.rectangle((0, GRH+Y0T+15, CANVASwidth+2,CANVASheight+2), fill=COLORcanvas)


    # Trace information
    txt = "Start at: " + TRACEdate + "    " + STATIONname
    x = X0L
    y = Y0T+GRH+20
    draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)

    if RASPIterminalinfo == True:
        print(txt)
  
    # Frequency information
    Flo = STARTfrequency
    Fpixel = (float(SAMPLErate / 2) / (SMPfftpwrTwo / 2 - 1)) * ZOOMfactor     # Frequency step per pixel
    Fhi = Flo + GRH * Fpixel 

    Ftxt = str(int(Flo * 10))
    Ftxt = Ftxt[:len(Ftxt)-1] + "." + Ftxt[-1:]

    txt = "Frequency range (Hz): " + Ftxt + " - " 

    Ftxt = str(int(Fhi * 10))
    Ftxt = Ftxt[:len(Ftxt)-1] + "." + Ftxt[-1:]

    txt = txt + Ftxt

    Fd = (Fhi - Flo) / Vdiv 

    Ftxt = str(int(Fd * 100))
    Ftxt = Ftxt[:len(Ftxt)-2] + "." + Ftxt[-2:]

    txt = txt + "    Hz/div: " + str(Vdiv)

    txt = txt + "    " + FFTwindowname
    txt = txt + "    Sample rate: " + str(SAMPLErate) + "    FFTsamples: " + str(SMPfft)

    if SMPfft != SMPfftpwrTwo:
        txt = txt + " (" + str(SMPfftpwrTwo) + ")"

    txt = txt + "    Bandwidth (mHz): " + str(FFTbandwidth) 

    x = X0L
    y = Y0T+GRH+39
    draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)


    # Soundcard level bargraph
    txt1 = "||||||||||||||||||||"                           # Bargraph
    le = len(txt1)                                          # Length of bargraph
    t = int(math.sqrt(AUDIOlevel) * le)

    if RASPIterminalinfo == True:
        txt = "Audio level (%): " + str(int(100 * AUDIOlevel))
        print(txt)

    n = 0
    txt = ""
    while(n < t and n < le):
        txt = txt + "|"
        n = n + 1

    x = X0L
    y = Y0T+GRH+55
    draw.text((x,y),txt1, font=TEXTfont, fill=COLORaudiobar)

    if AUDIOlevel >= 1.0:
        draw.text((x,y),txt, font=TEXTfont, fill=COLORaudiomax)
    else:
        draw.text((x,y),txt, font=TEXTfont, fill=COLORaudiook)

    # Place of text after bargraph
    w = TEXTfont.getsize(txt1)
    x = X0L + w[0] + 20
 
    # Runstatus and level information
    if (RUNstatus == 0) or (RUNstatus == 3):
        txt = "Stopped"
    else:
        txt = "Running"

    if AUDIOstatus == 1:
        txt = txt + "    Audio on"
    else:
        txt = txt + "    Audio off"
        
    txt = txt + "    Display " + str(DISPLAY) + "    C=" + str(Contrast) + "    B=" + str(Brightness)

    if FFTaverage > 1:
        txt = txt + "    AVG=" + str(FFTaverage)
    
    if NOISEblankerlevel == 0:
        txt = txt + "    Noise blanker off"
    else:
        txt = txt + "    Noise blanker level: " + str(NOISEblankerlevel)
        if NOISEblankeractive == True:                      # Noise blanker active
            txt = txt + "*"

    if RASPIcputemperature == True:
        try:
            temp = os.popen("vcgencmd measure_temp" ).readline()
            txt = txt + "    Raspberry Pi CPU " + temp
        except:
            pass

    txt = txt + "    Buffer (%): " + str(int(RXbuffermin / 2)) + " - "  + str(int(RXbuffermax / 2))

    y = Y0T+GRH+58
    draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)

    if RASPIterminalinfo == True:
        print(txt)

    x = X0L
    y = Y0T+GRH+77
    txt = FTPmessage + "    " + SNAPshotmessage
    draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)

    if RASPIterminalinfo == True:
        print(txt)


    # Program version
    w = TEXTfont.getsize(LoporaName)
    x = CANVASwidth - w[0] - 10
    draw.text((x,y),LoporaName, font=TEXTfont, fill=COLORtext)


    # Frequency scale
    Fpixel = (float(SAMPLErate / 2) / (SMPfftpwrTwo / 2 - 1)) * ZOOMfactor      # Frequency step per pixel
    Pdiv = Vdiv / Fpixel                                                        # Pixels per division

    FR = STARTfrequency
    i = GRH
    while (i > 0):
        text = str(FR)
        w = TEXTfont.getsize(text)
        x = CANVASwidth - w[0]
        y = i + Y0T - w[1] - 3
        xa = x + w[0] + 1
        ya = y + w[1]
        if y >= 0:
            draw.rectangle((x,y,xa,ya), fill=COLORcanvas)                       # Canvas color window
            draw.text((x,y),text, font=TEXTfont, fill=COLORfrequency)

        FR = FR + Vdiv
        i = i - Pdiv

    del draw            # Delete the draw item

    if DEBUG == 2:
        T2=time.time()
        print("UpdateText: " + str(T2-T1))
    
    SCREENrefresh()     # Refresh the screen


def MakeTrace():
    global AUDIOsignal1
    global CANVASheight
    global CANVASwidth
    global COLORcanvas
    global COLORtext
    global Contrast
    global DEBUG
    global DISPLAYblue
    global DISPLAYgreen
    global DISPLAYred
    global Dwidth
    global FFTline
    global FFTresult
    global GRH          # Screenheight
    global GRW          # Screenwidth
    global LOPshotnow
    global MARKERtype
    global RUNstatus
    global THEimage
    global TRACEh
    global TRACEm
    global X0L          # Left top X value
    global Y0T          # Left top Y value
    global SCREENupdate
    global SCREENupdatecounter
    global ZEROpadding
    global ZEROpaddingvalue
    global ZOOMfactor
    
    T1=time.time()
    
   
    # Open a draw item for THEimage
    draw = ImageDraw.Draw(THEimage)


    # Set the TRACEsize variable
    TRACEsize = len(FFTresult)                                              # Set the trace length, last two values are line and marker type
        
    X1 = int(X0L + FFTline * Dwidth)
    Y1 = Y0T + GRH                                                          # Start at bottom
          
    Cvalue = 2.0 ** (float(Contrast) / 2)                                   # Max. 1024x gain for contrast
    
    Dsample = 0                                                             # Pointer in FFTresult[]
    Dstep = ZEROpaddingvalue * ZOOMfactor                                   # Step for Data pointer
 
    n = 0
    while n < GRH:
        if (Dsample + Dstep) < TRACEsize:
            v = FFTresult[int(Dsample)]
            
            m = 1
            while m < Dstep:                                                # Peak value from more samples if zero padding or zoom active
                try:                                                        # Try for boundary overload error catching
                    v1 = FFTresult[int(Dsample+m)]
                except:
                    v1 = 0
                if v1 > v:
                    v = v1
                m = m + 1

            v = v * Cvalue                                                  # Multiply with Contrast and scaling factor
            if v > 999.0:
                v = 999.0

            i = int(v)

            clred = DISPLAYred[i]
            clgreen = DISPLAYgreen[i]
            clblue = DISPLAYblue[i]

            rgb = "#%02x%02x%02x" % (clred, clgreen, clblue)

            draw.rectangle((X1, Y1, (X1+Dwidth), (Y1-1)), fill=rgb)         # In frequency range

        else:
            draw.rectangle((X1, Y1, (X1+Dwidth), (Y1-1)), fill="#606060")   # Out of frequency range

        Y1 = Y1 - 1
        Dsample = Dsample + Dstep

        n = n + 1


    # Time markers
    Y1 = GRH + Y0T
    if MARKERtype == 1:                                                     # Start marker or buffer overflow
        draw.rectangle(((X1-2), Y1-20, X1, Y1), fill="red")
    if MARKERtype == 2:                                                     # Long marker
        draw.rectangle(((X1-2), Y1-10, X1, Y1), fill="red")
    if MARKERtype == 3:                                                     # Short marker (1 minute marker)
        draw.rectangle(((X1-2), Y1-5, X1, Y1), fill="red")


    # Display time stamps
    if MARKERtype > 0 and MARKERtype < 4:
        txt1 = str(TRACEh)
        if len(txt1) < 2:
            txt1 = "0" + txt1
        txt2 = str(TRACEm)
        if len(txt2) < 2:
            txt2 = "0" + txt2
        txt = txt1 + ":" + txt2

        x = X1 - 3
        y = Y1 + 1

        w = TEXTfont.getsize("88:88")                                       # Maximum size time stamp
        xa = x + w[0] + 1
        ya = y + w[1] + 1
        draw.rectangle((x,y,xa,ya), fill=COLORcanvas)                       # Delete time stamp
        if xa <= CANVASwidth:
            draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)

    del draw                                                                # Delete the draw item


    # Cursor line
    CURSOR(X1 + 2*Dwidth, 2*Dwidth)                                         # Make cursor line with width = 2*Dwidth
    

    # Check for SCREENrefresh or FTP upload and snapshot
    SCREENready = False

    if MARKERtype == 9:                                                     # Synchronized time interval end
        SCREENready = True

    FFTline = FFTline + 1
    SCREENupdatecounter = SCREENupdatecounter + 1
        
    if FFTline >= GRW/Dwidth:
        SCREENready = True

    if DEBUG == 2:
        T2=time.time()
        print("MakeTrace: " + str(T2-T1))
      
    if SCREENready == True:                                                 # Screen full, activate snapshot
        FFTline = 0
        SCREENupdatecounter = 0
        AUDIOsignal1 = []                                                   # Clear audio buffer
        RUNstatus = 4                                                       # Stop and restart
        CURSOR(X1 + 2*Dwidth + 2*Dwidth, CANVASwidth)                       # Make the remaining of the screen equal to the cursor line content
        UpdateText()                                                        # Update the text to reprint the frequency scale
        MakeSnapshot()                                                      # Take snapshot and do FTP upload and save if enabled
    else:
        if SCREENupdatecounter >= SCREENupdate:
            SCREENupdatecounter = 0
            UpdateText()                                                    # Update the text
            if LOPshotnow == True:                                          # If True then a file is saved at each screen update for screen checks via remote connections
                THEimage.save("lopshotnow.jpg", "JPEG", quality=80)         


def CURSOR(thisline, thiswidth):   # Make a cursor on this line with this width
    global CANVASheight
    global CANVASwidth
    global GRH          # Screenheight
    global GRW          # Screenwidth
    global RUNstatus
    global SAMPLErate
    global SMPfft
    global SMPfftpwrTwo
    global THEimage
    global Vdiv
    global X0L          # Left top X value
    global Y0T          # Left top Y value
    global ZOOMfactor


    # Open a draw item for THEimage
    draw = ImageDraw.Draw(THEimage)


    # Cursor line black background
    X1 = thisline
    X2 = thisline + thiswidth

    if X2 > CANVASwidth:
        X2 = CANVASwidth
  
    draw.rectangle((X1, Y0T, (X2), (Y0T+GRH)), fill="#000000")


    # Draw horizontal grid lines
    Fpixel = (float(SAMPLErate / 2) / (SMPfftpwrTwo / 2 - 1)) * ZOOMfactor      # Frequency step per pixel
    Pdiv = Vdiv / Fpixel                                                        # Pixels per division

    i = GRH
    while (i > 0):
        y = Y0T + int(i) - 1                                                    # -1 for correction thickness lowest line
        draw.rectangle((X1, y-1, X2,y+1), fill="red") 
        i = i - Pdiv

    del draw


def INITIALIZEstart():
    global FFTmemory
    global GRH
    global SAMPLErate
    global SMPfftpwrTwo
    global STARTfrequency
    global STARTsample
    global STOPsample
    global TUNEDfrequency
    global ZEROpaddingvalue
    global ZOOMfactor

    print("Initialize start values of variables")

    # First some subroutines to set specific variables
    CALCSMPfftpwrTwo()
    CALCFFTwindowshape()
    CALCDISPLAYshape()

    FFTmemory[0] = -1                                       # Clear the memory for averaging
    
    # Calculate start en stop sample that will be displayed and delete the unused samples
    ZEROpaddingvalue = int((2 ** ZEROpadding) + 0.5)
    fftsamples = ZEROpaddingvalue * SMPfftpwrTwo            # Add zero's to the arrays

    Fsample = float(SAMPLErate/2) / (fftsamples/2 - 1)      # Frequency step per sample 
    Flo = STARTfrequency - TUNEDfrequency                   # The audio frequency to start with
    STARTsample = Flo / Fsample                             # First sample in FFTresult[] that is used
    STARTsample = int(STARTsample)

    DPsamples = ZOOMfactor * ZEROpaddingvalue               # Number of samples per display-pixel
    STOPsample = float(DPsamples) * GRH + STARTsample + 4   # The last sample              
    STOPsample = int(STOPsample)

    MAXsample = fftsamples / 2                              # Just an out of range check
    if STARTsample > (MAXsample - 1):
        STARTsample = MAXsample - 1

    if STOPsample > MAXsample:
        STOPsample = MAXsample


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

    print("Calculate FFT window shapes")

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

    # m = 0                                       # For calculation of correction factor, furhter no function

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
              
    print("Calculate Display brightness curves")
              
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
        

def SHOWtime():                                     # Show the reception time for one screen
    global Dwidth
    global FFToverlap
    global GRW
    global SAMPLErate


    t = float(SMPfft) / SAMPLErate / FFToverlap     # Calculate Time per line in seconds
    t = t * GRW / Dwidth                            # Calculate Time per screen in seconds

    Ttxt = str(int(t / 6))
    Ttxt = Ttxt[:len(Ttxt)-1] + "." + Ttxt[-1:]
    
    showinfo("Reception time","Reception time for one screen:\n" + Ttxt + " minutes")     # show Time per screen in minutes 


def Saveconfig(filename):               # Save the configuration
    global Brightness
    global Contrast
    global DISPLAY
    global Dwidth
    global FFTaverage
    global FFToverlap
    global FFTwindow
    global NOISEblankerlevel
    global SAMPLErate
    global SCREENupdate
    global SMPfft
    global STACKING
    global STARTfrequency
    global STATIONname 
    global TUNEDfrequency
    global Vdiv
    global ZEROpadding
    global ZOOMfactor

    print("Save config: " + filename)
              
    Wfile = open(filename,'w')          # output file setting

    S = ""
    while len(S) < 25:
        S = S + " "

    txt = "LOPORA CONFIGURATION FILE\n"
    Wfile.write(txt)

    # Fixed
    txt = STATIONname + "\n"
    Wfile.write(txt)

    # Fixed
    txt = str(int(SAMPLErate))
    txt = txt + S[len(txt):] + "Sample rate of down sampled audio stream\n"
    Wfile.write(txt)

    # Fixed
    txt = str(int(ZEROpadding))
    txt = txt + S[len(txt):] + "Zero padding for interpolation between FFT points (power of 2, default 1, 0 for slow PC's, 2 for faster PC's)\n"
    Wfile.write(txt)

    # Fixed
    txt = str(ZOOMfactor)
    txt = txt + S[len(txt):] + "Zoom-out factor default 1, 2 for larger frequency range on screen\n"
    Wfile.write(txt)

    # Fixed
    txt = str(int(SMPfft))
    txt = txt + S[len(txt):] + "Number of FFT samples\n"
    Wfile.write(txt)

    # Fixed
    txt = str(int(FFTaverage))
    txt = txt + S[len(txt):] + "Average n traces, (2 to 10, 1 is off)\n"
    Wfile.write(txt)

    # Fixed
    txt = str(int(TUNEDfrequency))
    txt = txt + S[len(txt):] + "Tuning frequency of the receiver in Hz\n"
    Wfile.write(txt)

    # Fixed
    txt = str(int(SCREENupdate))
    txt = txt + S[len(txt):] + "Screen update per n FFT traces (to save processing time for screen update)\n"
    Wfile.write(txt)

    # Fixed
    txt = str(int(Vdiv))
    txt = txt + S[len(txt):] + "Hz per division\n"
    Wfile.write(txt)

    # Fixed
    txt = str(float(FFToverlap))
    txt = txt + S[len(txt):] + "FFT overlap (default=2, 3 for fast PC's), overlap of arrays of FFT samples\n"
    Wfile.write(txt)

    # Fixed
    txt = str(int(Dwidth))
    txt = txt + S[len(txt):] + "Speed control by setting the width of a pixel (integer, default=1, set to 2 or 3 for wider screen pixels)\n"
    Wfile.write(txt)

    # Changeable in program
    txt = str(Contrast)
    txt = txt + S[len(txt):] + "Contrast (0 to 25)\n"
    Wfile.write(txt)

    # Changeable in program
    txt = str(Brightness)
    txt = txt + S[len(txt):] + "Brightness (-6 to + 6)\n"
    Wfile.write(txt)
    
    # Changeable in program
    txt = str(int(FFTwindow))
    txt = txt + S[len(txt):] + "FFTwindow 0=None(B=1) 1=Cos(B=1.24) 2=Tri(B=1.33) 3=Han(B=1.5) 4=Bla(B=1.73) 5=Nut(B=2.02) 6=Flat(B=3.77)\n"
    Wfile.write(txt)

    # Changeable in program
    txt = str(int(STARTfrequency))
    txt = txt + S[len(txt):] + "Start frequency, reception frequency at bottom of screen in Hz\n"
    Wfile.write(txt)
 
    # Changeable in program
    txt = str(int(NOISEblankerlevel))
    txt = txt + S[len(txt):] + "Noise blanker level (0 to 5, 0 is off)\n"
    Wfile.write(txt)
 
    # Changeable in program
    txt = str(int(DISPLAY))
    txt = txt + S[len(txt):] + "Display compression factor 0 - 3\n"
    Wfile.write(txt)

    # NOT Changeable in program
    txt = str(int(STACKING))
    txt = txt + S[len(txt):] + "STACKING > 0 for time synchronized rx, STACKING > 1 for stacking of N screens\n"
    Wfile.write(txt)

    Wfile.close()           # Close the file


def Recallconfig(filename):
    global Brightness
    global Contrast
    global DISPLAY
    global Dwidth
    global FFTaverage
    global FFToverlap
    global FFTwindow
    global NOISEblankerlevel
    global SAMPLErate
    global SCREENupdate
    global SMPfft
    global STACKING
    global STATIONname 
    global STARTfrequency
    global TUNEDfrequency
    global Vdiv
    global ZEROpadding
    global ZOOMfactor

    print("Recall config: " + filename)
              
    try:
        Rfile = open(filename,'r')      # open the input file with settings
    except:
        return()

    try:
        txt = Rfile.readline()          # read the first line, do nothing with it, it is just a description
    except:
        pass
        
    try:
        txt = Rfile.readline()          # read the next line
        STATIONname = txt[0:-1]         # delete carriage return by [0:-1] addition
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        SAMPLErate = int(txt[:20])
        if SAMPLErate < 1200:
            SAMPLErate = 1200
        if SAMPLErate > 48000:
            SAMPLErate = 48000
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        ZEROpadding = int(txt[:20])
        if ZEROpadding < 0:
            ZEROpadding = 0
        if ZEROpadding > 5:
            ZEROpadding = 5
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        ZOOMfactor = float(txt[:20])
        if ZOOMfactor < 0.1:
            ZOOMfactor = 0.1
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        SMPfft = int(txt[:20])
        if SMPfft < 1024:
            SMPfft = 1024
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        FFTaverage = int(txt[:20])
        if FFTaverage < 1:
            FFTaverage = 1
        if FFTaverage > 10:
            FFTaverage = 10
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        TUNEDfrequency = int(txt[:20])
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        SCREENupdate = int(txt[:20])
        if SCREENupdate < 1:
            SCREENupdate = 1
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        Vdiv = int(txt[:20])
        if Vdiv < 1:
            Vdiv = 1
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        FFToverlap = float(txt[:20])
        if FFToverlap < 1:
            FFToverlap = 1
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        Dwidth = int(txt[:20])
        if Dwidth < 1:
            Dwidth = 1
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        Contrast = int(txt[:20])
        if Contrast < 0:
            Contrast = 0
        if Contrast > 25:
            Contrast = 25        
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        Brightness = int(txt[:20])
        if Brightness < -10:
            Brightness = -10
        if Brightness > 10:
            Brightness = 10
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        FFTwindow = int(txt[:20])
        if FFTwindow < 0:
            FFTwindow = 0
        if FFTwindow > 6:
            FFTwindow = 6
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        STARTfrequency = int(txt[:20])
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        NOISEblankerlevel = int(txt[:20])
        if NOISEblankerlevel < 0:
            NOISEblankerlevel = 0
        if NOISEblankerlevel > 5:
            NOISEblankerlevel = 5
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        DISPLAY = int(txt[:20])
        if DISPLAY < 0:
            DISPLAY = 0
        if DISPLAY > 3:
            DISPLAY = 3
    except:
        pass

    try:
        txt = Rfile.readline()          # read the next line
        STACKING = int(txt[:20])
        if STACKING < 0:
            STACKING = 0
        if STACKING > 5:                # Can be increased, depending on memory size
            STACKING = 5
    except:
        pass

    Rfile.close()                       # Close the file

    INITIALIZEstart()
    SCREENclear()


def MakeSnapshot():                     # Take snapshot and Save or FTP upload
    global FTPenabled
    global SNAPshotenabled
    global STACKING
    global WAVenabled

    if STACKING > 1:
        MAKEaveragestack()
        MAKEpeakstack()
        SHIFTstack()
    if SNAPshotenabled == True:
        DOsnapshot()
    if FTPenabled == True:
        if WAVenabled == True:
            WAVrecord()
        FTPupload()        


def MAKEaveragestack():
    global COLORcanvas
    global DEBUG
    global GRH
    global GRW
    global STACKING
    global STATIONname
    global THEimage
    global X0L
    global Y0T


    T1=time.time()

    if STACKING < 2:                                        # Extra test, averaging only if STACKING > 1
        return
    
    THEimage.save("lopstack0.bmp", "BMP")

    im = []
    n = 0
    while n < STACKING:                                     # Open the pictures
        filename = "lopstack" + str(n) + ".bmp"
        try:
            im.append(Image.open(filename))                 # Floating point not supported by Chops
        except:
            im.append(Image.open("lopstack0.bmp"))
        n = n + 1 

    imav = im[0].copy()                                     # Make an image immav from im[0] for the average function

    n = 1
    while n < STACKING:                                     # The average function for the stacking
        alpha = 1.0 / (n + 1)                               # Blend factor, n + 1 as picture 1 = im[0]!
        imav = Image.blend(imav, im[n], alpha)              # Blend the pictures for average function
        n = n + 1

    draw = ImageDraw.Draw(imav)                                                     # Open a draw item
    draw.rectangle((0, GRH+Y0T+1, CANVASwidth+2,CANVASheight+2), fill=COLORcanvas)  # Delete text items on the screen
    txt = "Stacking of " + str(STACKING) + " screens, average values " + strftime("%a, %d %b %Y %H:%M GMT", gmtime())
    txt = txt  + "    " + STATIONname
    x = X0L
    y = Y0T+GRH+15
    draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)                             # Draw the text
    del draw

    imav.save("lopshotav.jpg", "JPEG", quality=80)          # Quality between 0-100
    imav.save("lopshotav.bmp", "BMP")                       # Save the picture also as BMP for comparision with JPG

    if DEBUG == 2:
        T2=time.time()
        print("MAKEaveragestack: " + str(T2-T1))


def MAKEpeakstack():
    global COLORcanvas
    global DEBUG
    global GRH
    global GRW
    global STACKING
    global STATIONname
    global THEimage
    global X0L
    global Y0T


    T1=time.time()

    THEimage.save("lopstack0.bmp", "BMP")

    im = []
    n = 0
    while n < STACKING:                                     # Open the pictures
        filename = "lopstack" + str(n) + ".bmp"
        try:
            im.append(Image.open(filename))
        except:
            im.append(Image.open("lopstack0.bmp"))
        n = n + 1 

    impk = im[0].copy()                                     # Make an image immpk from im[1] for the peak function

    n = 1
    while n < STACKING:                                     # The peak and average function for the stacking
        impk = ImageChops.lighter(im[n], impk)              # Add the pictures for lighter, peak funtion
        n = n + 1

    draw = ImageDraw.Draw(impk)                                                     # Open a draw item
    draw.rectangle((0, GRH+Y0T+1, CANVASwidth+2,CANVASheight+2), fill=COLORcanvas)  # Delete text items on the screen
    txt = "Stacking of " + str(STACKING) + " screens, peak values " + strftime("%a, %d %b %Y %H:%M GMT", gmtime())
    txt = txt  + "    " + STATIONname
    x = X0L
    y = Y0T+GRH+15
    draw.text((x,y),txt, font=TEXTfont, fill=COLORtext)                             # Draw the text
    del draw

    impk.save("lopshotpk.jpg", "JPEG", quality=80)          # Quality between 0-100
    impk.save("lopshotpk.bmp", "BMP")                       # Save the picture also as BMP for comparision with JPG

    if DEBUG == 2:
        T2=time.time()
        print("MAKEpeakstack: " + str(T2-T1))


def SHIFTstack():
    global DEBUG
    global STACKING
    global THEimage


    T1=time.time()

    THEimage.save("lopstack0.bmp", "BMP")

    im = []
    n = 0
    while n < STACKING:                                     # Open the pictures
        filename = "lopstack" + str(n) + ".bmp"
        try:
            im.append(Image.open(filename))
        except:
            im.append(Image.open("lopstack0.bmp"))
        n = n + 1 

    n = STACKING - 1
    while n >= 0 :                                          # Save the pictures one higher in the picture shift register
        filename = "lopstack" + str(n + 1) + ".bmp"
        im[n].save(filename, "BMP")
        n = n - 1 

    if DEBUG == 2:
        T2=time.time()
        print("SHIFTstack: " + str(T2-T1))


def DOsnapshot():                                           # Make snapshot and save it to file
    global DEBUG
    global SNAPshotmessage
    global STACKING
    global THEimage

    T1=time.time()

    # Make snapshot message
    tme =  strftime("%Y%b%d-%H%M%S", gmtime())              # The time
    filename = "lopshot1-" + tme
    filename = filename + ".jpg"
    # filename = filename + ".bmp"
    # filename = filename + ".png"

    SNAPshotmessage = "Last snapshot: " + filename
    UpdateText()                                            # Set the snapshot message before saving THEimage 


    # Save the screen image                   
    THEimage.save(filename, "JPEG", quality=80)             # Quality between 0-100
    # THEimage.save(filename, "BMP")
    # THEimage.save(filename, "PNG")

    if STACKING > 1:
        filename = "lopshotpk-" + tme + ".jpg"
        im = Image.open("lopshotpk.bmp")
        im.save(filename, "JPEG", quality=80)               # Quality between 0-100

        filename = "lopshotav-" + tme + ".jpg"
        im = Image.open("lopshotav.bmp")
        im.save(filename, "JPEG", quality=80)               # Quality between 0-100

    if DEBUG == 2:
        T2=time.time()
        print("DOsnapshot: " + str(T2-T1))

       
def WAVrecord():                                            # Make audio snapshot and upload it with FTP
    global SAMPLErate
    
    RECORDtime = 10                                         # 10 seconds record time
    RATE = 4800                                             # The sample rate of the WAV file
    # RATE = SAMPLErate                                       # The alternative sample rate of the WAV file
    
    FORMAT = pyaudio.paInt16
    CHANNELS = 1                                            # Only one audio channel
    chunk = RATE                                            # The audio buffer size (1 second)

    PB = pyaudio.PyAudio()

    stream = PB.open(format = FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    frames_per_buffer = chunk,
                    input_device_index = None)

    sound = []
    n = 0
    while n < RECORDtime * RATE / chunk:
        data = stream.read(chunk)
        sound.append(data)
        # print("recording")
        n = n + 1

    stream.close()
    PB.terminate()

    # write data to WAVE file
    data = ''.join(sound)

    wf = wave.open("lopsound.wav", 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(PB.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()


def FTPupload():                                                # Upload the files with FTP
    global ARCHIVEfiles
    global DEBUG
    global FTPdir
    global FTPhost
    global FTPmessage
    global FTPpassword
    global FTPuser
    global Remote
    global STACKING
    global STACKinterval
    global THEimage
    global WAVenabled

    T1=time.time()

    ftp = None

    # Make FTP message
    filename =  "lopshot1.jpg"                                  # This is the normal default grabber picture
    # filename =  "lopshot1.bmp"                                # Do not use this, too large file, it was just an experiment
    # filename =  "lopshot1.png"                                # Do not use this, too large file, it was just an experiment

    THEtime = strftime("%H:%M:%S GMT", gmtime())                    
    FTPmessage = "Last FTP upload: " + filename + " at " + THEtime


    # Save all 3 versions for comparision purposes, only one will be uploaded
    THEimage.save("lopshot1.bmp", "BMP")                        # Save the BMP version
    THEimage.save("lopshot1.jpg", "JPEG", quality=80)           # Save the JPEG version Quality between 0-100
    THEimage.save("lopshot1.png", "PNG")                        # Save the PNG version
    

    # Make an FTP connection and upload the file
    fup = open(filename, 'rb')                                  # Open the file of the picture to be uploaded

    if ARCHIVEfiles == True:                                    # Make the archive file name "lopshot1-1.jpg" to "lopshot1-72.jpg"
        uu = THEtime[0:2]
        mm = THEtime[3:5]
        t = 60 * int(uu) + int(mm) + 5                          # Do +5 to be in the correct 10 minute interval
        t = int (t / STACKinterval) + 1                         # Make the number 1 - 72
        while t > 72:
            t = t - 72
        ARCHIVEname = "lopshot1-" + str(t) + ".jpg"             # The ARCHIVE file name "lopshot1-1.jpg" to "lopshot1-72.jpg"
        
    try:
        # ftp = ftplib.FTP(FTPhost, FTPuser, FTPpassword)         # Open the FTP connection for file uploading with the default time out, works OK for me
        ftp = ftplib.FTP(FTPhost, FTPuser, FTPpassword, "", 10) # Open the FTP connection for file uploading with a time out, did avoid some problems for others
        
        if DEBUG > 0:
            print("Connected and logged in to FTP host for snapscreen upload")

        if FTPdir != "":
            ftp.cwd(FTPdir)
            if DEBUG > 0:
                print("Changed to remote directory: " + FTPdir)

        fup = open(filename, 'rb')                              # Open the file of the picture to be uploaded
        ftp.storbinary("STOR " + filename, fup, 8192)           # Store the picture
        fup.close()
        
        if DEBUG > 0:
            print (filename + " uploaded")

        if ARCHIVEfiles == True and STACKING > 0:               # Only when time synchronized reception
            fup = open(filename, 'rb')                          # Open the file of the picture to be uploaded
            ftp.storbinary("STOR " + ARCHIVEname, fup, 8192)    # Store the picture
            fup.close()
            
            if DEBUG > 0:
                print (ARCHIVEname + " uploaded")
            
        if STACKING > 1:
            fup = open("lopshotpk.jpg", 'rb')                   # Open the file of the picture to be uploaded
            ftp.storbinary("STOR lopshotpk.jpg", fup, 8192)     # Store the stacking peak picture
            fup.close()
            if DEBUG > 0:
                print("lopshotpk.jpg uploaded")
            fup = open("lopshotav.jpg", 'rb')                   # Open the file of the picture to be uploaded
            ftp.storbinary("STOR lopshotav.jpg", fup, 8192)     # Store the stacking average picture
            fup.close()
            if DEBUG > 0:
                print("lopshotav.jpg uploaded")

        if WAVenabled == True:
            fup = open("lopsound.wav", 'rb')                    # Open the WAV file to be uploaded
            ftp.storbinary("STOR lopsound.wav", fup, 8192)      # Store the WAV file
            fup.close()
            if DEBUG > 0:
                print("lopsound.wav uploaded")
                
    except:
        txt = strftime("%H:%M:%S GMT", gmtime())
        FTPmessage = "FTP upload FAILED at " + txt
        if DEBUG > 0:
            print(FTPmessage)


    # Remote configure file available?
    if Remote == True:
        Saveconfig("lopold.cfg")                                # Save the configuration

        try:
            fcp = open("lopold.cfg", 'rb')
            ftp.storbinary("STOR lopold.cfg", fcp, 8192)        # Upload the old configuration to the FTP server
            fcp.close()  
        except:
            pass

        try:
            fdwn = open("lopnew.cfg", 'wb')                     # Try to download a new configuration from the FTP server
            ftp.retrbinary("RETR lopnew.cfg", fdwn.write)
            ftp.delete("lopnew.cfg")                            # Delete a new configuration on the FTP server
            fdwn.close()
            Recallconfig("lopnew.cfg")                          # Set the settings of the new configuration file "lopnew.cfg"
            Saveconfig("lopora.cfg")                            # Save configuration also as default that will be reloaded when the program starts
        except:
            pass

        try:                                                    # Close if still open due to FTP errors
            fdwn.close()
        except:
            pass

        try:
            os.remove("lopnew.cfg")                             # Try to remove lopnew.cfg from the directory if exist
        except:
            pass

    try:
        if ftp:
            ftp.close()
    except:
        pass

    UpdateText()

    THEtime = strftime("%H:%M:%S GMT", gmtime())                    
    print("FTP ready: " + THEtime)

    if DEBUG == 2:
        T2=time.time()
        print("FTPupload: " + str(T2-T1))


def SELECTaudiodevice():        # Select an audio device
    global AUDIOdevin
    global AUDIOdevout

    PA = pyaudio.PyAudio()
    ndev = PA.get_device_count()

    n = 0
    ai = ""
    ao = ""
    while n < ndev:
        s = PA.get_device_info_by_index(n)
        # print(n, s)
        if s['maxInputChannels'] > 0:
            ai = ai + str(s['index']) + ": " + s['name'] + "\n"
        if s['maxOutputChannels'] > 0:
            ao = ao + str(s['index']) + ": " + s['name'] + "\n"
        n = n + 1
    PA.terminate()

    AUDIOdevin = None
    
    s = askstring("Device","Select audio INPUT device:\nPress Cancel for Windows Default\n\n" + ai + "\n\nNumber: ")
    if (s != None):             # If Cancel pressed, then None
        try:                    # Error if for example no numeric characters or OK pressed without input (s = "")
            v = int(s)
        except:
            s = "error"

        if s != "error":
            if v < 0 or v > ndev:
                v = 0
            AUDIOdevin = v

    AUDIOdevout = None

    s = askstring("Device","Select audio OUTPUT device:\nPress Cancel for Windows Default\n\n" + ao + "\n\nNumber: ")
    if (s != None):             # If Cancel pressed, then None
        try:                    # Error if for example no numeric characters or OK pressed without input (s = "")
            v = int(s)
        except:
            s = "error"

        if s != "error":
            if v < 0 or v > ndev:
                v = 0
            AUDIOdevout = v


def SETmessages():                      # Set the SNAPshotmessage and the FTPmessage
    global FTPenabled
    global FTPmessage
    global SNAPshotenabled
    global SNAPshotmessage

    if SNAPshotenabled == True:
        SNAPshotmessage = "Save snapshot enabled"
    else:
        SNAPshotmessage = "Save snapshot disabled"
        
    if FTPenabled == True:
        FTPmessage = "FTP upload enabled"
    else:
        FTPmessage = "FTP upload disabled"


def ASKWAVfilename():
    filename = askopenfilename(filetypes=[("WAVfile","*.wav"),("allfiles","*")])

    if (filename == None):              # No input, cancel pressed or an error
        filename = ""

    if (filename == ""):
        return(filename)
    
    if filename[-4:] != ".wav":
        filename = filename + ".wav"

    return(filename)

# ================ Make Screen ==========================
LoporaName = "LOPORAv03d.py(w) (25-08-2017): QRSS reception"


if RASPIterminalmode == False:                                      # No terminal mode but Desktop mode, do install the Desktop screen
    root=Tk()
    root.title(LoporaName)

    frame2 = Frame(root, background="blue", borderwidth=5, relief=RIDGE)
    frame2.pack(side=LEFT, expand=1, fill=Y)

    frame1 = Frame(root, background="blue", borderwidth=5, relief=RIDGE)
    frame1.pack(side=LEFT, expand=1, fill=X, anchor=NW)

    ca = Canvas(frame1, width=CANVASwidth, height=CANVASheight, background = COLORcanvas)
    ca.pack(side=TOP)

    # Top buttons
    b = Button(frame2, text="Start", width=Buttonwidth, command=BStart)
    b.pack(side=TOP, padx=1, pady=2)

    b = Button(frame2, text="Stop", width=Buttonwidth, command=BStop)
    b.pack(side=TOP, padx=1, pady=2)

    b = Button(frame2, text="Contrast+", width=Buttonwidth, command=BContrast2)
    b.pack(side=TOP, padx=1, pady=2)

    b = Button(frame2, text="Contrast-", width=Buttonwidth, command=BContrast1)
    b.pack(side=TOP, padx=1, pady=2)

    b = Button(frame2, text="Brightness+", width=Buttonwidth, command=BBrightness2)
    b.pack(side=TOP, padx=1, pady=2)

    b = Button(frame2, text="Brightness-", width=Buttonwidth, command=BBrightness1)
    b.pack(side=TOP, padx=1, pady=2)

    b = Button(frame2, text="Average+", width=Buttonwidth, command=BAverage2)
    b.pack(side=TOP, padx=1, pady=2)

    b = Button(frame2, text="Average-", width=Buttonwidth, command=BAverage1)
    b.pack(side=TOP, padx=1, pady=2)

    b = Button(frame2, text="FFTwindow", width=Buttonwidth, command=BFFTwindow)
    b.pack(side=TOP, padx=1, pady=2)

    b = Button(frame2, text="Noise blanker+", width=Buttonwidth, command=BNBlevel2)
    b.pack(side=TOP, padx=1, pady=2)

    b = Button(frame2, text="Noise blanker-", width=Buttonwidth, command=BNBlevel1)
    b.pack(side=TOP, padx=1, pady=2)

    b = Button(frame2, text="Audio on/off", width=Buttonwidth, command=BAudiostatus)
    b.pack(side=TOP, padx=1, pady=2)

    b = Button(frame2, text="Display", width=Buttonwidth, command=BDisplay)
    b.pack(side=TOP, padx=1, pady=2)

    b = Button(frame2, text="Reset screen", width=Buttonwidth, background="red", command=SCREENclear)
    b.pack(side=TOP, padx=1, pady=2)

    # Bottom buttons
    b = Button(frame2, text="Take Snap", width=Buttonwidth, background="red", command=Btakesnap)
    b.pack(side=BOTTOM, padx=1, pady=2)

    b = Button(frame2, text="Snapshot", width=Buttonwidth, command=Bsnapshot)
    b.pack(side=BOTTOM, padx=1, pady=2)

    b = Button(frame2, text="Save setting", width=Buttonwidth, command=BSave)
    b.pack(side=BOTTOM, padx=1, pady=2)

    b = Button(frame2, text="Recall setting", width=Buttonwidth, command=BRecall)
    b.pack(side=BOTTOM, padx=1, pady=2)

    b = Button(frame2, text="Startfrequency", width=Buttonwidth, command=BStartfrequency)
    b.pack(side=BOTTOM, padx=1, pady=2)

    b = Button(frame2, text="Audio device", width=Buttonwidth, command=BAudiodevice)
    b.pack(side=BOTTOM, padx=1, pady=2)

# ================ Initialize the screen picture ===============================

import PIL      # Added by Geoff Cowne 2E0XID Sometimes Image does not work unless you import PIL and then ===> from PIL import xxxx
import Image
import ImageChops
import ImageTk
import ImageDraw
import ImageFont

THEimage = Image.new("RGB",(CANVASwidth+2,CANVASheight+2),color="blue")

if RASPIterminalmode == True:                                   # Terminal mode
    AUTORUN = True                                              # Aways autostart in terminal mode         
else:
    DISPLAYimg = ImageTk.PhotoImage(THEimage)                   # If Desktopmode, then make DISPLAYimg
    Pid = ca.create_image(0, 0, anchor=NW, image=DISPLAYimg)    # If Desktopmode, then display the image

# Select one of the fonts here below for the text
# This font should be in the same directory as the Lopora program
# You can find other .pil fonts on the internet
# =============================================

# TEXTfont = ImageFont.load("helvR08.pil")
TEXTfont = ImageFont.load("helvB08.pil")
# TEXTfont = ImageFont.load("helvR10.pil")
# TEXTfont = ImageFont.load("helvB10.pil")


# ================ Main routine ================================================
txt = strftime("%H:%M:%S GMT", gmtime())
print("=== START RUNNING: " + txt + " ===")
              
Recallconfig("lopora.cfg")          # Try to load the config file
INITIALIZEstart()                   # Initialize variables
SETmessages()                       # Set the SNAPshotmessage and FTPmessage

DoRootUpdate()                      # Activate updated screens

if WAVinput == 0:
    if AUTORUN == True:
        RUNstatus = 1               # RUNstatus has to be 1 to start the program!
    else:
        SELECTaudiodevice()         # Select an audio device
        SHOWtime()                  # Show the reception time for one screen
        Bsnapshot()                 # Ask for enabling Snapshot and FTP upload
        RUNstatus = 1               # RUNstatus set 1 to start the program without pressing the start button
    AUDIOin()                       # Start the main audio reading routine loop
else:                               # Input from WAV file instead of audio device
    WAVin()
