#!/usr/bin/env python3
try:
    from lncdtask import LNCDTask, create_window, replace_img, \
            wait_for_scanner, ExternalCom, RunDialog, FileLogger
except ImportError:
    from lncdtask.lncdtask import LNCDTask, create_window, replace_img,\
            wait_for_scanner, ExternalCom, RunDialog, FileLogger

import sys
import numpy as np
import pandas as pd


def random_positions(center=.2, edge=.9, n=20, reps=1):
    # default is 20 steps from center .2 to edge .9 (right side)
    # left side is that but negative: center -.2 to edge -.9
    # for the right side
    p_r = np.linspace(center, edge, n)
    p_lr = np.concatenate([p_r, -1 * p_r])
    ridx = [p for ii in range(reps) for p in np.random.permutation(len(p_lr)) ]
    return p_lr[ridx]


def random_pos_df(dur=.5, **kargs):
    positions = random_positions(**kargs)
    events = []
    onset = 0
    for p in positions:
        events.append({'event_name': 'iti',
                       'position': p, 'onset': onset})
        onset = onset + dur

        events.append({'event_name': 'dot',
                       'position': p, 'onset': onset})
        onset = onset + dur

    # last iti so we see all of final dot
    events.append({'event_name': 'iti',
                   'position': 0, 'onset': onset})

    return pd.DataFrame(events)

def ttl_wrap(desc):
    print(desc)
    return 10

class EyeCal(LNCDTask):
    """
    show a dot to VGS to at a bunch of intervals
    """
    def __init__(self, *karg, **kargs):
        """ create DollarReward task. like LNCDTask,
        need onset_df and maybe win and/or participant
        this also adds a ringimg dictionary and an imageratsize (dotsize)
        >> win = create_window(False)
        >> dr = EyeCal(win=win, externals=[printer])
        >> dr.dot(0, .75)
        """
        super().__init__(*karg, **kargs)

        # extra stims/objects, exending base LNCDTask class
        self.trialnum = 0

        # events
        self.add_event_type('dot', self.dot, ['onset', 'position'])
        self.add_event_type('iti', self.iti, ['onset'])

    def dot(self, onset, position=0):
        """position dot on horz axis to cue anti saccade
        position is from -1 to 1
        """
        self.trialnum = self.trialnum + 1
        self.crcl.pos = (position * self.win.size[0]/2, 0)
        self.crcl.size = (1, 1)
        self.crcl.draw()
        return(self.flip_at(onset, self.trialnum, 'dot', position))


def parse_args(argv):
    import argparse
    parser = argparse.ArgumentParser(description='Run Eye Calibration')
    parser.add_argument('--tracker',
                        choices=["arrington", "testing", "eyelink"],
                        default=None,
                        help='how to track eyes')
    parser.add_argument('--lpt',
                        type=str,
                        default="",
                        help='parallel port (LPT) address to send TTL triggers (/dev/parport0, 53264)')
    parser.add_argument('--n_right',
                        type=int,
                        default=4,
                        help='how many points to use')
    parser.add_argument('--dur',
                        type=float,
                        default=1.0,
                        help='how long to show each point')
    parser.add_argument('--reps',
                        type=int,
                        default=3,
                        help='how long to show each point')
    parsed = parser.parse_args(argv)
    return(parsed)


def run_eyecal(parsed):
    printer = ExternalCom()
    eyetracker = None
    run_info = RunDialog(extra_dict={'fullscreen': True,
                                     'dur': parsed.dur,
                                     'reps': parsed.reps,
                                     'n_right': parsed.n_right},
                         order=['subjid', 'run_num',
                                'timepoint', 'fullscreen', 'dur', 'n_right'])

    if not run_info.dlg_ok():
        sys.exit()

    dur = float(run_info.info['dur'])
    n_right = int(run_info.info['n_right'])
    reps = int(run_info.info['n_right'])

    # create task
    win = create_window(run_info.info['fullscreen'])
    eyecal = EyeCal(win=win, externals=[printer],
                    onset_df=random_pos_df(dur=dur, n=n_right, reps=reps))
    eyecal.gobal_quit_key()  # escape quits
    eyecal.DEBUG = False

    participant = run_info.mk_participant(['EyeCal'])
    run_id = f"{participant.ses_id()}_task-EC_run-{run_info.run_num()}"

    if parsed.tracker == 'arrington':
        try:
            # as module
            from lncdtask.externalcom import Arrington
        except ImportError:
            # as script
            from externalcom import Arrington
        eyetracker = Arrington()
        eyecal.externals.append(eyetracker)
        eyetracker.new(run_id)
    elif parsed.tracker == "eyelink":
        try:
            # as module
            from lncdtask.externalcom import Eyelink
        except ImportError:
            # as script
            from externalcom import Eyelink
        eyetracker = Eyelink(win.size)
        eyecal.externals.append(eyetracker)
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
    eyecal.externals.append(logger)

    eyecal.run(end_wait=1)
    eyecal.onset_df.to_csv(participant.run_path(f"run-{run_info.run_num()}_info"))
    win.close()


def main():
    parsed = parse_args(sys.argv[1:])
    print(parsed)
    run_eyecal(parsed)


if __name__ == "__main__":
    main()
