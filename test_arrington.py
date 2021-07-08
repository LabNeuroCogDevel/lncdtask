#!/usr/bin/env python3

# use either host socket or dll with viewpointclient
HOST = "10.48.88.120"
VPXDLL = r"C:/Windows/System32/VPX_InterApp_64.dll"


import os
import sys
from time import sleep
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/lncdtask")
from lncdtask.externalcom import Arrington
from lncdtask.arrington_socket import ArringtonSocket

# can take a dll or ip address
if len(sys.argv) > 1:
    if re.search('dll', sys.argv[1], re.IGNORECASE):
        VPXDLL = sys.argv[1]
        HOST = ""
        print("setting dll to {VPXDLL}")
    else:
        HOST = sys.argv[1]
        VPXDLL = ""
        print("setting host to {HOST}")

# test out
try:
    if 'HOST' in vars() and HOST:
        print("connecting ...")
        tracker = ArringtonSocket(HOST)

    elif 'VPXDLL' in vars() and VPXDLL:
        if not os.path.exists(VPXDLL):
            raise Exception(f"VPXDLL doesn't exist! '{VPXDLL}'")
        else:
            print(f"using {VPXDLL}")

        print("# DLL directly")
        from ctypes import cdll, CDLL
        cdll.LoadLibrary(VPXDLL)
        vpx = CDLL(VPXDLL)
        print(f"status: {vpx.VPX_GetStatus(1)}")
        print("'say' command to ET")
        res = vpx.VPX_SendCommand('say "python is connected"')
        print(f"  res: {res}")

        print("creating tracker object with dll")
        tracker = Arrington(VPXDLL, verbose=True)

        print("using vpx directly via tracker package")
        tracker.vpx.VPX_SendCommand('say "python is connected via wrapper"')
    else:
        raise Exception(f"define HOST or VPXDLL in {__file__}")


    print("# USING lncdtask ET WRAPPER")

    print("opening new file")
    tracker.new("test_file")

    print("start recording")
    tracker.start()


    print("send event and waiting 1 second...")
    tracker.event("test event")
    sleep(1)

    print("again and wait 1 second...")
    tracker.event("different event")
    sleep(1)

    print("done")
    tracker.stop()

except Exception as e:
    print(f"ERROR: {e}")

input("Press enter to quit\n")
