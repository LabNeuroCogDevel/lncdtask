#!/usr/bin/env python3
"""
Memory Guided Saccade Behavioral Task.

Participant ask to trials that consists of looking
0. center fix (mgs cue)
1. to a dot (mgs target)
2. at center fix cross (delay)
3. back to prev dot loc on empty screen (mgs execute)

Port of EPrime1 task. MGS_lookatblue.es
2 delays (short=2.5s, long=7.5s) and 4 dot positions (40,160,460,600)/640 %
each combo repeated 4 times. 4 reps *2 delays*4 pos = 32 trials

"""

MGS_TIMING={
        'mgs_cue': 2, # yellow '+'
        'mgs_target':2, # yellow dot (cue.bmp in EP1)
        'mgs_delay': 0, # blue '+' variable duration
        'mgs_exec': 2,  # empty screen
        'iti': 2 # "Feedback" in EP1, white '+' on black
        }

try:
    from lncdtask import LNCDTask, create_window, replace_img, \
            wait_for_scanner, ExternalCom, RunDialog, FileLogger
except ImportError:
    from lncdtask.lncdtask import LNCDTask, create_window, replace_img,\
            wait_for_scanner, ExternalCom, RunDialog, FileLogger

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
        for event in ['mgs_cue','mgs_target','mgs_delay','mgs_exec','iti']:
            events.append({'event_name': event, 'position': p, 'delay': d, 'onset': onset, 'code':f'{event}_{d}_{p}'})
            # accumulates onsets
            # 2 seconds for all but mgs_delay which is variable (likely 2.5 or 7.5)
            dur = d if event == 'mgs_delay' else MGS_TIMING[event]
            onset = onset + dur

    return pd.DataFrame(events)

def ttl_wrap(desc):
    print(desc)
    return 10

class MGSEye(LNCDTask):
    """
    Memory Guided Saccade Behavioral Task.
    Events:
     center fix (mgs cue); dot (mgs target); center fix (delay); empty screen 
    """
    def __init__(self, *karg, **kargs):
        """ create LNCDTask derivative,
        >> win = create_window(False)
        >> dr = MGSEye(win=win, externals=[printer])
        >> dr.mgs_target(0, .75)
        """
        super().__init__(*karg, **kargs)

        # extra stims/objects, extending base LNCDTask class
        self.trialnum = 0

        # update circle size
        # no effect?
        #self.crcl.size = (1, 1)
        #self.crcl.unit = 'pix'
        #self.crcl.rad = 15

        # events
        # also see MGS_TIMING: 'mgs_cue','mgs_target','mgs_delay','mgs_exec','iti'
        self.add_event_type('mgs_cue', self.mgs_cue, ['onset', 'code'])
        self.add_event_type('mgs_target', self.dot, ['onset', 'position'])
        self.add_event_type('mgs_delay',self.mgs_delay, ['onset', 'code'])
        # black is empty screen
        self.add_event_type('mgs_exec', self.mgs_exec, ['onset', 'code'])
        self.add_event_type('iti', self.mgs_helper, ['onset','position','code'])

    def mgs_cue(self,onset,code):
        return self.cross(color='yellow',onset=onset,code=code)

    def mgs_delay(self,onset,code):
        return self.cross(color='blue', onset=onset, code=code)

    def mgs_exec(self, onset, code):
        return self.cross(color='black', onset=onset, code=code)

    def mgs_helper(self, onset, position, code):
        return self.cross(color='white', onset=onset, code=code, x_pos=position)

    def dot(self, onset, position=0, code='dot'):
        """position dot on horz axis to cue anti saccade
        position is from -1 to 1
        """
        self.crcl.pos = (position * self.win.size[0]/2, 0)
        self.crcl.draw()
        return(self.flip_at(onset, code))

    def cross(self, onset, color='white', code='cross', x_pos=0):
        if color == 'yellow': # yellow = mgs_cue
            self.trialnum = self.trialnum + 1
            # TODO: mark trial if SR
       
        self.iti_fix.pos = (x_pos,0)
        self.iti_fix.color = color
        self.iti_fix.draw()
        return(self.flip_at(onset, code))


def parse_args(argv):
    import argparse
    parser = argparse.ArgumentParser(description='Run Eye Calibration')
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
    parsed = parser.parse_args(argv)
    return(parsed)


def run_mgseye(parsed):
    printer = ExternalCom()
    eyetracker = None
    run_info = RunDialog(extra_dict={'fullscreen': not parsed.nofullscreen,
                                     'tracker': ["eyelink","arrington","testing"]},
                         order=['subjid', 'run_num',
                                'timepoint', 'fullscreen'])

    if not run_info.dlg_ok():
        sys.exit()

    # create task
    win = create_window(run_info.info['fullscreen'])
    mgs = MGSEye(win=win, externals=[printer],
                    onset_df=random_pos_df())
    mgs.gobal_quit_key()  # escape quits
    mgs.DEBUG = False

    participant = run_info.mk_participant(['MGSEye'])
    run_id = f"{participant.ses_id()}_task-MGS_run-{run_info.run_num()}"

    if parsed.tracker == 'arrington':
        try:
            # as module
            from lncdtask.externalcom import Arrington
        except ImportError:
            # as script
            from externalcom import Arrington
        eyetracker = Arrington()
        mgs.externals.append(eyetracker)
        eyetracker.new(run_id)
    elif parsed.tracker == "eyelink":
        try:
            # as module
            from lncdtask.externalcom import Eyelink
        except ImportError:
            # as script
            from externalcom import Eyelink
        eyetracker = Eyelink(win.size)
        mgs.externals.append(eyetracker)
        eyetracker.new(run_id)

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
    mgs.externals.append(logger)

    print(mgs.onset_df)
    mgs.run(end_wait=1)
    mgs.onset_df.to_csv(participant.run_path(f"run-{run_info.run_num()}_info"))
    win.close()


def main():
    parsed = parse_args(sys.argv[1:])
    print(parsed)
    run_mgseye(parsed)


if __name__ == "__main__":
    main()
