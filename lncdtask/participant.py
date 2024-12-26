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
    >>> import re
    >>> re.match('^[0-9]{8}$', vdate_str()) # doctest: +ELLIPSIS
    <re.Match object; span=(0, 8), match='20...
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
        >>> x.datadir # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        'subj_info/sub-XX/ses-01/20..._task-1_type-a'
        >>> x.logdir # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        'subj_info/sub-XX/ses-01/20..._task-1_type-a/log'

        >>> x = Participant(subjid="XX", task_info=["a"], timepoint='abc', mkdir=False)
        >>> x.logdir # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        'subj_info/sub-XX/ses-abc/20..._a/log'

        >>> x = Participant(subjid="XX", task_info=["a"], timepoint='now', mkdir=False)
        >>> x.logdir # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        'subj_info/sub-XX/ses-20.../a/log'
        """
        # remove date from id if it is the last bit ("xxxx_YYYYMMDD" -> "xxxx")
        self.vdate = vdate if vdate else vdate_str()
        if isinstance(timepoint, int) and int(timepoint) < 10:
            self.timepoint = "%02d" % timepoint
        elif timepoint == 'now':
            self.timepoint = vdate_str()
        else:
            self.timepoint = str(timepoint)
        # remove "_vdate" from subjid if given
        self.subjid = re.sub("_%s$" % self.vdate, "", subjid)

        # subj_info/subj/timepoint_date/modality_set_date/
        tpdir = self.timepoint
        taskdir = "_".join(task_info)

        # add yyyymmdd to task name for posterity
        # but not needed if session already encodes that
        if timepoint != 'now':
            lastdir = self.vdate + "_" + taskdir
        else:
            lastdir = taskdir
        self.datadir = os.path.join(subj_root, "sub-" + subjid, "ses-" + tpdir, lastdir)
        self.logdir = os.path.join(self.datadir, 'log')
        if mkdir:
            os.makedirs(self.logdir, exist_ok=True)

    def run_path(self, bname):
        return os.path.join(self.datadir,f"{bname}-{time():.0f}.csv")

    def log_path(self, bname):
        return os.path.join(self.logdir,f"{bname}-{time():.0f}.log")

    def ses_id(self, use_date=False):
        "bids format session id: sub-XXX_ses-yyy. can use yyyymmdd for ses or timepoint"
        ses = self.vdate if use_date else self.timepoint
        return f"sub-{self.subjid}_ses-{ses}"

