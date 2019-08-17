# LOPEXTftp-v1a.py(w) (18-10-2018)
# For External uploading of the LOPORA pictures
# For Python version 3
# With external module None
# Made by Onno Hoekstra (pa2ohh)


import os
import time
import ftplib

from time import gmtime, strftime

FTPFILES = "FTPuploads.txt"

# ============================================ Main routine ====================================================

def CONTROL():          # Control of the whole process
    global FTPFILES
     # ================ CONTROL ================================================
    while(1):
        if os.path.exists(FTPFILES):
            time.sleep(5)                       # Give the grabber time to finish writing the file names
            FTPupload()
            os.remove(FTPFILES)                 # Remove the file after it is used and wait for the new one
            print(FTPFILES + " removed")
        else:
            print("CHECK: " + FTPFILES + " does not exist")
        time.sleep(30)                          # Next check of the FTPFILES file exist after 30 seconds


def FTPupload():
    global FTPFILES
    FTPfiles = ""
    FTPhost = ""
    FTPuser = ""
    FTPdir = ""
    FTPpassword = "" 
    WORKmap = ""
   
    t = time.time()
    T =time.gmtime(t)
    txt = strftime("%H:%M:%S", T)
    print(txt + "-start FTP upload")

    FTPfiles = []                               # Array that will be filled with the file names
    
    try:
        Rfile = open(FTPFILES,'r')              # open the input file with settings
    except:
        print("ERROR: Cannot open file with file names.")
        return()

    try:
        txt = Rfile.readline()                  # read the next line
        WORKmap = txt[0:-1]
        print("WORK map: " + WORKmap)
    except:
        print("ERROR: Cannot read WORKmap name.")
        return()

    try:
        txt = Rfile.readline()                  # read the next line
        FTPhost = txt[0:-1]
        print("FTP host name: " + FTPhost)
    except:
        print("ERROR: Cannot read FTP host name.")
        return()

    try:
        txt = Rfile.readline()                  # read the next line
        FTPuser = txt[0:-1]
        print("FTP user name: " + FTPuser)
    except:
        print("ERROR: Cannot read FTP user name.")
        return()

    try:
        txt = Rfile.readline()                  # read the next line
        FTPdir = txt[0:-1]
        print("FTP directory: " + FTPdir)
    except:
        print("ERROR: Cannot read FTP directory name.")
        return()

    try:
        txt = Rfile.readline()                  # read the next line
        FTPpassword = txt[0:-1]
        print("FTP password: " + FTPpassword)
    except:
        print("ERROR: Cannot read FTP password.")
        return()

    TheEnd = False
    while (TheEnd == False):
        try:
            txt = Rfile.readline()              # read the next line
            txt = txt[0:-1]

            if txt != "":                       # A filename to be uploaded
                FTPfiles.append(txt)
                print(txt)
            else:
                TheEnd = True 
        except:
            TheEnd = True

    # Start FTP upload routine    
    ftp = None
 
    try:
        # ftp = ftplib.FTP(FTPhost, FTPuser, FTPpassword)           # Open the FTP connection for file uploading with the default time out, works OK for me
        ftp = ftplib.FTP(FTPhost, FTPuser, FTPpassword, "", 10)     # Open the FTP connection for file uploading with a time out, did avoid some problems for others
        print("Connected and logged in to FTP host")
    except:
        print("ERROR: Cannot connected and log in to FTP host")

    if (ftp):
        # Change FTP directory
        try:    
            if FTPdir != "":
                ftp.cwd(FTPdir)
                print("Changed to remote directory: " + FTPdir)
        except:
            print("ERROR: Cannot change to remote directory: " + FTPdir)
            
        # Upload the files
        n = 0
        while n < len(FTPfiles):
            filename = FTPfiles[n]
            storedname = WORKmap + filename

            try:            
                fup = open(storedname, 'rb')                        # Open the file of the picture to be uploaded
                ftp.storbinary("STOR " + filename, fup, 8192)       # Store the file (picture)
                fup.close()
                print(filename + " uploaded")
            except:
                print("ERROR: " + filename + " upload FAILED")
            n = n + 1
    try:
        if ftp:
            ftp.close()
    except:
        pass

    t = time.time()
    T =time.gmtime(t)
    txt = strftime("%H:%M:%S", T)
    txt = txt + "-end FTP upload"
    print(txt)
  

CONTROL()                       # Start the main routine loop
