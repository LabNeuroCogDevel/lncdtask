from lncdtask import LNCDTask, create_window
from psychopy import misc, visual
import numpy as np
import pandas as pd

"""
switch between a message event and an iti event
message event has two parameters
"""


class HelloWorldTask(LNCDTask):
    def __init__(self, *karg, **kargs):
        """ small example task """
        super().__init__(*karg, **kargs)

        # stim to display. self.win provided by LNCDTask
        self.name = visual.TextStim(self.win, text='', name='name', color='white', bold=True)
        # how to handle event_names
        self.add_event_type('mesg', self.mesg, ['onset','mesg','name'])
        self.add_event_type('iti', self.iti, ['onset'])   # self.iti defined in LNCDTask

    def mesg(self, onset, mesg, name):
        self.name.text = f"{mesg} {name}"
        self.name.draw()
        flip_dict = self.flip_at(onset, mesg, name)
        return(flip_dict)

if __name__ == "__main__":
    from lncdtask import ExternalCom
    from psychopy import core
    from screen import wait_for_scanner
    printer = ExternalCom() # todo: use Arrington or EyeLink or ParallelPortEEG
    task = HelloWorldTask(externals=[printer])

    # describe events
    onset_df= pd.DataFrame({
      'onset'     :[     0,     1,           1.5,   2.5,    3  ],
      'event_name':['mesg', 'iti',        'mesg', 'iti', 'mesg' ],
      'mesg':      ['Hello', None,     'Goodbye',  None, 'DONE' ],
      'name':      ['World', None, 'cruel world',  None, ''     ]
    })

    # add events to task
    task.set_onsets(onset_df)
    # wait for keypress to say we are ready
    wait_for_scanner(task.msgbox, ['equal'])

    # run it
    flip_times = task.run()
    # wait one second (display last) before quiting
    core.wait(1) 
    task.win.close()
    print(f"fliptimes: {flip_times}")
