import os
import os.path
from time import time
from psychopy import core
import re

class ExternalCom():
    def __init__(self, lookup=None):
        self.lookup = lookup
    def print_time(self, msg):
        print(f"extcom: {time():.2f} {msg}")

    def event(self, code=None):
        if code is None:
            self.print_time("event code NONE")
            return
        elif self.lookup:
            lcode = self.lookup(code)
            self.print_time(f"event {code} => {lcode}")
        else:
            self.print_time(f"event {code}")

    def new(self, fname):
        self.print_time("new files %s" % fname)

    def start(self):
        self.print_time("start")

    def stop(self):
        self.print_time("stop")
        

class FileLogger(ExternalCom):
    def __init__(self, lookup=None):
        pass

    def write(self, msg):
        self.fh.write(f"{time():.5f} {msg}\n")

    def new(self, fname):
        self.fh = open(fname, 'a+')

    def event(self, code=None):
        self.write(code)

    def start(self):
        self.write("starting task")

    def stop(self):
        self.write("stopping task")
        self.fh.close()


class Arrington(ExternalCom):
    """ Arrington eyetracking software. connected via ethernet.
    must run client software (likely to 192.1.1.2)
    Windows only communcation to provided dev kit provided DLL
   (MRRC hardware provided by avotec)

    should already be calibrated using eyetracking computer stims
    """
    def __init__(self, vpxDll=None, verbose=True, recVideo=False):
        self.verbose = verbose
        self.recVideo = recVideo
        # only used when recVideo
        self.runEyeName = "UNSETNAME"

        # need vpxDLL to communicate with eye tracker
        # e.g. "C:/ARI/VP/VPX_InterApp.dll"
        # (unless maybe we communicate with sockets? see eprime code?)
        # if not set in initialization, try to pull from environment
        # in windows, run with batch. see desktop_run_dollarreward.bat
        if vpxDll is None:
            vpxDll = os.environ.get('VPXDLL')
            if vpxDll is None:
                raise Exception('VPXDLL not set! try setting in environment')
        from ctypes import cdll, CDLL
        if not os.path.exists(vpxDll):
            raise Exception('cannot find eyetracking dll @ ' + vpxDll)
        print(f"trying to open {vpxDll} (confirmed does exist)")
        cdll.LoadLibrary(vpxDll)
        self.vpx = CDLL(vpxDll)
        if self.vpx.VPX_GetStatus(1) < 1:
            raise Exception('ViewPoint is not running!')
        self.vpxsend('say "python is connected"')

    def vpxsend(self, cmd):
        """20210805 - wrap VPX_SendCommand w/str re-encoding
        als suggested by Karl Arrington"""
        self.vpx.VPX_SendCommand(str(cmd).encode('ascii'))

    def event(self, code=None):
        if code is None:
            return
        self.vpxsend('dataFile_InsertString "%s"' % code)
        self.vpxsend('say "sent %s"' % code)

    def new(self, fname):
        self.runEyeName = fname.replace(".txt", "")
        self.vpxsend('dataFile_Pause 1')
        self.vpxsend('dataFile_NewName "%s.txt"' % fname)
        if self.verbose:
            print("tried to open eyetracking file %s" % fname)
            self.vpxsend('say "newfile %s"' % fname)

    def start(self):
        self.vpxsend('dataFile_Pause 0')
        if self.recVideo:
            print("send eyeMoive_NewName cmd")
            self.vpxsend('eyeMovie_NewName "%s.avi"' % self.runEyeName)

    def stop(self) -> os.path:
        self.vpxsend('dataFile_Close 0')
        if self.recVideo:
            print("send end movie cmd")
            self.vpxsend('eyeMovie_Close')
        return self.runEyeName + ".txt"


