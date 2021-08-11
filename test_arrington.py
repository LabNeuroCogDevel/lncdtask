#!/usr/bin/env python3
from lncdtask.externalcom import Arrington
from psychopy import core, event
import os

#VPXDLL = "C:/Users/Clark/Desktop/VPx64-Client/VPX_InterApp_64.dll"
VPXDLL = 'C:\\Users\\Luna\\Desktop\\VPx32\\Interfaces\\VPx32-Client\\VPX_InterApp_32.dll'
try:
    if not os.path.exists(VPXDLL):
        raise Exception(f"VPXDLL doesn't exist! '{VPXDLL}'")
    else:
        print(f"using {VPXDLL}")

    print("connecting ...")
    tracker = Arrington(vpxDll=VPXDLL)

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

except Exception as e:
    print(f"{e}")

#print("anykey to quit")
event.waitKeys()
