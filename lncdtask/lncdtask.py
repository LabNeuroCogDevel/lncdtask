#!/usr/bin/env python3
# -*- py-which-shell: "ipython"; -*-
# -*- elpy-use-ipython: "ipython"; -*-
# python -m doctest -v mgs_task.py
"""
LNCDTask: a wrapper around psychopy for "draw, flip, wait" tasks

If timing is fixed, `set_onsets()` and `run()` can push most of the burden of task programming onto a onset_df
dataframe
"""

# kludge: different imports depending on context
# lncdtask/dollarreward.py is run as though this isn't a module
# TODO: rework dollarreward as console script?
try:
    from participant import Participant
except ModuleNotFoundError:
    from os.path import dirname, abspath
    import sys
    this_file = abspath(__file__)
    package_root = dirname(this_file)
    print(f"inserting {package_root} to path")
    sys.path.insert(1, package_root)
    from participant import Participant

from rundialog import RunDialog
from screen import wait_until, create_window, take_screenshot, msg_screen, replace_img, wait_for_scanner
from externalcom import Arrington, Eyelink, MuteWinSound, ParallelPortEEG, AllExternal, ExternalCom, FileLogger
from arrington_socket import ArringtonSocket
from trial_shuffle import shuf_for_ntrials
import psychopy
from psychopy import visual, core

class EventRunner():
    """
    store function and arguments to use when an event is called
    """
    def __init__(self, func, args_cols, event_name=None):
        """store function and columns"""
        self.func = func
        self.args_cols = args_cols
        if event_name is None:
            event_name = self.func.__name__
        self.event_name = event_name

    def run(self, event_row):
        """
        event_row pandas row. hopefully with columns matching args_cols
        """
        event_info = event_row.to_dict()
        # could quickly use generator. but want to throw a warning when value is missing
        #event_vals = [event_info.get(x) for x in self.args_cols]

        event_vals = [None]*len(self.args_cols)
        for i, key in enumerate(self.args_cols):
            event_vals[i] = event_info.get(key)
            if event_vals[i] is None:
                print(f"WARNING! no value for column '{key}' when running event function '{self.event_name}'")

        return(self.func(*event_vals))


