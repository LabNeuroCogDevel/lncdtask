#!/usr/bin/env python3
from lncdtask.externalcom import Arrington
from lncdtask.arrington_socket import ArringtonSocket
from psychopy import core, event
import os

VPXDLL = r"C:/Windows/System32/VPX_InterApp_64.dll"

try:
 
    print("# USING WRAPPER")
    print("connecting ...")
    tracker = ArringtonSocket("10.48.88.120")


    print("opening new file")
    tracker.new("test_file")

    print("start recording")
    tracker.start()


    print("send event and waiting 1 second...")
    tracker.event("test event")
    core.wait(1)

    print("again and wait 1 second...")
    tracker.event("different event")
    core.wait(1)

    print("done")
    tracker.stop()

    if not os.path.exists(VPXDLL):
        raise Exception(f"VPXDLL doesn't exist! '{VPXDLL}'")
    else:
        print(f"using {VPXDLL}")

    print("# USING DLL")
    from ctypes import cdll, CDLL
    cdll.LoadLibrary(VPXDLL)
    vpx = CDLL(VPXDLL)
    print(f"status: {vpx.VPX_GetStatus(1)}")
    print("sending 'say' command")
    res = vpx.VPX_SendCommand('say "python is connected"')
    print(f"  res: {res}")

    print("using vpx directly")
    tracker.vpx.VPX_SendCommand('say "python is connected"')

except Exception as e:
    print(f"{e}")

#print("anykey to quit")
event.waitKeys()
