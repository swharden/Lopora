#!/bin/sh

# Start lopora
cd /home/pi/lopora/Python3/
lxterminal -l -e 'python3 LOPORA-v5a.py ; /bin/sh ' &
lxterminal -l -e 'python3 LOPEXTftp-v1a.py ; /bin/sh ' &

# Start lopora2
# cd /home/pi/lopora2/Python3/
# lxterminal -l -e 'python3 LOPORA-v5a.py ; /bin/sh ' &
# lxterminal -l -e 'python3 LOPEXTftp-v1a.py ; /bin/sh ' &
