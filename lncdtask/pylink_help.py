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


class eyelink:
    """
    quick access to eyelink
    should use pyGaze instead
    20210330 - should use iohub insetad? see psychoeye.py
    """
    def __init__(self, sp):
        """ initialize eyetracker
        @param 'sp' screen res"""
        el = pl.EyeLink()
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

    def open(self, dfn, sessionid=None, base36enc=False):
        """open file"""
        # only alpha numeric and _
        dfn = re.sub('[^A-Za-z0-9]','_',dfn)
        # pygaze note: cannot be more than 8 characters?!

        # base36 can encode unix seconds in the filename with a character to spair for the next 50 years
        # len(base_repr(int(datetime.datetime(2099,12,31,23,59,59).strftime("%s")),36)) == 7
        if len(dfn) > 8:
            raise Warning("%s is too long of a file name. 8 char is max. using base36 of unix seconds!" % dfn)
            base36enc=True
        if base36enc:
            import numpy
            dfn = numpy.base_repr(int(datetime.datetime().now().strftime("%s")),36)

        self.el.openDataFile(dfn + '.EDF')
        if sessionid is None:
            sessionid=dfn
        self.el.sendMessage("NAME: %s"%sessionid)

        self.sessionid = sessionid

    def start(self):
        """start tracking"""
        self.el.sendMessage("START")
        error = self.el.startRecording(1, 1, 1, 1)
        if error:
            raise Exception("Failed to start pylink eye tracking!")

    def stop(self):
        """cose file and stop tracking"""
        self.el.sendMessage("END")
        pl.endRealTimeMode()
        pl.getEYELINK().setOfflineMode()
        # el.sendCommand("set_offline_mode = YES")
        self.el.closeDataFile()

    def get_data(seflf, saveas=None):

        if saveas is None:
            seconds = datetime.datetime.strftime(datetime.datetime.now(), "%Y%M%d%H%M%S")
            # TODO: make sure session id is a save filename?
            savas_edf = "%s_%s.edf" % (self.sessionid, seconds)
        self.el.closeDataFile() # incase we didn't already
        self.el.receiveDataFile("",saveas_edf)

    def trigger(self, eventname):
        """send event discription"""
        self.el.sendMessage(eventname)

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