class LNCDTask():
    """
    generic task template.
    `run` is for fixed schedule. (cannot change order of events based on outcomes)
    has
     {cue,isi,iti}_fix 'TextStim' (default: blue,yellow,white)
     img  ImageStims (See img_replace)
     crcl Circle (yellow)
    
    """
    def __init__(self, onset_df=None, win=None, externals=[], participant=None):
        if win is None:
            win = create_window(True)
        self.win = win
        
        # could have just one and change the color
        self.iti_fix = visual.TextStim(win, text='+', name='iti_fixation',
                                       color='white', bold=True)
        self.isi_fix = visual.TextStim(win, text='+', name='isi_fixation',
                                       color='yellow', bold=True)
        self.cue_fix = visual.TextStim(win, text='+', name='cue_fixation',
                                       color='royalblue', bold=True)
        self.msgbox = visual.TextStim(win, text='', name='message_box',
                                       color='white', bold=True)

        # images
        self.img = visual.ImageStim(win, name="imgdot", interpolate=True)
        self.crcl = visual.Circle(win, radius=10, lineColor=None,
                                  fillColor='yellow', name="circledot")
        self.crcl.units = 'pix'


        # talk to the outside world
        self.externals = AllExternal(externals)
        # storing a place to write a log
        self.participant = participant

        # to be set
        self.events = {}      # dictionary of event=>EventRunners
        self.results = [{}]   # list of dict per event
        if onset_df is not None:
            self.set_onsets(onset_df)
        else:
            print("WARNING: lncdtask: missing onset_df. timing unmanaged")

        self.DEBUG = False

    def gobal_quit_key(self, key='escape'):
        if not psychopy.event.globalKeys.get(key):
            psychopy.event.globalKeys.add(key=key, func=self.mark_and_quit, name='shutdown')

    def mark_and_quit(self):
        self.mark_external("FORCE QUIT")
        self.externals.stop()
        core.quit()

    def mark_external(self, *kargs):
        """ print flip and send to external sources """
        msg=" ".join([str(x) for x in kargs])
        self.externals.event(msg)
        
    def msg(self, message):
        """
        mostly useless wrapper around screen.msg_screen.
        as part of LNCDTask, can use self.msgbox and wrap that part of mgs_screen
        return is response
        """
        resp = msg_screen(self.msgbox, message)
        return resp


    def flip_at(self, onset, *kargs, mark_func=None):
       """wait and then flip.
       send event notification to external sources with mark_func (def to mark_external)
       returns dictionary with 'flip' time"""
       if mark_func is None:
           mark_func = self.mark_external
       if len(kargs) > 0:
           self.win.callOnFlip(mark_func, *kargs)
       # timing
       wait_until(onset)
       flip = self.win.flip()
       return({'flip': flip})

    def eyelink_trial_mark_plus_external(self, trial, *kargs):
        """
        for SR EyeLink: want a trial start and end marker
        wraps flip_at's default 'mark_func' function
        """
        # push to flip_at as mark_func
        #self.win.callOnFlip(mark_func, *kargs)
        if self.eyelink:
            if self.trialnum > 1:
                self.eyelink.eyelink.trial_end()
            self.eyelink.eyelink.trial_start(trial)
        self.mark_external(*kargs)



    def set_onsets(self, onset_df):
        """
        add onsets dataframe for fixed timing using run

        onset_df is a dataframe with at least 'onset' and 'event' columns
        win is a psychopy window (will be creates if not provided)
        external is a list of external sources. e.g. [Arrington("newfile")])
        """

        if not 'onset' in onset_df.columns:
            raise Exception("onset_df must have 'onset' column")
        if not 'event_name' in onset_df.columns:
            raise Exception("onset_df must have 'event_name' column")

        # list of dictonaries for event outcomes
        n_events = onset_df.shape[0]
        self.onset_df = onset_df
        self.results = [{'fliptime': -1}] * n_events 
        

    def add_event_type(self, name, func, arg_cols=['onset']):
        """
        add a known event type
        """
        self.events[name] = EventRunner(func, arg_cols)
    
    def run(self, start_at=None, end_wait=0):
        """
        run through onset_df, running events when we have them
        """
        if self.onset_df is None:
            raise Exception("no timing exsits. use set_onsets()")
        if start_at is None:
            start_at = core.getTime()

        self.onset_df['onset0'] = self.onset_df.onset
        self.onset_df['onset'] = self.onset_df.onset + start_at
        
        # tell everyone we are starting
        self.externals.start()

        for (i, row) in self.onset_df.iterrows():
            event_name = row['event_name']
            ev = self.events.get(event_name, None)
            if self.DEBUG:
                print(row)
            if ev is None:
                print(f"WARNING: event {i} unknown event '{event_name}'. add it with add_event_type()!")
                continue

            self.results[i] = ev.run(row)


        # based on onsets. dont have durations. might need to wait at the end
        if end_wait:
            core.wait(end_wait)
        self.externals.stop()
        return(self.results)

      
    # --- Examples

    def run_instructions(self, instruction_funcs=[]):
        blue = '#000080'  # dark blue used in EPrime

        # can put this as default b/c 'self' doesn't exist at definition time
        if len(instruction_funcs) == 0:
            instruction_funcs=[self.instruction_welcome, self.instruction_ready]

        i=0;
        while True:
            resp = instruction_funcs[i]()
            print(f"instructions {i}: ran {instruction_funcs[i].__name__}, got {resp}")
            # allow presenter to go backwards
            # but most keys go forward until we run out of instruction_funcs
            if resp is None:
                print("WARNING: instruction function provided no response! can only move foward through instructions'")
                i += 1
            elif 'left' in resp and i > 0:
                i -= 1
            else:
                i += 1
            if i >= len(instruction_funcs):
                break

    def instruction_welcome(self, msg='Welcome to the Lab'):
        blue = '#000080'  # dark blue used in EPrime
        # 1. welcome - blue (b/c it was blue in EPrime)
        prev_bgcolor = self.win.color
        self.win.color = blue; self.win.flip()
        resp = self.msg(msg)
        if 'c' in resp and self.eyelink is not None:
            # TODO: two opengl screens? does this fail?
            self.eyelink.eyelink.eyeTrkCalib()


        # TODO: does this send in a way anyone can see? not recording yet
        if self.eyelink:
            self.eyelink.eyelink.trigger('instruct')

        # set bgcolor back to black
        self.win.color = prev_bgcolor; self.win.flip()
        return resp

    def instruction_ready(self,msg='Ready?\n\n(any key; esc to quit)'):
        return self.msg(msg)

    def iti(self, onset=0, code='iti'):
        self.iti_fix.draw()
        return(self.flip_at(onset, code))

    def isi(self, onset=0, code='isi'):
        self.isi_fix.draw()
        return(self.flip_at(onset, code))

    def add_default_events(self):
        self.events['isi'] = EventRunner(self.isi, ['onset'])
        self.events['iti'] = EventRunner(self.iti, ['onset'])
        #self.add_event_type('iti',self.iti)
        #self.add_event_type('isi',self.isi)
