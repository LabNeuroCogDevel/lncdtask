from externalcom import ExternalCom
import socket
import os


class ArringtonSocket(ExternalCom):
    """ Arrington eyetracking software. connected via ethernet. 
    can get away without running client software if we use socket?
    """
    def __init__(self, host=None, port=5000, verbose=True, recVideo=False):
        self.verbose = verbose
        self.recVideo = recVideo
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if host is None:
            print("getting ArringtonSocket host from env ET_HOST")
            host = os.environ.get("ET_HOST")
            if host is None:
                raise Exception("no ET host specified! use ET_HOST env var")
        print(f"connecting to {host}")
        self.server.connect((host, port))

        # TODO: get status, confirm working

    def send_cmd(self, cmd):
        cmd = cmd + ";"
        cmdl = len(cmd)
        buf = f"VPX2 {cmdl};220;{cmd}"
        self.server.send(buf)

    def event(self, code=None):
        if code is None:
            return
        self.send_cmd('dataFile_InsertString "%s"' % code)
        self.send_cmd('say "sent %s"' % code)

    def new(self, fname):
        self.runEyeName = fname.replace(".txt", "")
        self.send_cmd('dataFile_Pause 1')
        self.send_cmd('dataFile_NewName "%s"' % fname)
        if self.verbose:
            print("tried to open eyetracking file %s" % fname)
            self.send_cmd('say "newfile %s"' % fname)

    def start(self):
        self.send_cmd('dataFile_Pause 0')
        if self.recVideo:
            print("send eyeMoive_NewName cmd")
            self.send_cmd('eyeMovie_NewName "%s.avi"' % self.runEyeName)

    def stop(self):
        self.send_cmd('dataFile_Close 0')
        if self.recVideo:
            print("send end movie cmd")
            self.send_cmd('eyeMovie_Close')
