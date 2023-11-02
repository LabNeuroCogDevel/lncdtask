"""
utility functions for using screen
"""
from psychopy import core, visual, event

# this causes some artifacts!?
def take_screenshot(win, name, saveto='screenshots'):
    os.makedirs(saveto, exist_ok=True)
    win.getMovieFrame()   # Defaults to front buffer, I.e. what's on screen now
    win.saveMovieFrames(saveto + '/' + name + '.png')


def wait_until(stoptime, maxwait=30):
    """
    just like core.wait, but instead of waiting a duration
    we wait until a stoptime.
    optional maxwait will throw an error if we are wating too long
    so we dont get stuck. defaults to 30 seconds
    """
    if stoptime - core.getTime() > maxwait:
        raise ValueError("request to wait until stoptime is more than " +
                         "30 seconds, secify maxwait to avoid this error")
    # will hog cpu -- no pyglet.media.dispatch_events here
    while core.getTime() < stoptime:
        continue


def center_textbox(textbox):
    """
    center textbox in 'norm' units
    """
    tw = textbox.boundingBox[0]
    ww = float(textbox.win.size[0])
    textbox.pos = (-tw/ww, 0)


def wait_for_scanner(textbox, trigger=['equal'], msg='Waiting for scanner (pulse trigger)'):
    """
    wait for scanner trigger press
    start any auxilary things (eyetracking for mri, ttl for eeg)
    return time of keypush
    """
    textbox.setText(msg)
    center_textbox(textbox)
    textbox.draw()
    textbox.win.flip()
    event.waitKeys(keyList=trigger)
    starttime = core.getTime()
    return(starttime)


def msg_screen(textbox, msg='no message given', pos=(0, 0), minwait=.4, flip=True):
    """quickly display a message. wait half a second. and avdance on any keypress"""
    textbox.pos = pos
    textbox.text = msg
    textbox.draw()
    if not flip:
        return
    textbox.win.flip()
    core.wait(minwait)
    return event.waitKeys()


def create_window(fullscr, screen=0, bg=(-1,-1,-1)):
    """ create window either fullscreen or 800,600
    hide mouse cursor and make active
    """
    # setup screen
    if fullscr:
        win = visual.Window(fullscr=fullscr, screen=screen)
    else:
        win = visual.Window([800, 600])

    win.winHandle.activate()  # make sure the display window has focus
    win.mouseVisible = False  # and that we don't see the mouse

    # -- change color to black --
    win.color = bg
    # flip twice to get the color
    win.flip()
    win.flip()

    return(win)

# we could  img.units='deg', but that might complicate testing on diff screens
def ratio(screen, image, scale):
    """ screen to image ratio
    Q: screen width=100, image w = 5; Want img on 50% of the screen
    A: 10x
    >>> ratio(100, 5, .5)
    10.0
    """
    return(float(screen) * scale/float(image))


def replace_img(img, filename, horz, imgpercent=.04, defsize=(225, 255), vertOffset=0):
    '''
    replace_img adjust the image and position of a psychopy.visual.ImageStim
    '''
    # set image, get props
    if filename is not None:
        img.image = filename
        (iw, ih) = img._origSize
    else:
        (iw, ih) = defsize

    (sw, sh) = img.win.size
    img.units = 'pix'

    # resize img
    scalew = ratio(sw, iw, imgpercent)
    # scaleh= ratio(sh,ih,imgpercent)
    # scale evenly in relation to x-axis
    # img.size=(scalew*iw,scalew*sw/sh*ih) # if units were 'norm'
    img.size = (scalew*iw, scalew*ih)  # square pixels
    # img._requestedSize => (80,80) if imgprecent=.1*sw=800

    # # position
    winmax = sw/float(2)
    # horz=-1 => -400 for 800 wide screen
    horzpos = horz*winmax
    halfimgsize = scalew*iw/2.0
    # are we partially off the screen? max edges perfect
    if horzpos - halfimgsize < -winmax:
        horzpos = halfimgsize - winmax
    elif horzpos + halfimgsize > winmax:
        horzpos = winmax - halfimgsize

    # where to show the image
    vertpos = (vertOffset)*sh/2.0

    # set
    img.pos = (horzpos, vertpos)

    # # draw if we are not None
    if filename is not None:
        img.draw()

    return(img.pos)


