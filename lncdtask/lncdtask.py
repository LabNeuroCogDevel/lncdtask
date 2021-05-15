#!/usr/bin/env python3
# -*- py-which-shell: "ipython"; -*-
# -*- elpy-use-ipython: "ipython"; -*-
# python -m doctest -v mgs_task.py
"""Main module."""

from participant import Participant
from screen import wait_until, create_window, take_screenshot, msg_screen, replace_img, wait_for_scanner
from externalcom import Arrington, Eyelink, MuteWinSound, ParallelPortEEG, AllExternal, ExternalCom
from psychopy import visual

class EventRunner():
    """
    store function and arguments to use when an event is called
    """
    def __init__(self, func, args_cols):
        """store function and columns"""
        self.func = func
        self.args_cols = args_cols

    def run(event_row):
        """
        event_row pandas row. hopefully with columns matching args_cols
        """
        event_info = event_row.to_dict()
        event_info = {event_info.get(x) for x in self.arg_cols}
        self.func(**event_info)


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
            win = create_window()
        self.win = win
        
        # could have just one and change the color
        self.iti_fix = visual.TextStim(win, text='+', name='iti_fixation',
                                       color='white', bold=True)
        self.isi_fix = visual.TextStim(win, text='+', name='isi_fixation',
                                       color='yellow', bold=True)
        self.cue_fix = visual.TextStim(win, text='+', name='cue_fixation',
                                       color='royalblue', bold=True)

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
        self.events = [{}]      # dictionary of event=>EventRunners
        self.resutls = [{}]
        if onset_df is not None:
            self.add_onsets(onset_df)
            
        

    def add_onsets(self, onset_df):
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
    
    def run(self):
        """
        run through onset_df, running events when we have them
        """
        if self.onset_df is None:
            raise Exception("no timing exsits. use add_onsets()")
        for (i, row) in self.onset_df.iterrows():
            event = self.events.get(row['event_name'], None)
            if event is None:
                print(f"WARNING: unknown event '{event}'. add it with add_event_type()!")
                continue

            self.results[i] = self.events[event].run(x)

      
    # --- here as examples
    def iti(self, onset=0, code='iti'):
        self.iti_fix.draw()
        self.win.callOnFlip(self.externals.event, code)
        showtime = self.win.flip()
        return({'flip': showtime})

    def isi(self, onset=0, code='isi'):
        self.isi_fix.draw()
        self.win.callOnFlip(self.externals.event, code)
        showtime = self.win.flip()
        return({'flip': showtime})

    def add_default_events(self):
        self.events['isi'] = EventRunner(self.isi, ['onset'])
        self.events['iti'] = EventRunner(self.iti, ['onset'])



    
