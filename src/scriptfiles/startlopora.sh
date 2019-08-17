#!/bin/sh

# wait 120 sec till the Internet modem has rebooted after a power failure
# And the "system-timesync" has set the Raspberry Pi time clock
sleep 120

# Start lopora
cd /home/pi/lopora/Python3/
lxterminal -l -e 'python3 LOPORA-v5a.py ; /bin/sh ' &
lxterminal -l -e 'python3 LOPEXTftp-v1a.py ; /bin/sh ' &

# Start lopora2
# cd /home/pi/lopora2/Python3/
# lxterminal -l -e 'python3 LOPORA-v5a.py ; /bin/sh ' &
# lxterminal -l -e 'python3 LOPEXTftp-v1a.py ; /bin/sh ' &

