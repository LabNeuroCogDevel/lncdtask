#!/usr/bin/env python3
"""
Rest "task" can be used
 1. Without participant facing visuals (task projector off) to track MR Scanner TR TTL (scanner sent '=')
    a. Forwarded TR events to an eye track for syncing MR timing
    b. Measuring TR intervals for sequence and hardware debugging. Background changes color based on start and unequal time between TR.
 2. With visual presented to the participant (w/o without a fixation cross)
"""
try:
    from lncdtask import (
        LNCDTask,
        create_window,
        replace_img,
        wait_for_scanner,
        ExternalCom,
        RunDialog,
        FileLogger,
    )
except ImportError:
    from lncdtask.lncdtask import (
        LNCDTask,
        create_window,
        replace_img,
        wait_for_scanner,
        ExternalCom,
        RunDialog,
        FileLogger,
    )

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from psychopy import core, event, visual


class RestTask(LNCDTask):
    """
    Show an empty screen. Send scanner TTL ('=') onto EyeLink
    """

    def __init__(self, *karg, **kargs):
        """create DollarReward task. like LNCDTask,
        need onset_df and maybe win and/or participant
        this also adds a ringimg dictionary and an imageratsize (dotsize)
        >> win = create_window(False)
        >> r = RestTask(win=win)
        >> r.watch_keys()
        >> # r.run()
        """
        self.times = []
        self.tr = 0
        super().__init__(*karg, **kargs)

    def new_tr(self, time: float) -> float:
        """
        Add time of tr and calculate tr
        set self.tr if not set
        """
        self.times.append(float(time))
        if len(self.times) <= 1:
            return 0

        tr = self.times[-1] - self.times[-2]
        # set to first
        if self.tr == 0:
            self.tr = tr
        return tr

    def with_instructions(self, cnt=0, time=0, code="rest flip"):
        """show instructions about resting state"""
        self.mark_external(code)

        tr = self.new_tr(time)
        tr_diff = tr - self.tr
        # window color changes when starting
        # and when TR is not consistent
        if cnt == 1:
            visual.Rect(self.win, size=(2, 2), fillColor="blue").draw()
        elif abs(tr_diff) > 0.5:
            visual.Rect(self.win, size=(2, 2), fillColor="red").draw()

        ## write instructions
        self.msgbox.pos = (0, -0.6)
        self.msgbox.text = (
            "Turn of projector.\n"
            + "Instructions: keep eyes open and let mind wonder.\n\n"
            + "Push q to quit\n"
            + "waiting for scanner ('=')"
        )
        self.msgbox.draw()

        if cnt or time:
            self.msgbox.pos = (0, 0.3)
            self.msgbox.text = (
                f"Scanner TTL/TR pulse count: {cnt or 0}\n"
                + f"Total rest time: {time or 0}\n"
                + (
                    f"TR: first={self.tr:.2f} cur={tr:.2f} (diff={tr_diff:.2f})\n"
                    if self.tr > 0
                    else ""
                )
            )
            self.msgbox.draw()

        flip = self.win.flip()
        return {"flip": flip}

    def run(self, cross):
        if cross:
            self.iti(code="RestTask launched")
        else:
            self.with_instructions(0, 0, "launched")

        starttime = 0
        cnt = 0
        while True:
            key = event.waitKeys(keyList=["equal", "q"])
            # print(key)
            pushtime = core.getTime()
            if key[0] == "q":
                break

            if starttime == 0:
                starttime = pushtime
            time = "%.3f" % (pushtime - starttime)
            msg = f"{cnt} {time}"
            cnt = cnt + 1
            if cross:
                self.iti(0, code=msg)
            else:
                self.with_instructions(cnt, time, code=msg)


def parse_args(argv):
    """Argparser for Resting State Task. see 'lncd_rest --help'"""
    import argparse

    parser = argparse.ArgumentParser(description="Run Eye Calibration")
    parser.add_argument(
        "--tracker",
        choices=["eyelink", "", "arrington"],
        default="eyelink",
        help="how to track eyes",
    )
    parser.add_argument(
        "--no_fullscreen",
        default=False,
        action="store_true",
        help="show task fullscreen? useful for debugging",
    )
    parser.add_argument(
        "--cross",
        default=False,
        action="store_true",
        help="show fixation cross; otherwise expect screen to be turned off",
    )
    parser.add_argument("--subj", default="000", help="default subject id")
    parser.add_argument(
        "--sess", default="1", help="default session label. use 'now' for yyyymmdd"
    )
    parser.add_argument(
        "--subj_root",
        default=Path.home() / "Desktop" / "task_data",
        help="where to save",
    )
    parser.add_argument(
        "--no_dialog", default=False, action="store_true", help="skip dialog window"
    )

    parsed = parser.parse_args(argv)
    return parsed


def run_rest(parsed):
    """
    Launch Rest Task
    """
    printer = ExternalCom()
    eyetracker = None
    run_info = RunDialog(
        extra_dict={
            "subjid": parsed.subj,
            "timepoint": parsed.sess,
            "show_cross": parsed.cross,
            "fullscreen": not parsed.no_fullscreen,
            "tracker": parsed.tracker,
        },
        order=["subjid", "run_num", "timepoint", "show_cross", "tracker"],
    )

    if parsed.no_dialog:
        pass  # skip dialog
    elif not run_info.dlg_ok():
        sys.exit()

    # create task
    win = create_window(run_info.info["fullscreen"])
    eyecal = RestTask(win=win, externals=[printer])
    eyecal.gobal_quit_key()  # escape quits
    eyecal.DEBUG = True

    participant = run_info.mk_participant(["RestTask"], subj_root=parsed.subj_root)
    run_id = f"{participant.ses_id()}_task-rest_run-{run_info.run_num()}"

    if run_info.info["tracker"] == "arrington":
        try:
            # as module
            from lncdtask.externalcom import Arrington
        except ImportError:
            # as script
            from externalcom import Arrington
        eyetracker = Arrington()
        eyecal.externals.append(eyetracker)
        eyetracker.new(run_id)
    elif run_info.info["tracker"] == "eyelink":
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

    eyecal.run(run_info.info["show_cross"])
    win.close()


def main():
    """
    Run Rest Task from CLI
    """
    parsed = parse_args(sys.argv[1:])
    print(parsed)
    run_rest(parsed)


if __name__ == "__main__":
    main()
