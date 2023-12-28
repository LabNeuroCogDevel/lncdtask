#!/usr/bin/env python3
"""
Visually Guided Saccade Behavioral Task.


CLI USAGE:
  lncdtask/vgs.py --nofullscreen --subjid wf --nofullscreen --tracker testing
GUI DIALOG:
  lncdtask/vgs.py
"""

VGS_TIMING={
        'vgscue': 2, # green '+' variable
        'gap': .2, # empty screen
        'vgstarget':1, # yellow dot (cue.bmp in EP1)
        'blank': .03, # empty screen
        }

VGS_CUE_DURS_SEC = [.5, 2, 6, 4]
VGS_DOT_POS = [-.875, -.43, .43,.875] #  (c(40,180,460,600) - 640/2) /(640/2)

try:
    from lncdtask import LNCDTask, create_window, replace_img, \
            wait_for_scanner, ExternalCom, RunDialog, FileLogger, msg_screen
except ImportError:
    from lncdtask.lncdtask import LNCDTask, create_window, replace_img,\
            wait_for_scanner, ExternalCom, RunDialog, FileLogger, msg_screen

import sys
import numpy as np
import pandas as pd

def random_positions(pos=VGS_DOT_POS, delay=VGS_CUE_DURS_SEC, reps=3):
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
        for event in ['vgscue','gap','vgstarget','blank']:
            events.append({'event_name': event, 'position': p, 'delay': d, 'onset': onset, 'code':f'{event}_{d}_{p}'})
            # accumulates onsets
            # 2 seconds for all but vgs_delay which is variable (TODO: what values)
            dur = d if event == 'vgscue' else VGS_TIMING[event]
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
        self.add_event_type('vgscue', self.vgs_cue, ['onset', 'code'])
        self.add_event_type('gap',self.blank, ['onset', 'code'])
        self.add_event_type('vgstarget', self.dot, ['onset', 'position','code'])
        self.add_event_type('blank',self.blank, ['onset', 'code'])


    ## instructions copied from EP1 version
    def instruction_cross1(self):
        self.vgs_cue(0,'none',flip=False)
        return msg_screen(self.msgbox,'Look at the green cross', pos=(0,.9))

    def instruction_dot(self):
        self.crcl.pos = (0.9 * self.win.size[0]/2, 0)
        self.crcl.draw()
        return msg_screen(self.msgbox,'A dot will appear.\nLook at it!', pos=(0,.9))

    def instruction_cross2(self):
        self.vgs_cue(0,'none',flip=False)
        return msg_screen(self.msgbox,'Look back to the green cross', pos=(0,.9))

    def welcome(self):
        return self.instruction_welcome(msg='Welcome to the Lab\n\nThis is the VGS task.\n\n (c to calibrate)')

    ## only 3 events
    def vgs_cue(self, onset, code, flip=True):
        """green fix cross indicating start of trial"""
        self.iti_fix.pos = (0,0)  # center
        self.iti_fix.color = 'green'
        self.iti_fix.draw()
        if flip:
            self.trialnum = self.trialnum + 1
            print(f"trial {self.trialnum} @ {onset}")
            return self.flip_at(onset, self.trialnum, code,
                                mark_func=self.eyelink_trial_mark_plus_external)

    def blank(self, onset, code):
        """flash black before flashing dot"""
        return(self.flip_at(onset, code))

    def dot(self, onset, position=0, code='dot'):
        """position dot on horz axis to cue anti saccade
        position is from -1 to 1
        NB. prev did not pass 'code' column to self.dot when vgstarget
            now code set like rest of task events ('vsgtarget_{dur}_{pos}')
        """
        self.crcl.pos = (position * self.win.size[0]/2, 0)
        self.crcl.draw()
        return self.flip_at(onset, code)


def parse_args(argv):
    """ command line arguments for VGS (same as MGS) """
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
    vgs.run_instructions([vgs.welcome,
                          vgs.instruction_cross1,
                          vgs.instruction_dot,
                          vgs.instruction_cross2,
                          vgs.instruction_ready])

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
