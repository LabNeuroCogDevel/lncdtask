try:
    from lncdtask import LNCDTask, create_window, replace_img, wait_for_scanner
except ImportError:
    from lncdtask.lncdtask import LNCDTask, create_window, replace_img, wait_for_scanner
from psychopy import misc, visual
import numpy as np
import pandas as pd
from math import floor, ceil
import os
import psychopy

# this is defined by enviromental variable
# see ../desktop_run_dollarreward.bat
# VPXDLL=r"C:/Windows/System32/VPX_InterApp_64.dll"

def eppos2relpos(x, orig_width=800):
    """convert from old eprime value 0-600 to -1 to 1
    >>> eppos2relpos(0)
    -1
    >>> eppos2relpos(400)
    0
    >>> eppos2relpos(800)
    1
    """
    half_width=orig_width/2
    return (x-half_width)/half_width


def ttl_wrap(code):
    """
    might int input: start and stop codes from library
    otherwise is a string of trial event rew pos
    sent to ttl()
    """
    if type(code) == str:
        einfo = code.split(' ')
        code = ttl(*einfo)
        print(f"code: {code} from {einfo}")
    return code

def ttl(trial, event=None, rew=None, pos=None):
    """
    input is same as what is given to flip_at
    passed from there into
    callOnFlip(mark_func, *kargs)
    """
    rew_look = {'neu': 100, 'rew': 200}
    evt_look = { 'iti': 10, 'ring': 20, 'prep': 20,
                'cue': 30,  'dot': 40}
    # though we were using input pos
    # but actually getting calc screen -1 to 1
    #pos_look = {  '7': 1, '214': 2,
    #            '426': 3, '633': 4}
    #pos_look= pos_look.get(str(pos), 5)
    if pos is None:
        pos = 9
    else:
        pos = float(pos)

    if pos < -.7: #-.97
        pos_look = 1
    elif pos < -.5: # -.66
        pos_look = 2
    elif pos < 0: # -.33
        pos_look = 3
    elif pos < .5: # .33
        pos_look = 4
    elif pos < .9: # .66
        pos_look = 5
    elif pos < 1: # .97
        pos_look = 6
    else:
        pos_look = 0 # iti -- no side


    v = rew_look.get(rew, 0) +\
        evt_look.get(event, 50) + \
        pos_look

    return(v)
            

