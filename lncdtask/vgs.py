#!/usr/bin/env python3
"""
Visually Guided Saccade Behavioral Task.


CLI USAGE:
  lncdtask/vgs.py --nofullscreen --subjid wf --nofullscreen --tracker testing
GUI DIALOG:
  lncdtask/vgs.py
"""

VGS_TIMING={
        'vgs_cue': 2, # green '+' variable
        'blank': .1, # empty screen
        'vgs_target':1, # yellow dot (cue.bmp in EP1)
        }

try:
    from lncdtask import LNCDTask, create_window, replace_img, \
            wait_for_scanner, ExternalCom, RunDialog, FileLogger, msg_screen
except ImportError:
    from lncdtask.lncdtask import LNCDTask, create_window, replace_img,\
            wait_for_scanner, ExternalCom, RunDialog, FileLogger, msg_screen

import sys
import numpy as np
import pandas as pd


def random_positions(pos=[-.875,-.5,.5,.875], delay=[2.5,7.5], reps=4):
    """
    randomize position and delay pairs with 'reps' number of repeats
    """
    pos_delay = np.array([(p,d) for p in pos for d in delay])
    ridx = [pd for ii in range(reps) for pd in np.random.permutation(len(pos_delay)) ]
    return pos_delay[ridx]


def random_pos_df():
    pos_delays = random_positions()
    events = []
    onset = 0

    for p,d in pos_delays:
        for event in ['vgs_cue','blank','vgs_target']:
            events.append({'event_name': event, 'position': p, 'delay': d, 'onset': onset, 'code':f'{event}_{d}_{p}'})
            # accumulates onsets
            # 2 seconds for all but vgs_delay which is variable (TODO: what values)
            dur = d if event == 'vgs_cue' else VGS_TIMING[event]
            onset = onset + dur

    return pd.DataFrame(events)

def ttl_wrap(desc):
    print(desc)
    return 10

class VGSEye(LNCDTask):
    """
    Visually Guided Saccade Behavioral Task.
    Events:
     TODO:
    """
    def __init__(self, *karg, **kargs):
        """ create LNCDTask derivative,
        >> win = create_window(False)
        >> vgs = VGSEye(win=win, externals=[printer])
        >> vgs.vgs_target(0, .75)
        """
        super().__init__(*karg, **kargs)

        # extra stims/objects, extending base LNCDTask class
        self.trialnum = 0

        # update circle size
        # no effect?
        self.crcl.size = (1, 1)
        self.crcl.unit = 'pix'
        self.crcl.rad = 10

        # events
        # also see VGS_TIMING: 
        self.add_event_type('vgs_cue', self.vgs_cue, ['onset', 'code'])
        self.add_event_type('vgs_target', self.dot, ['onset', 'position'])
        self.add_event_type('blank',self.mgs_delay, ['onset', 'code'])

    def instructions(self):
        blue = '#000080'  # dark blue used in EPrime


        # 1. welcome - blue (b/c it was blue in EPrime)
        self.win.color = blue; self.win.flip()
        resp = msg_screen(self.msgbox,'Welcome to the Lab\n\nThis is the VGS task.\n\n (c to calibrate)')
        if 'c' in resp and self.eyelink is not None:
            # TODO: two opengl screens? does this fail?
            self.eyelink.eyelink.eyeTrkCalib()


        # TODO: does this send in a way anyone can see? not recording yet
        if self.eyelink:
            self.eyelink.eyelink.trigger('instructions, not recording')

        ## step wise instructions
        self.win.color = 'black'; self.win.flip()

        i=0;
        while True:
            if i == 0:
                self.crcl.pos = (0.9 * self.win.size[0]/2, 0)
                self.crcl.draw()
                resp = msg_screen(self.msgbox,'A dot will appear.\nLook at it!', pos=(0,.9))

            if 'left' in resp and i > 0:
                i -= 1
            else:
                i += 1
            if i > 0:
                break

    def vgs_cue(self,onset,code):
        self.trialnum = self.trialnum + 1
        self.iti_fix.pos = (0,0)  # center
        self.iti_fix.color = 'yellow'
        self.iti_fix.draw()
        return(self.flip_at(onset, self.trialnum, code, mark_func=self.mark_trial))


    def blank(self, onset, code):
        return(self.flip_at(onset, code))

    def dot(self, onset, position=0, code='dot'):
        """position dot on horz axis to cue anti saccade
        position is from -1 to 1
        """
        self.crcl.pos = (position * self.win.size[0]/2, 0)
        self.crcl.draw()
        return(self.flip_at(onset, code))

    def mark_trial(self, trial, *kargs):
        # push to flip_at as mark_func
        #self.win.callOnFlip(mark_func, *kargs)
        if self.eyelink:
            if self.trialnum > 1:
                self.eyelink.eyelink.trial_end()
            self.eyelink.eyelink.trial_start(trial)
        self.mark_external(*kargs)


