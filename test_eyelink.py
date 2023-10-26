#!/usr/bin/env python3

# sudo ip route add default via 10.135.64.10; sudo ip route delete default; sudo ip route add 100.1.1.1 via 100.1.1.2


import os
import sys
from time import sleep
import re

# if any arguements, run calibration
allargs = "_".join(sys.argv[1:])
print(allargs)
if re.search("help", allargs):
    print("*USEAGE: ./test_eyelink.py cal sendimg")
    sys.exit(0)


sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/lncdtask")
from lncdtask.externalcom import Eyelink


# test out
print("creating tracker object with dll")
winsize=[1280,1024]
tracker = Eyelink(winsize,verbose=True)

if re.search("cal", allargs):
    print("running calibration")
    tracker.eyelink.eyeTrkCalib()




print("opening new file")
tracker.new("my_test_file")

print("start recording")
tracker.start()
sleep(1)

print("start trial")
tracker.eyelink.trial_start("1")
sleep(1)

print("send event and waiting 1 second...")
tracker.event("test event")
sleep(1)

if re.search("sendimg", allargs):
    print("sending image .. white cross")
    import lncdtask.lncdtask
    win = lncdtask.lncdtask.create_window(False)
    iti_fix = lncdtask.lncdtask.visual.TextStim(win, text='+', color='white')
    print(iti_fix)
    iti_fix.draw()
    tracker.eyelink.win_screenshot(win)
    win.flip()
    print("and now yellow")
    sleep(1)
    iti_fix = lncdtask.lncdtask.visual.TextStim(win, text='+', color='yellow')
    iti_fix.draw()
    tracker.eyelink.win_screenshot(win)
    win.close()

print("send event directly with eyelink...")
tracker.eyelink.trigger("example trigger")
sleep(1)

print("set data...")
tracker.eyelink.var_data("abc")
sleep(1)

print("end trial...")
tracker.eyelink.trial_end()


#tracker.eyelinkupdate_screen()


print("done. and saving file here")
tracker.stop()