class DollarReward(LNCDTask):
    """
              Description
      1       Neutral antisaccade (neutralCue 1.5s,PrepCue 1.5s,SaccadeCue 1.5s)  
      2       Reward antisaccade  (rewardCue  1.5s,PrepCue 1.5s,SaccadeCue 1.5s)
      3       Neutral catch1 (neutralCue 1.5s, PrepCue 1.5s)
      4       Reward catch1  (RewardCue 1.5s, PrepCue 1.5s)
      5       Neutral catch2 (neutralCue 1.5s)
      6       Reward catch2  (RewardCue 1.5s)
    Fixation cross during PrepCue and SaccadeCue is red, otherwise fixation cross is white.

    From original across 4 runs:
     counts TrialType
     57     1
     55     2
     12     3
     12     4
     12     5
     12     6
    """
    def __init__(self, *karg, **kargs):
        """ create DollarReward task. like LNCDTask, need onset_df and maybe win and/or participant
        this also adds a ringimg dictionary and an imageratsize (dotsize)
        >> win = create_window(False)
        >> onset_df= pd.DataFrame({'onset':[0], 'event_name':['ring']})
        >> printer = lncdtask.ExternalCom()
        >> dr = DollarReward(win=win, onset_df=onset_df, externals=[printer])
        >> dr.ring(0, 'rew')
        """
        super().__init__(*karg, **kargs)

        # extra stims/objects, exending base LNCDTask class
        self.ringimg = {}
        self.dotsize_edge = .15 # part of hack to get circle size
        self.make_ring()
        self.trialnum = 0
        
        self.ringpng = {
            'rew': visual.ImageStim(self.win, name="ringnue", interpolate=True, image='images/dollarRing.png'),
            'neu': visual.ImageStim(self.win, name="ringrew", interpolate=True, image='images/neutralRing.png')
        }

        self.instructionpng = visual.ImageStim(self.win, name="instruct", interpolate=True, image='images/instructions.png')

        # events
        self.add_event_type('ring', self.ring, ['onset','ring_type','position'])
        self.add_event_type('prep', self.prep, ['onset','ring_type','position'])
        self.add_event_type('dot', self.dot, ['onset','ring_type','position'])
        self.add_event_type('iti', self.iti, ['onset'])

    # -- drawing functions
    def ring(self, onset, ring_type, position=None):
        """ display ring: reward or neutral """
        self.trialnum = self.trialnum + 1
        #self.ringimg[ring_type].draw()
        self.ringpng[ring_type].draw()
        self.cue_fix.color = 'white'
        self.cue_fix.draw()
        return(self.flip_at(onset, self.trialnum, 'ring', 'rew', position))

    def prep(self, onset, ring_type=None, position=None):
        """cue before onset"""
        self.cue_fix.color = 'red'
        self.cue_fix.draw()
        return(self.flip_at(onset, self.trialnum, 'cue', ring_type, position))

    def dot(self, onset, ring_type=None, position=0):
        """position dot on horz axis to cue anti saccade
        position is from -1 to 1
        """
        # hack to get dot size
        imgpos = replace_img(self.img, None, position, self.dotsize_edge)
        self.crcl.pos = imgpos
        self.crcl.size=(1,1) # TODO: needed in newer versions of psychopy? why?
        self.crcl.draw()
        #print(f"CIRCLE INFO:\n{self.crcl}")
        return(self.flip_at(onset, self.trialnum, 'dot', ring_type, position))

    def get_ready(self, triggers=['equal']):
        "flip the two instruction png, wait for the scanner trigger"
        self.instructionpng.image = 'images/instruction_1.png'
        self.instructionpng.draw()
        self.win.flip()
        psychopy.event.waitKeys()
        print("Waiting for scanner")
        self.instructionpng.image = 'images/instructions.png'
        self.instructionpng.draw()
        self.win.flip()
        psychopy.event.waitKeys(keyList=triggers)

    # -- helpers
    def make_ring(self, text_size=45):
        """ create the ring
        20210518 - use images instead to match eprime experiment
        makes self.ringimg['rew'] and self.ringimg['neu']
        see
        https://discourse.psychopy.org/t/the-best-way-to-draw-many-text-objects-rsvp/2758
        """

        # color and symbol for ring reward
        cues = {'neu': {'color': 'gray', 'sym': '#'},
                'rew': {'color': 'green', 'sym': '$'}}
        n_in_ring = 12
        el_rs = 250  # TODO: make relative to screen size?
        el_thetas = np.linspace(0, 360, n_in_ring, endpoint=False)
        el_xys = np.array(misc.pol2cart(el_thetas, el_rs)).T
        ringtext = visual.TextStim(win=self.win, units='pix', bold=True,
                                   height=text_size, text='$')  # '$' will be changed
        cap_rect_norm = [
            -(text_size / 2.0) / (self.win.size[0] / 2.0),  # left
            +(text_size / 2.0) / (self.win.size[1] / 2.0),  # top
            +(text_size / 2.0) / (self.win.size[0] / 2.0),  # right
            -(text_size / 2.0) / (self.win.size[1] / 2.0)   # bottom
        ]
        for k in ['rew', 'neu']:
            ringtext.text = cues[k]['sym']
            ringtext.color = cues[k]['color']
            buff = visual.BufferImageStim(
                win=self.win,
                stim=[ringtext],
                rect=cap_rect_norm)
            # img = (np.flipud(np.array(buff.image)[..., 0]) / 255.0 * 2.0 - 1.0)
            self.ringimg[k] = visual.ElementArrayStim(
                win=self.win,
                units="pix",
                nElements=n_in_ring,
                sizes=buff.image.size,
                xys=el_xys,
                # colors=cues[k]['color'],
                elementMask=None,
                elementTex=buff.image)
    
    def read_timing(self,run_num, fname="dollar_reward_events.txt", n_start_iti=3, tr=1.5):
        """
        read in timing extracted from eprime1 .es file
        """
        if not os.path.exists(fname):
            raise Exception(f"cannot find eprime timing file! '{fname}'")
        print(fname)
        ep_df = pd.read_csv(fname,sep="\t", header=None)
        ep_df.columns=["run","epevent","position640", "ring_type","event_name"]
        ep_df['position'] = eppos2relpos(ep_df.position640, 640)
        ep_df = ep_df[ep_df.run==run_num].reset_index()
        start_fix = pd.DataFrame({'event_name':['iti']*n_start_iti})
        onset_df = pd.concat([start_fix, ep_df])
        onset_df['onset'] = [x*tr for x in range(len(onset_df))]
        return onset_df

    def read_timing_tr_independent(self, fname):
        """
        timing that is not tr locked -- entirely specified by csv
        """
        if not os.path.exists(fname):
            raise Exception(f"cannot find non-tr locked timing file! '{fname}'")
        print(fname)
        df = pd.read_csv(fname, sep="\t")
        print(df)
        df['position'] = eppos2relpos(df.position, 640)
        return df


    def generate_timing(n=40, dur=1.5, n_catch1=6, n_catch2=6):
        """
        generate timing with catches for rew and neutral
        not implemented, unfinished
        """
        from lncdtask import shuf_for_ntrials
        n_catch = n_catch1 + n_catch2 # 12
        n_full = n - n_catch          # 28
        rew_type    = ['rew','neu']

        positions = [-1,-.66,-.33,.33,.66,1]

        # full trials. balence left/rigth and rew/neu
        partition_size = floor(n_full/4) # TODO: warn if not even?
        trial_list = []
        for side in ['left','right']:
            for rew in rew_type:
                pos_opts = positions[0:3] if side == "left" else positions[3:]
                pos_vec = shuf_for_ntrials(pos_opts, partition_size)
                df = pd.DataFrame({'ring_type':rew, 'side': side, 'pos': pos_vec, 'trial_type':'full', 'dur': tr*3})
                trial_list.append(df)

        # catch trials
        for ctype in ['catch1','catch2']:
            n_thiscatch = n_catch1 if ctype=="catch1" else n_catch2
            partition_size = n_thiscatch/2 # 3 for each reward type
            dur = tr if ctype=="catch1" else tr*2
            for rew in rew_type:
                df = pd.DataFrame({'ring_type':rew, 'side': side, 'pos': pos_vec, 'trial_type': ctype})
                trial_list.append(np.repeat(df.valuse,partition_size,axis=0))
        
        # break into events
        # TODO: random extra fixations
        events = { 'full': ['ring','prep','sac'],
                   'catch1': ['ring','prep'],
                   'catch2': ['ring']}
        event_list = []
        for i, row in pd.concat(trial_list).iterrows():
            evs = events[row['trial_type']]
            event_dict = row.to_dict()
            event_dict.update({'event_names': evs + ['fix']})
            print(event_dict)
            df = pd.DataFrame(event_dict)
            df['dur'] = tr
            event_list.append(df)
        
        onset_df = pd.concat(event_list)
        onset_df['onset'] = np.cumsum(onset_df.dur)

    def excersise(self):
       # exercise functions

       from psychopy import core
       from lncdtask import wait_until
       t = core.getTime()
       #self.DEBUG = True

       self.ring(t, 'rew', .75)
       self.prep(t+1, 'rew', .75)
       self.dot(t+2, 'rew', .75)
       wait_until(t+3)
       

       # run with hard coded timing
       onset_df= pd.DataFrame({
         'onset'     :[     0,      1,     2,     3,     5  ],
         'event_name':['ring', 'prep', 'dot', 'iti', 'ring' ],
         'ring_type': ['neu',  'neu',  'neu', 'neu',  'rew' ],
         'position':  [.75,      .75,    .75,   .75,      1 ]
       })
       self.set_onsets(onset_df)
       self.run(t+3)


