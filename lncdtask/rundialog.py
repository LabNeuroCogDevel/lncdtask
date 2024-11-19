from psychopy.gui import DlgFromDict

from participant import Participant

class RunDialog():
    """
    small wrapper around pyschopy's dialog
    and loose integration with Participant

    * stores dialog results in 'info', tracks 'prev'
    * 'run_num' can be incremented
    """
    def __init__(self, extra_dict={}, order=['run_num','subjid', 'timepoint']):
        self.info = {'subjid': "000", 'run_num': 1, 'timepoint': 1, **extra_dict}
        self.prev = {**self.info}
        self.order = order

    def next_run(self):
        self.info['run_num'] += 1

    def dlg_ok(self):
        """returns true if okay; sideeffect: changes self.info"""
        self.prev = {**self.info}
        dlg = DlgFromDict(self.info, order=self.order)
        return dlg.OK

    def run_num(self):
        return self.info['run_num']
    
    def has_changed(self, key):
        return self.prev.get(key) != self.info.get(key)

    def mk_participant(self, task_info=[], **kargs):
       return Participant(self.info['subjid'], task_info, timepoint=self.info['timepoint'], **kargs)