def parse_args(argv):
    import argparse
    parser = argparse.ArgumentParser(description='Run visually guided saccade (vgs) task')
    parser.add_argument('--tracker',
                        choices=["arrington", "testing", "eyelink"],
                        default=None,
                        help='how to track eyes')
    parser.add_argument('--nofullscreen',
                        action="store_true",
                        default=False,
                        help='how to track eyes')
    parser.add_argument('--lpt',
                        type=str,
                        default="",
                        help='parallel port (LPT) address to send TTL triggers (/dev/parport0, 53264)')
    parser.add_argument('--subjid',
                        type=str,
                        default=None,
                        help='subject id. if set will not open dialog box gui')
    parser.add_argument('--run_num',
                        type=int,
                        default=1,
                        help='within visit run number')
    parsed = parser.parse_args(argv)
    return(parsed)


def run_vgseye(parsed):
    printer = ExternalCom()

    # menu or already picked?
    eyetrackers = ["eyelink","arrington","testing"]
    if parsed.tracker:
        eyetrackers = parsed.tracker 

    extra_dict={'fullscreen': not parsed.nofullscreen,
                'tracker': eyetrackers}
    run_info = RunDialog(extra_dict=extra_dict,
                         order=['subjid', 'run_num',
                                'timepoint', 'fullscreen'])

    # dont want a gui window if we've specified subjid
    if parsed.subjid:
        run_info.info['subjid'] = parsed.subjid
        run_info.info['run_num'] = parsed.run_num
        dlg_success = True
    else:
        dlg_success = run_info.dlg_ok()

    # maybe user closed with 'cancel'? dont run then
    if not dlg_success:
        sys.exit()

    # create task
    win = create_window(run_info.info['fullscreen'])
    vgs = VGSEye(win=win, externals=[printer],
                    onset_df=random_pos_df())
    vgs.gobal_quit_key()  # escape quits
    vgs.DEBUG = False
    vgs.eyelink = None

    participant = run_info.mk_participant(['VGSEye'])
    run_id = f"{participant.ses_id()}_task-VGS_run-{run_info.run_num()}"


    if run_info.info["tracker"] == 'arrington':
        try:
            # as module
            from lncdtask.externalcom import Arrington
        except ImportError:
            # as script
            from externalcom import Arrington
        eyetracker = Arrington()
        vgs.externals.append(eyetracker)
        eyetracker.new(run_id)
    elif run_info.info["tracker"] == "eyelink":
        try:
            # as module
            from lncdtask.externalcom import Eyelink
        except ImportError:
            # as script
            from externalcom import Eyelink
        vgs.eyelink = Eyelink(win.size)
        vgs.externals.append(vgs.eyelink)
        vgs.eyelink.new(run_id)

    if parsed.lpt:
        try:
            # as module
            from lncdtask.externalcom import ParallelPortEEG
        except ImportError:
            # as script
            from externalcom import ParallelPortEEG
        port = parsed.lpt # on windows, for to int. on linux /dev/parport0
        eyetracker = ParallelPortEEG(port, lookup_func=ttl_wrap, verbose=True)

    logger = FileLogger()
    logger.new(participant.log_path(run_id))
    vgs.externals.append(logger)

    # want to fail early if ET setup isn't working
    # so instructions are after that
    # 'run()' calls 'start()' for each external. so should't be recording yet
    vgs.instructions()

    print(vgs.onset_df)
    vgs.run(end_wait=1)
    vgs.onset_df.to_csv(participant.run_path(f"run-{run_info.run_num()}_info"))
    win.close()


def main():
    parsed = parse_args(sys.argv[1:])
    print(parsed)
    run_vgseye(parsed)


if __name__ == "__main__":
    main()
