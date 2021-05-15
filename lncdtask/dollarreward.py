from lncdtask import LNCDTask, create_window, wait_until, replace_img
from psychopy import misc, visual
import numpy as np
import pandas as pd

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

    From original:
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
        >> y = DollarReward(win=win, onset_df=onset_df, externals=[printer])
        >> y.ring(0, 'rew')
        """
        super().__init__(*karg, **kargs)
        self.ringimg = {}
        self.dotsize_edge = .15 # part of hack to get circle size
        self.make_ring()

    def ring(self, onset, ring_type, position=None):
        """ display ring: reward or neutral """
        self.ringimg[ring_type].draw()
        self.cue_fix.color = 'white'
        self.cue_fix.draw()
        return(self.generic_flip(onset,'ring', 'rew', position))

    def prep(self, onset, ring_type=None, position=None):
        """cue before onset"""
        self.cue_fix.color = 'red'
        self.cue_fix.draw()
        return(self.generic_flip(onset,'cue', ring_type, position))

    def dot(self, onset, ring_type=None, position=0):
        """position dot on horz axis to cue anti saccade
        position is from -1 to 1
        """
        # hack to get dot size
        imgpos = replace_img(self.img, None, position, self.dotsize_edge)
        self.crcl.pos = imgpos
        self.crcl.draw()
        return(self.generic_flip(onset,'dot', ring_type, position))
    
    def generic_flip(self, onset, *kargs):
        """wait and then flip. send event notification to external sources"""
        self.win.callOnFlip(self.print_and_send, *kargs)
        # timing
        wait_until(onset)
        flip = self.win.flip()
        return({'flip': flip})

    def print_and_send(self, event, pos, trialtype):
        """ print flip and send to external sources """
        # # left to right 1 to 5 from -1 -.5 .5 1 | no 0 (center), never see 3
        # pos_code = pos*2 + 3
        # ttl = pos_code + \
        #     eventTTLlookup.get(event, 0) +\
        #     100 * int(trialtype == 'rew')

        # send code
        self.externals.event(f"{event} {trialtype} {pos}")


    def make_ring(self, text_size=45):
        """ create the ring
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

    def generate_timing(n=15, dur=1.5, n_catch=3):
        """
        generate timing with catches for rew and neutral
        """
        events=['ring','prep','sac','iti']
        rew   =['rew','neu']


if __name__ == "__main__":
    from lncdtask import ExternalCom
    from psychopy import core
    win = create_window(False)
    onset_df= pd.DataFrame({'onset':[0], 'event_name':['ring']})
    printer = ExternalCom()
    y = DollarReward(win=win, onset_df=onset_df, externals=[printer])
    t = core.getTime()
    y.ring(t, 'rew', .75)
    y.prep(t+1, 'rew', .75)
    y.dot(t+2, 'rew', .75)
    wait_until(t+3)
    y.win.close()
