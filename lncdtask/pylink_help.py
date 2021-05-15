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

    def open(self, dfn):
        """open file"""
        # pygaze note: cannot be more than 8 characters?!
        if len(dfn) > 6:
            raise Exception("%s is too long of a file name!" % dfn)
        self.el.openDataFile(dfn + '.EDF')

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