if __name__ == "__main__":
    from lncdtask import ExternalCom, FileLogger, Participant, RunDialog
    from time import time
    printer = ExternalCom()
    logger = FileLogger()

    n_runs=4
    eyetracker = None
    participant = None
    # 20220825 - mgs task has port as 0xD010. earlier as DDF8
    #            0xDDF8 == 56824; 0xD010=53264
    run_info = RunDialog(extra_dict={'EyeTracking': ['EEG', 'Arrington','ArringtonSocket', 'None'],
                                     'screenhack': False,
                                     'fullscreen': True,
                                     'truncated': False,
                                     'LPTport': "53264"},
                             order=['run_num','subjid', 'timepoint', 'EyeTracking', 'fullscreen','screenhack', 'LPTport'])

    
    # if we specify file(s) as arguments. read as though they're tr independent files
    # see [[file:../timing/timing_to_txt.R::afni_to_task]]
    # otherwise use ../dollar_reward_events.txt (old, from original eprime version)
    # this should/can be set by .bat files
    import sys
    if len(sys.argv)>1:
        from random import shuffle
        tfiles = sys.argv[1:]
        shuffle(tfiles)  # rearrange inpace/side-effect
        n_runs = len(sys.argv) - 1
        read_file_func = lambda dr, runnum: dr.read_timing_tr_independent(fname=tfiles[runnum-1])
    else:
        read_file_func = lambda dr, runnum: dr.read_timing(runnum, fname="dollar_reward_events.txt")

    # open a dialog and then a psychopy window for each run
    while run_info.run_num() <= n_runs:
        if not run_info.dlg_ok():
            break
        
        # update participant (logging info)
        if run_info.has_changed('subjid') or participant is None:
            participant = run_info.mk_participant(['DollarReward'])
            

        run_num = run_info.run_num()

        if run_info.info['screenhack']:
            # pygame (default), pyglet (newer), glfw (experimental)
            # MR res = [1024,768]
            # fullscreen doesn't exist. goes into power saving mode
            win = visual.Window([1024,768])#, winType='pyglet')
            win.winHandle.activate()  # make sure the display window has focus
            win.mouseVisible = False  # and that we don't see the mouse
            win.color = (-1, -1, -1)
            win.flip()
            win.flip()
        else:
            win = create_window(run_info.info['fullscreen'])
        dr = DollarReward(win=win, externals=[printer])
        dr.gobal_quit_key()  # escape quits
        dr.DEBUG = True

        # read_file_func goes through specified files
        # or defaults to original eprime task list
        onset_df = read_file_func(dr, run_num)

        if run_info.info['truncated']:
            onset_df = onset_df[0:5]

        dr.set_onsets(onset_df)
        dr.trialnum = 0

        # write to external files
        run_id = f"{participant.ses_id()}_task-DR_run-{run_num}"
        if run_info.info['EyeTracking'] == "Arrington":
            from externalcom import Arrington
            eyetracker = Arrington()

        elif run_info.info['EyeTracking'] == "ArringtonSocket":
            from arrington_socket import ArringtonSocket
            eyetracker = ArringtonSocket()
        elif run_info.info['EyeTracking'] == 'EEG':
            from externalcom import ParallelPortEEG
            port = int(run_info.info['LPTport'])
            eyetracker = ParallelPortEEG(port, lookup_func=ttl_wrap, verbose=False)
        else:
            eyetracker = None

        if eyetracker:
            dr.externals.append(eyetracker)
            eyetracker.new(run_id)
        else:
            print("WARNING: tracker is None, selected '%s'" %
                    run_info.info['EyeTracking'])

        # added after eyetracker
        # timing more important to eyetracker than log file
        logger.new(participant.log_path(run_id))
        dr.externals.append(logger)

        # how do we  trigger start?
        # if EEG keyboard should go?
        triggers = ['equal']
        if run_info.info['EyeTracking'] in ['EEG']:
            triggers = None

        # RUN
        dr.get_ready(triggers=triggers)
        dr.run(end_wait=1.5)
        dr.onset_df.to_csv(participant.run_path(f"onsets_{run_num:02d}"))
        dr.msg(f"Finished run {run_num}/{n_runs}!")
        dr.win.close()

        run_info.next_run()
