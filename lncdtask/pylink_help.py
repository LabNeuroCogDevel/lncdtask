"""
eyelink eyetracker functions
largely from "brittAnderson"
  https://stackoverflow.com/questions/35071433/psychopy-and-pylink-example
also see
pygaze
   https://github.com/esdalmaijer/PyGaze/blob/6c07b263c91a0bd8c9c64aedfc2d76c18efa2abf/pygaze/_eyetracker/libeyelink.py
install instructions
 - from internet
   https://osdoc.cogsci.nl/2.9.0/devices/eyelink/#installing-pylink

 - from the vendor
   https://www.sr-support.com/showthread.php?16-Linux-Display-Software-Package

TODO: use pyGaze instead
"""
import pylink as pl
import re
import datetime

def seconds_36base() -> str:
    """
    base 36 encoded unix epoch seconds for saving unique edf log file

    Psychopy 2024.1.4 is using win+python3.8 . no "%s" strftime
    """
    import numpy
    try:
        now = int(datetime.datetime.now().strftime("%s"))
    except ValueError as e:
        import time
        now = int(time.time())
    return numpy.base_repr(int(now),36)

class eyelink:
    """
    quick access to eyelink
    should use pyGaze instead
    20210330 - should use iohub insetad? see psychoeye.py
    """
    def __init__(self, sp, ip='100.1.1.1'):
        """ initialize eyetracker
        :param sp: screen res
        :param ip:  address of tracker. use empty or none for dummy"""
        if not ip:
            el = pl.EyeLink(None)
        else:
            el = pl.EyeLink(ip)
        # pygaze uses
        #  pylink.getEYELINK().setPupilSizeDiameter(True)
        #  pylink.getEYELINK().sendCommand(cmd)
        el.sendCommand("screen_pixel_coords = 0 0 %d %d" % (sp[0], sp[1]))
        el.quietMode(0) # allow messages
        el.sendMessage("DISPLAY_COORDS  0 0 %d %d" % (sp[0], sp[1]))
        el.sendCommand("select_parser_configuration 0")
        el.sendCommand("scene_camera_gazemap = NO")
        # area or diameter
        el.sendCommand("pupil_size_diameter = YES")
        self.el = el
        self.sp = sp

        # sub+session. data file name. set in open. saved to tracker. copied locally
        self.sessionid = None
        # where to save outputfiles (used by self.savename())
        # expect to be set manually outside of class
        self.task_savedir = None

    def open(self, dfn, sessionid=None, base36enc=False):
        """open file"""
        # only alpha numeric and _
        if sessionid is None:
            sessionid = dfn
        dfn = re.sub('[^A-Za-z0-9]','_',dfn)
        # pygaze note: cannot be more than 8 characters?!

        # base36 can encode unix seconds in the filename with a character to spair for the next 50 years
        # len(base_repr(int(datetime.datetime(2099,12,31,23,59,59).strftime("%s")),36)) == 7
        if len(dfn) > 8:
            #raise Warning("%s is too long of a file name. 8 char is max. using base36 of unix seconds!" % dfn)
            base36enc=True
        if base36enc:
            old_dfn = dfn
            dfn = seconds_36base()
            if len(old_dfn)>8:
                print(f"WARNING: {old_dfn}>8 chars long. using base36 encoded time on tracker instead: {dfn}")

        self.el.openDataFile(dfn + '.EDF')
        self.el.sendMessage("NAME: %s"%sessionid)
        print(f"eyelink data metadata header: name '{sessionid}'")

        self.sessionid = sessionid

    def start(self):
        """start tracking"""
        self.el.sendMessage("START")
        error = self.el.startRecording(1, 1, 1, 1)
        if error:
            raise Exception("Failed to start pylink eye tracking!")

    def stop(self):
        """cose file and stop tracking. reurns where data was saved"""
        self.el.sendMessage("END")
        pl.endRealTimeMode()
        # el.sendCommand("set_offline_mode = YES")
        self.el.closeDataFile()
        return self.get_data()
        #pl.getEYELINK().setOfflineMode()

    def savename(self):
        "generate local edf filename"
        seconds = datetime.datetime.strftime(datetime.datetime.now(), "%Y%M%d%H%M%S")
        session_clean = re.sub('[^A-Za-z0-9]','_',self.sessionid)
        prefix = ""
        if self.task_savedir:
            prefix=self.task_savedir + "/"
        saveas = "%s%s_%s.edf" % (prefix, session_clean, seconds)
        return saveas

    def get_data(self, saveas=None):

        if saveas is None:
            saveas = self.savename()
        self.el.closeDataFile() # incase we didn't already
        self.el.receiveDataFile("", saveas)
        print(f"saved eyelink data to {saveas}")
        return saveas

    def trigger(self, eventname):
        """send event discription"""
        # event name must be <=120 characters?
        eventname = re.sub(' ','_', eventname) # this might be slow? millisecond offset?
        self.el.sendMessage(eventname)
        self.el.sendCommand(f"record_status_message {eventname}")

    def trial_start(self,trialid):
        "12 numbers and letters that uniquely identify the trial"
        self.el.sendMessage(f"TRIALID {trialid}")

    def trial_end(self):
        self.el.sendMessage("TRIAL OK")

    def var_data(self, condition, value):
        self.el.sendMessage(f"!V TRIAL_VAR_DATA {condition} {value}");

    def update_screen(self, image_path):
        # todo write
        self.el.sendMessage(f"!V IMGLOAD FILL {image_path}");

    def win_screenshot(self,win):
        from tempfile import mkstemp
        import os
        screenshotname = mkstemp(suffix=".png")[1]
        print(screenshotname)
        win.getMovieFrame(buffer='back')
        win.saveMovieFrames(screenshotname)
        self.update_screen(screenshotname)
        os.unlink(screenshotname)

    def eyeTrkCalib(self, colordepth=32):
        """
        callibration. not used?
        @param colordepth - color depth of display (why?)
        """
        sp = self.sp
        pl.openGraphics(sp, colordepth)
        pl.setCalibrationColors((255, 255, 255), (0, 0, 0))
        pl.setTargetSize(int(sp[0]/70), int(sp[1]/300))
        pl.setCalibrationSounds("", "", "")
        pl.setDriftCorrectSounds("", "off", "off")
        self.el.doTrackerSetup()
        pl.closeGraphics()
