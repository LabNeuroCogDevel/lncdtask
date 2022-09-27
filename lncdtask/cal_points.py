#!/usr/bin/env python3
try:
    from lncdtask import LNCDTask, create_window, msg_screen
except ImportError:
    from lncdtask.lncdtask import LNCDTask, create_window, msg_screen
import numpy as np
import pandas as pd
import psychopy.core
from psychopy import event


def cpos(i, mx):
    """position (0,mx) on -1 to 1
    >>> cpos(0,3)
    -1
    >>> cpos(1,3)
    0
    >>> cpos(2,3)
    1"""
    return -1 + 2*i/(mx-1)


def nudge_edge(pos, nudge=.1):
    """dont want to be on the edge. so nudge off of it
    >>> nudge_edge(-1)
    -.9
    >>> nudge_edge(1)
    .9
    >>> nudge_edge(.5)
    .5
    """
    if abs(pos) == 1:
        nudge = nudge * (-1 if pos > 0 else 1)
        pos = pos + nudge
    return pos


def gen_dots(rows=3, cols=3):
    dot_pos = []
    for row in range(rows):
        for col in range(cols):
            xy = (nudge_edge(cpos(row, rows)), -1*nudge_edge(cpos(col, cols)))
            dot_pos.append(xy)
    return dot_pos


class ArrCal(LNCDTask):
    """
    show dot at calibration points
    """
    def __init__(self, *karg, **kargs):
        """
        >> win = create_window(False)
        >> dr = ArrCal(win=win, externals=[printer])
        >> dr.dot(0, .75)
        """
        super().__init__(*karg, **kargs)

        # extra stims/objects, exending base LNCDTask class
        self.trialnum = 0

        # events
        self.add_event_type('dot', self.dot, ['dot_i'])

        self.rows = 3
        self.cols = 3
        self.dot_pos = gen_dots(self.rows, self.cols)

    def draw_dot(self, i, color='gray'):
        x = self.dot_pos[i][0]
        y = self.dot_pos[i][1]
        self.crcl.pos = (x * self.win.size[0]/2,
                         y * self.win.size[1]/2)
        self.crcl.size = (1, 1)
        self.crcl.color = color
        self.crcl.draw()
        self.msgbox.pos = (x, y)
        self.msgbox.color = 'black'
        self.msgbox.text = str(i+1)
        self.msgbox.draw()

    def usage(self):
        self.msgbox.unit = 'pix'
        self.msgbox.pos = (-.5, -.9)
        self.msgbox.height = .05
        self.msgbox.color = 'gray'
        self.msgbox.text = "esc/q. #, space, arrow. enter to use"
        self.msgbox.draw()

    def dot(self, dot_i=0, used=False):
        """all dots in gray. primary in yellow"""
        self.trialnum = self.trialnum + 1
        self.usage()  # show instruction menu
        # draw all circles in gray
        for i in range(len(self.dot_pos)):
            self.draw_dot(i)
        # current in yellow
        color = 'red' if used else 'yellow'
        self.draw_dot(dot_i, color)
        return(self.flip_at(0, self.trialnum, 'dot', color))


if __name__ == "__main__":
    import sys
    import argparse
    from lncdtask import ExternalCom, RunDialog, FileLogger
    printer = ExternalCom()
    eyetracker = None

    parser = argparse.ArgumentParser(description='Run Eye Calibration')
    parser.add_argument('--tracker',
                        choices=["arrington", "test"],
                        default="arrington",
                        help='how to track eyes')
    parser.add_argument('--fullscreen',
                        choices=["yes", "no"],
                        default="yes",
                        help='run fullcreen?')
    parser.add_argument('--n',
                        type=int,
                        default=9,
                        help='how many points to use')
    parsed = parser.parse_args()
    print(parsed)

    # create task
    win = create_window(parsed.fullscreen == 'yes')
    eyecal = ArrCal(win=win, externals=[printer])
    eyecal.gobal_quit_key()  # escape quits
    eyecal.DEBUG = False

    if parsed.tracker == 'arrington':
        from externalcom import Arrington
        eyetracker = Arrington()
        eyecal.externals.append(eyetracker)
        # "calibration_SnapMode ON"
        # "calibration_Snap %d"

    dot_i = 0  # 0 to 9
    while True:
        # print instruction text text on bottom
        eyecal.msgbox.draw()
        # print(dot_i)
        eyecal.dot(dot_i)
        key = event.waitKeys()
        print(key)
        if key[0] in ['return']:
            eyecal.dot(dot_i, used=True)
            cmd = f"calibration_Snap {dot_i+1}"
            if eyetracker:
                eyetracker.vpxsend(cmd)
            else:
                print("# want to " + cmd)
            psychopy.core.wait(.1)
            eyecal.dot(dot_i)
        elif key[0] in ['q']:
            break
        elif key[0] in [str(i) for i in range(10)]:
            try:
                i = int(key[0])
                if i <= len(eyecal.dot_pos) and i > 0:
                    dot_i = i - 1
            except Exception:
                pass
        elif key[0] in ['left']:
            dot_i = dot_i - eyecal.cols
        elif key[0] in ['right']:
            dot_i = dot_i + eyecal.cols
        elif key[0] in ['up', 'down']:
            mvdir = -1 if key[0] == 'up' else 1
            cur_col = int(dot_i/eyecal.cols)*(eyecal.cols)
            into_row = (dot_i%eyecal.rows + mvdir)%eyecal.rows
            dot_i =  cur_col + into_row
        else:
            dot_i = dot_i + 1

        # make sure we're in bounds
        dot_i = dot_i % len(eyecal.dot_pos)

    win.close()
