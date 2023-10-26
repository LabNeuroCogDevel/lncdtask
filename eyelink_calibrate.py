#!/usr/bin/env python3

# sudo ip route add default via 10.135.64.10; sudo ip route delete default; sudo ip route add 100.1.1.1 via 100.1.1.2


import os
import sys
from time import sleep
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/lncdtask")
from lncdtask.externalcom import Eyelink


# test out
if len(sys.argv) > 1:
    winsize= sys.argv[1:2]
else:
    winsize=[1280,1024]
print("""
   page up/up arrow     - inc pupil thres
   page down/down arrow - dec pupil thres
   + / -                - inc/dec corneal reflection thresh
   ESC                  - exit
   A                    - Autotrigger (when stable)
   left/right arrow     - select eye (also global or zoomed view)

   === during calibration ===
   ENTER/Spacebar       - start calibration sequence
   M / A                - auto trigger off (manual) / on
   BACKSPACE            - repat prev

   === after calibration ===
   ENTER                - accept calibration
   V                    - validate
   ESC                  - discard calibration
   Backspace            - repeat last

   === after validation ===
   DELETE - restart validation


   === STARTUP ====
   C    -  to start calibration
   Enter - see eye
      """)
input("any key when ready?")
tracker = Eyelink(winsize,verbose=True)
tracker.eyelink.eyeTrkCalib()
