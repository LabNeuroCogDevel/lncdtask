"""
participant info
"""
import datetime
import os
import re
from time import time




def vdate_str():
    """
    return YYYYMMDD format for right now
    >>> import re; re.match(vdate_str, '^\d{8}$')
    True
    """
    datestr = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
    return(datestr)

class Participant():
    """ participant info
    generate (and create) a path to save subjects visit data
    directory for subject and task like "10931/01_eeg_A"
    """
    def __init__(self, subjid, task_info, vdate=None, timepoint=1, subj_root="subj_info", mkdir=True):
        """
        store participant info (subjid, vdate) and optionally make directories
        >>> x = Participant(subjid="XX", task_info=["task-1","type-a"], mkdir=False)
        >>> x.datadir
        subj_info/XX/task-1_type-a_20...
        >>> x.logdir
        subj_info/XX/task-1_type-a_20.../log
        """
        # remove date from id if it is the last bit ("xxxx_YYYYMMDD" -> "xxxx")
        self.vdate = vdate if vdate else vdate_str()
        self.timepoint = "%02d" % timepoint
        # remove "_vdate" from subjid if given
        self.subjid = re.sub("_%s$" % self.vdate, "", subjid)
        
        # subj_info/subj/timepoint_date/modality_set_date/
        tpdir = self.timepoint
        tinfo_str = "_".join(task_info)
        lastdir = "_".join([self.vdate, tinfo_str])
        self.datadir = os.path.join(subj_root, "sub-" + subjid, "ses-" + tpdir, lastdir)
        self.logdir = os.path.join(self.datadir, 'log')
        if mkdir:
            os.makedirs(self.logdir, exist_ok=True)

    def run_path(self, bname):
        return os.path.join(self.datadir,"%s-%.0f.csv"  % (bname, time()))

    def log_path(self, bname):
        return os.path.join(self.logdir,"%s-%.0f.log" % (bname, time()))

    def ses_id(self, use_date=False):
        "bids format session id: sub-XXX_ses-yyy. can use yyyymmdd for ses or timepoint"
        ses = self.vdate if use_date else self.timepoint
        return "sub-%s_ses-%s" % (self.subjid, ses)

