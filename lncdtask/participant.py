"""
participant info
"""
import datetime
import os
import re




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
    def __init__(self, subjid, task_info, timepoint=1, subj_root="subj_info", mkdir=True):
        """
        store participant info (subjid, vdate) and optionally make directories
        >>> x = Participant(subjid="XX", task_info=["task-1","type-a"], mkdir=False)
        >>> x.datadir
        subj_info/XX/task-1_type-a_20...
        >>> x.logdir
        subj_info/XX/task-1_type-a_20.../log
        """
        # remove date from id if it is the last bit ("xxxx_YYYYMMDD" -> "xxxx")
        self.vdate = vdate_str()
        self.subjid = re.sub("_%s$" % vdate, "", subjid)
        
        # subj_info/subj/timepoint_date/modality_set_date/
        tpdir = "%02d" % int(timepoint)
        lastdir = "_".join([*task_info, vdate])
        self.datadir = os.path.join(subj_root, subjid, tpdir, lastdir)
        self.logdir = os.path.join(datadir, 'log')
        if mkdir:
            os.makedirs(self.logdir, exist_ok=True)
