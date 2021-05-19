#!/usr/bin/env python3
from lncdtask.externalcom import Arrington
from psychopy import core

print("connecting ...")
tracker = Arrington()

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

