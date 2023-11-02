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

CLI USAGE:
  lncdtask/mgs.py --nofullscreen --subjid wf --nofullscreen --tracker testing
GUI DIALOG:
  lncdtask/mgs.py
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
        self.crcl.size = (1, 1)
        self.crcl.unit = 'pix'
        self.crcl.rad = 10

        # events
        # also see MGS_TIMING: 'mgs_cue','mgs_target','mgs_delay','mgs_exec','iti'
        self.add_event_type('mgs_cue', self.mgs_cue, ['onset', 'code'])
        self.add_event_type('mgs_target', self.dot, ['onset', 'position'])
        self.add_event_type('mgs_delay',self.mgs_delay, ['onset', 'code'])
        # black is empty screen
        self.add_event_type('mgs_exec', self.mgs_exec, ['onset', 'code'])
        self.add_event_type('iti', self.mgs_helper, ['onset','position','code'])

    def instructions(self):
        blue = '#000080'  # dark blue used in EPrime


        # 1. welcome - blue (b/c it was blue in EPrime)
        self.win.color = blue; self.win.flip()
        resp = msg_screen(self.msgbox,'Welcome to the Lab\n\nThis is the MGS task.\n\n (c to calibrate)')
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

            elif i == 1:
                self.iti_fix.color = 'blue'
                self.iti_fix.draw()
                resp = msg_screen(self.msgbox,'The yellow dot will disappear.\nLook back to the blue center cross.', pos=(0,.6))
            
            elif i == 2:
                resp = msg_screen(self.msgbox,'When the cross also disappears\nMove your eyes to where the flash was\n\n\n<---   --->', pos=(0,.7))

            elif i == 3: 
                msg_screen(self.msgbox,'At the end, your helper', pos=(0,.8), flip=False)
                self.iti_fix.pos = (.9, 0); self.iti_fix.color = 'white'; self.iti_fix.draw()
                resp = msg_screen(self.msgbox,'shows you the right place to look', pos=(0,-.8))

            elif i == 4: 
                # final summary
                self.win.color = blue; self.win.flip()
                self.img.image = 'images/mgs/mgs_summary.png'
                self.img.draw()
                resp = msg_screen(self.msgbox,'')

            elif i == 5: 
                # last screen before we start
                self.win.color = 'black'; self.win.flip()
                resp = msg_screen(self.msgbox,'Ready?\n\n(any key; esc to quit)')

            if 'left' in resp and i > 0:
                i -= 1
            else:
                i += 1
            if i > 5:
                break

    def mgs_cue(self,onset,code):
        self.trialnum = self.trialnum + 1
        self.iti_fix.pos = (0,0)  # center
        self.iti_fix.color = 'yellow'
        self.iti_fix.draw()
        return(self.flip_at(onset, self.trialnum, code, mark_func=self.mark_trial))

    def mgs_delay(self,onset,code):
        return self.show_cross(color='blue', onset=onset, code=code)

    def mgs_exec(self, onset, code):
        return self.show_cross(color='black', onset=onset, code=code)

    def mgs_helper(self, onset, position, code):
        return self.show_cross(color='white', onset=onset, code=code, x_pos=position)

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


    def show_cross(self, onset, color='white', code='cross', x_pos=0):
        "most events are just showing a colored cross somewhere on the screen"
        self.iti_fix.pos = (x_pos,0)
        self.iti_fix.color = color
        self.iti_fix.draw()
        return(self.flip_at(onset, code))


def parse_args(argv):
    import argparse
    parser = argparse.ArgumentParser(description='Run memory guided saccade (mgs) task')
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


def run_mgseye(parsed):
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
    mgs = MGSEye(win=win, externals=[printer],
                    onset_df=random_pos_df())
    mgs.gobal_quit_key()  # escape quits
    mgs.DEBUG = False
    mgs.eyelink = None

    participant = run_info.mk_participant(['MGSEye'])
    run_id = f"{participant.ses_id()}_task-MGS_run-{run_info.run_num()}"


    if run_info.info["tracker"] == 'arrington':
        try:
            # as module
            from lncdtask.externalcom import Arrington
        except ImportError:
            # as script
            from externalcom import Arrington
        eyetracker = Arrington()
        mgs.externals.append(eyetracker)
        eyetracker.new(run_id)
    elif run_info.info["tracker"] == "eyelink":
        try:
            # as module
            from lncdtask.externalcom import Eyelink
        except ImportError:
            # as script
            from externalcom import Eyelink
        mgs.eyelink = Eyelink(win.size)
        mgs.externals.append(mgs.eyelink)
        mgs.eyelink.new(run_id)

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

    # want to fail early if ET setup isn't working
    # so instructions are after that
    # 'run()' calls 'start()' for each external. so should't be recording yet
    mgs.instructions()

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