class Eyelink(ExternalCom):
    """ SR Research Eyelink
    pylink_helper imports pylink
    TODO: calibration is usually done as part of the task
    see eyeTrkCalib
    """
    def __init__(self, winsize, verbose=True):
        self.verbose=verbose

        try:
            # as module
            from lncdtask.pylink_help import eyelink
        except ImportError:
            # as script
            from pylink_help import eyelink
        self.eyelink = eyelink(winsize)

    def event(self, code):
        if code is None:
            return
        self.eyelink.trigger(code)
    
    def new(self, fname):
        # sepcifically grab the first id looking thing
        # NB max file length (w/o .edf) is 8. handled by pylink_helper
        self.eyelink.open(fname)

    def start(self):
        self.eyelink.start()

    def stop(self):
        return self.eyelink.stop()


class ParallelPortEEG(ExternalCom):
    """EEG parallel port ttl"""

    def __init__(self, pp_address, zeroTTL=True, lookup_func=int, verbose=True):
        """
        send codes to LPT 'pp_address'.
        optionally set the TTL to zero after
        b/c TTL is limited 0-255. use lookup_func to lookup codes for event
        NB. this introduces a .01 second lag
        TODO: use async?
        """
        from psychopy import parallel
        self.zeroTTL = zeroTTL
        pp_address = int(pp_address)
        print(f"pp_address: {pp_address}")
        self.pp_address = pp_address
        self.port = parallel.ParallelPort(address=pp_address)
        self.lookup_func = lookup_func
        self.verbose = verbose

        # need core.wait for zeroing
        if zeroTTL:
            from psychopy import core

    def event(self, *kargs):
        """
        send ttl trigger to parallel port
        wait 10ms and send 0
        """
        if kargs is None:
            return
        #print(f"# ttl event: have {kargs}")
        thistrigger = self.lookup_func(*kargs)
        self.port.setData(thistrigger)
        if self.verbose:
            print("eeg code %s" % thistrigger)
        if self.zeroTTL:
            # core imported at __init__ if zeroTTL
            core.wait(.01)  # wait 10ms and send zero
            self.port.setData(0)

    def new(self, fname):
        "no way to start a new file"
        pass

    def start(self):
        "eeg devices starts recording when recives 128"
        self.event(128)

    def stop(self):
        "eeg devices stops recording when recives 129"
        self.event(129)


class MuteWinSound(ExternalCom):
    """
    on windows: mute all sounds while task is going
    implemented because monitor switching and notifications interupt task
    """
    def __init__(self):
        "find all the sound devices"
        try:
            from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
            sessions = AudioUtilities.GetAllSessions()
            self.volumes = [session._ctl.QueryInterface(ISimpleAudioVolume)
                            for session in sessions]
            # is already muted?
            self.origMute = [v.GetMute() for v in self.volumes]
        #except ImportError: # 20180409 -- if it fails for anyreason, continue
        except:
            # set no volumes and no origMutes, nothing will be done by funcs below
            if os.name in ['nt']:
                print(f"WARNING: no volume control; install pycaw")
                print("\tpython -m pip --user install https://github.com/AndreMiras/pycaw/archive/master.zip")
            self.volumes = []
            self.origMute = []

    def start(self):
        "mute all"
        for v in self.volumes:
            v.SetMute(1, None)

    def stop(self) -> str:
        "unmute all. returns empty string: "
        for v in self.volumes:
            v.SetMute(0, None)
        return ""

    def new(self, fname): pass

    def event(self, code): pass
    

class AllExternal(ExternalCom):
    """ugly copy paste. better than using string accessors?"""
    def __init__(self, externals=[]):
        self.externals = externals

    def append(self, extern):
        self.externals.append(extern)

    def prepend(self, extern: ExternalCom):
        """
        Add device to start of externals list.
        Useful to put the more time sensitive device first.
        `start`, `stop`, `event`, etc all issue commands to devices in the order they are in `externals`
        :param extern: external device
        """
        self.externals.insert(0,extern)

    def start(self):
        for ext in self.externals:
            ext.start()

    def stop(self) -> list[str]:
        """stop all externals.return list for eyelink is save file location"""
        return [ext.stop() for ext in self.externals]

    def new(self, fname):
        for ext in self.externals:
            ext.new(fname)

    def event(self, code):
        for ext in self.externals:
            ext.event(code)
