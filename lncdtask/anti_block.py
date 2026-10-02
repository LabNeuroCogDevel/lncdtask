#!/usr/bin/env python3
import numpy as np
import psychopy
import lncdtask
try:
    from lncdtask import LNCDTask, create_window, replace_img, wait_for_scanner,\
        ExternalCom, FileLogger, Participant, RunDialog,\
        wait_until, shuf_for_ntrials
except ImportError as e:
    print(e)
    from lncdtask.lncdtask import LNCDTask, create_window, replace_img, wait_for_scanner,\
        ExternalCom, FileLogger, Participant, RunDialog, \
        wait_until, shuf_for_ntrials

import pandas as pd

## setup. timing from EEG vgs_anti
block_reps = 2
blocks = np.random.permutation(['rew', 'neu','vgs'])
between_block = 45 # seconds
event_dur = 1.5
colors = {'neu': 'blue',
          'rew': 'red',
          'vgs': 'lightgreen'}
dur = {'iti': [1]*10 + [1.5]*5 + [2]*3 + [2.5]*2,
       'prep': .5,
       'dot': 1}
pos = {'far_left': -.85,
       'far_right': .85}


## utilities
def maxreps(v):
    """
    whats the longest string of repeats
    >>> maxreps([1,2,3,1])
    1
    >>> maxreps([1,1,2,1])
    2
    >>> maxreps([1,1,2,1,2,2,2])
    3
    """
    prev, maxrep, currep = (v[0], 0, 0)
    for i, cur in enumerate(v):
        if i < 1: continue
        if prev == cur:
            currep = currep + 1
        else:
            currep = 0
        if currep > maxrep:
            maxrep = currep
        prev = cur
    return maxrep+1

ntrials_per_block = len(dur['iti'])
calc_block_time = ntrials_per_block*(dur['prep'] + dur['dot']) + np.sum(dur['iti'])
# 20 trials in a block, 58.5 seconds
task_info_msg = f"{ntrials_per_block} trials in a block, {calc_block_time} seconds. {between_block} seconds between. for blocks {blocks}"
print(task_info_msg)


class AntiBlock(LNCDTask):
    def __init__(self, *karg, **kargs):
        """
        >> win = lncdtask.screen.create_window(False)
        >> onset_df= pd.DataFrame({'onset':[0], 'event_name':['ring']})
        >> printer = lncdtask.ExternalCom()
        >> dr = DollarReward(win=win, onset_df=onset_df, externals=[printer])
        >> dr.ring(0, 'rew')
        """
        super().__init__(*karg, **kargs)
        self.add_event_type('blockbreak', self.cross, ['onset','color'])
        self.add_event_type('iti', self.cross, ['onset','color'])
        self.add_event_type('prep', self.cross, ['onset','color'])
        self.add_event_type('dot', self.dot, ['onset','pos'])
        self.add_event_type('done', self.done, ['onset'])
        self.add_event_type('note', self.note, ['onset', 'block','color'])

    def note(self, onset, block='MIA', color='white'):
        """fixation cross. prep cue or iti"""
        self.msgbox.color = color
        self.msgbox.text = "Next block: %s" % block
        self.msgbox.draw()
        self.msgbox.color='white' # revert
        return(self.flip_at(onset,'note', block, color))

    def cross(self, onset, color='white'):
        """fixation cross. prep cue or iti"""
        self.cue_fix.color = color
        self.cue_fix.draw()
        return(self.flip_at(onset,'cross',color))

    def dot(self, onset, pos=.9):
        """position dot on horz axis to cue anti saccade
        position is from -1 to 1
        """
        # hack to get dot size
        self.crcl.pos =(pos*self.win.size[1]//2,0)
        self.crcl.size=(1,1)
        self.crcl.draw()
        return(self.flip_at(onset, 'dot', str(pos)))

    def done(self, onset):
        self.msgbox.text = "All Done!"
        self.msgbox.draw()
        return(self.flip_at(onset,'done'))



def build_time():
    df = []
    for bi, btype in enumerate(blocks):
        # TODO: fixed schedule
        pos_seq=None
        while pos_seq is None or maxreps(pos_seq) > 3:
            pos_seq = np.random.permutation((list(pos.keys())*(ntrials_per_block//2)))
        itis = np.random.permutation(dur['iti'])

        df.append({'block':btype, 'pos': None, 'event_name': 'note', 'edur': 1, 'color': colors[btype]})
        df.append({'block':btype, 'pos': None, 'event_name': 'iti', 'edur': 3, 'color': 'white'})

        for i in range(ntrials_per_block):
            trial_info= {'block':btype, 'pos': pos[pos_seq[i]]}
            df.append({**trial_info, 'event_name': 'prep', 'edur': dur['prep'], 'color': colors[btype]})
            df.append({**trial_info, 'event_name': 'dot', 'edur': dur['dot'], 'color': None})
            df.append({**trial_info, 'event_name': 'iti', 'edur': itis[i], 'color': 'white'})

        # no rest after the final block
        if bi < len(blocks)-1:
            # kludge. >30s throws an error. wait 45/2. also gives us a chance to escape
            df.append({'block':btype, 'pos': None, 'event_name': 'blockbreak', 'edur': between_block/2, 'color': 'gray'})
            df.append({'block':btype, 'pos': None, 'event_name': 'blockbreak', 'edur': between_block/2, 'color': 'gray'})

    df.append({'block':None, 'pos': None, 'event_name': 'done', 'edur': 0, 'color': None})

    df = pd.DataFrame(df)
    df['endtime'] = np.cumsum(df.edur)
    df['onset'] = [0, *df.endtime[:-1]]
    return df

def run():
    onsets = build_time()

    sub = Participant("pilot",task_info=["anti_block"])
    onsets.to_csv(sub.run_path(f"onsets-init"))

    ab = AntiBlock(onset_df=onsets)

    logger = FileLogger()
    logger.new(sub.log_path(bname='x'))
    ab.externals.append(logger)

    printer = ExternalCom()
    ab.externals.append(printer)


    # instructions
    ab.msg("""
Welcome to the Saccade Task!
    Look at the cross.
    Get ready when it changes colors.
    Look to or opposite the dot that appears.
    continue to look at the correct location until the cross apears again.
""")
    ab.msg(f"""
When the cross is
  Green = Look at dot (easy!)
  Red = Look away. Get points and a reward.
  Blue = Look away but no reward

  Gray means rest

Hold the correct location until the the cross returns.
{task_info_msg}; end at {list(onsets.endtime)[-1]}
""")
    wait_for_scanner(ab.msgbox, msg="Waiting for scanner ('=')")

    ab.gobal_quit_key()  # escape quits
    #ab.DEBUG = True
    ab.run()
    ab.onset_df.to_csv(sub.run_path(f"onsets"))

    ab.msg("All Done!")


if __name__ == "__main__":
    run()
