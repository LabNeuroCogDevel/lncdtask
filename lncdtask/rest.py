#!/usr/bin/env python3
try:
    from lncdtask import LNCDTask, create_window, replace_img, \
            wait_for_scanner, ExternalCom, RunDialog, FileLogger
except ImportError:
    from lncdtask.lncdtask import LNCDTask, create_window, replace_img,\
            wait_for_scanner, ExternalCom, RunDialog, FileLogger

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from psychopy import core, event


class RestTask(LNCDTask):
    """
    show an empty screen. send scanner tll ('=') onto EyeLink
    """
    def __init__(self, *karg, **kargs):
        """ create DollarReward task. like LNCDTask,
        need onset_df and maybe win and/or participant
        this also adds a ringimg dictionary and an imageratsize (dotsize)
        >> win = create_window(False)
        >> r = RestTask(win=win)
        >> r.watch_keys()
        >> # r.run()
        """
        super().__init__(*karg, **kargs)


    def with_instructions(self, cnt=None, time=None, code="rest flip"):
        """show instructions about resting state
        """
        self.mark_external(code)
        self.msgbox.pos = (0,.6)
        self.msgbox.text = 'Turn of projector.\nInstructions: keep eyes open and let mind wonder.\n\nPush q to quit'
        self.msgbox.draw()
        if cnt or time:
            self.msgbox.pos = (0,0)
            self.msgbox.text = f'Scanner TTL/TR pulse count: {cnt}\nTotal rest time: {time}'
            self.msgbox.draw()
        flip = self.win.flip()
        return({'flip': flip})

    def run(self, cross):
        if cross:
            flip_on = self.iti(code="rest launched")
        else:
            self.with_instructions(0,0)

        starttime = 0
        cnt = 0
        while True:
            key = event.waitKeys(keyList=["equal","q"])
            print(key)
            pushtime = core.getTime()
            if key[0] == "q":
                break

            if starttime == 0:
                starttime = pushtime
            time = "%.2f" % (pushtime - starttime)
            msg = f"{cnt} {time}"
            cnt = cnt + 1
            if cross:
                self.iti(0,code=msg)
            else:
                self.with_instructions(cnt, time, code=msg)


def parse_args(argv):
    import argparse
    parser = argparse.ArgumentParser(description='Run Eye Calibration')
    parser.add_argument('--tracker',
                        choices=["eyelink"],
                        default="eyelink",
                        help='how to track eyes')
    parser.add_argument('--no_fullscreen',
                        default=False,
                        action='store_true',
                        help='show task fullscreen? useful for debugging')
    parser.add_argument('--cross',
                        default=False,
                        action='store_true',
                        help='show fixation cross; otherwise expect screen to be turned off')
    parser.add_argument('--subj_root',
                        default=Path.home()/"Desktop"/"task_data",
                        help='where')

    parsed = parser.parse_args(argv)
    return(parsed)


def run_rest(parsed):
    printer = ExternalCom()
    eyetracker = None
    run_info = RunDialog(extra_dict={'show_cross': parsed.cross,
                                     'fullscreen': not parsed.no_fullscreen,
                                     'tracker': parsed.tracker,
                                     },
                         order=['subjid', 'run_num',
                                'timepoint', 'show_cross', 'tracker'])

    if not run_info.dlg_ok():
        sys.exit()

    # create task
    win = create_window(run_info.info['fullscreen'])
    eyecal = RestTask(win=win, externals=[printer])
    eyecal.gobal_quit_key()  # escape quits
    eyecal.DEBUG = True

    participant = run_info.mk_participant(['RestTask'], subj_root=parsed.subj_root)
    run_id = f"{participant.ses_id()}_task-rest_run-{run_info.run_num()}"

    if run_info.info['tracker'] == 'arrington':
        try:
            # as module
            from lncdtask.externalcom import Arrington
        except ImportError:
            # as script
            from externalcom import Arrington
        eyetracker = Arrington()
        eyecal.externals.append(eyetracker)
        eyetracker.new(run_id)
    elif run_info.info['tracker'] == "eyelink":
        try:
            # as module
            from lncdtask.externalcom import Eyelink
        except ImportError:
            # as script
            from externalcom import Eyelink
        eyetracker = Eyelink(win.size)
        eyecal.externals.append(eyetracker)
        eyetracker.new(run_id)

    logger = FileLogger()
    logger.new(participant.log_path(run_id))
    eyecal.externals.append(logger)

    eyecal.run(run_info.info['show_cross'])
    win.close()


def main():
    parsed = parse_args(sys.argv[1:])
    print(parsed)
    run_rest(parsed)


if __name__ == "__main__":
    main()
