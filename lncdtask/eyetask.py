"""
Task using eye tracking and/or button responses
"""
class lncdTask:
    # initialize all the compoents we need
    def __init__(self,
                 win,
                 accept_keys={'known':        '1',
                              'maybeknown':   '2',
                              'maybeunknown': '9',
                              'unknown':      '0',
                              'Left':         '1',
                              'NearLeft':     '2',
                              'NearRight':    '9',
                              'Right':        '9',
                              'oops':         '5'},
                 vertOffset=0,
                 ET_type=None,
                 usePP=False,
                 fullscreen=True,
                 pp_address=0xDFF8,
                 zeroTTL=True,
                 recVideo=False,
                 # for arrington eye tracking with VPx32
                 vpxDll='C:\\Users\\Luna\\Desktop\\VPx32\\Interfaces\\VPx32-Client\\VPX_InterApp_32.dll'):

        # compensate for mdiway pause
        self.addTime = 0
        # were we given a window?
        # make our own if not
        if win is None:
            win = create_window(fullscreen)

        # settings for eyetracking and parallel port ttl (eeg)
        # thisscript=os.path.abspath(os.path.dirname(__file__))
        # self.vpxDll = os.path.join(thisscript,"VPX_InterApp.dll")
        #self.vpxDll = 'C:\\Users\\Public\\Desktop\\tasks\\EyeTracking_ViewPointConnect\\VPX_InterApp.dll'
        self.vpxDll = vpxDll 
        #self.vpxDll = 'C:\Users\Luna\Desktop\VPx32\Interfaces\Programing\SDK\\VPX_InterApp_32.dll'
        self.usePP = usePP
        # ## eyetracking -- updated later if to be used
        self.vpx = None
        self.eyelink = None
        self.ET_type = ET_type

        # # parallel port triggers or eyetracking
        if self.ET_type == "arrington":
            self.init_vpx()
        elif self.ET_type == "iohub_eyelink":
            # 20210329 using psychopy documentation instead of pylink
            # for ringrewrads. can maybe use pylink instead
            pass
            
        elif self.ET_type == "pylink":
            from pylink_help import eyelink
            self.eyelink = eyelink(win.size)

        if self.usePP:
            self.pp_address = pp_address
            self.zeroTTL    = zeroTTL
            self.init_PP()
            # settings for parallel port
            # see also 0x03BC, LPT2 0x0278 or 0x0378, LTP 0x0278
            #self.pp_address = 0x0378
            #self.pp_address = 0x0278
            #self.pp_address = 0xDFF8 # EEG
            # self.pp_address = 0x0378 # ASL practice

        # want to mute windows computer
        # so monitor switching doesn't beep

        self.winvolume = winmute.winmute()

        self.verbose = True

        # how far off the horizonal do we display cross and images?
        self.vertOffset = vertOffset

        # do we tell arrington to record eye video?
        self.recVideo = recVideo
        self.runEyeName = datetime.datetime.strftime(
                            datetime.datetime.now(),
                            "unnamed_%Y%m%d_%H%M%S.avi")

        # images relative to screen size
        self.imgratsize = .15

        # window and keys
        self.win = win
        self.accept_keys = accept_keys

        # allocate screen parts
        self.img = visual.ImageStim(win, name="imgdot", interpolate=True)
        self.crcl = visual.Circle(win, radius=10, lineColor=None,
                                  fillColor='yellow', name="circledot")
        #  ,AutoDraw=False)
        self.crcl.units = 'pix'

        # instruction eyes image
        # for draw_instruction_eyes(self,
        self.eyeimg = visual.ImageStim(win, name="eye_img_instructions",
                                       interpolate=True)
        self.eyeimg.image = 'img/instruction/eyes_center.png'
        self.eyeimg.pos = (0, -.9)

        # instructions overview
        self.imgoverview = visual.ImageStim(win, name="eye_img_overview",
                                            interpolate=True)
        self.imgoverview.image = 'img/instruction/overview.png'

        self.timer = core.Clock()

        # could have just one and change the color
        self.iti_fix = visual.TextStim(win, text='+', name='iti_fixation',
                                       color='white', bold=True)
        self.isi_fix = visual.TextStim(win, text='+', name='isi_fixation',
                                       color='yellow', bold=True)
        self.cue_fix = visual.TextStim(win, text='+', name='cue_fixation',
                                       color='royalblue', bold=True)
        # double size
        self.iti_fix.size = 2
        self.isi_fix.size = 2
        self.cue_fix.size = 2
        self.textbox = visual.TextStim(win, text='**', name='generic_textbox',
                                       alignHoriz='left', color='white',
                                       wrapWidth=2)
        # if we are mr and want horzinal line to have vertical offset,
        #  need to increase position
        # .5 is center
        self.iti_fix.pos[1] = self.vertOffset
        self.isi_fix.pos[1] = self.vertOffset
        self.cue_fix.pos[1] = self.vertOffset

        # # for quiz
        self.text_KU = visual.TextStim(win,
                                       text='seen:\nyes, maybe yes | maybe no, no',
                                       name='KnownUnknown',
                                       alignHoriz='center',
                                       color='white',
                                       height=.07,
                                       wrapWidth=2,
                                       pos=(-0.2, -.75))
        # self.text_KU.units = 'pixels'
        # self.text_KU.size = 8
        self.text_LR = visual.TextStim(win,
                                       text='side:\nfar left, mid left | mid right, far right',
                                       name='LeftRight',
                                       alignHoriz='center',
                                       color='white',
                                       height=0.07,
                                       wrapWidth=2,
                                       pos=(-0.2, -.75))
        # self.text_LR.units = 'pixels'
        # self.text_LR.size = 8

        # for recall only:
        # tuplet of keys and text: like ('1', 'text after pushed')
        self.dir_key_text = [
                             (self.accept_keys['Left'],   'left'),
                             (self.accept_keys['NearLeft'],  '   left'),
                             (self.accept_keys['NearRight'],  'right    '),
                             (self.accept_keys['Right'],  '        right'),
                             (self.accept_keys['oops'],   '    oops     ')
                             ]
        self.known_key_text = [
                               (self.accept_keys['known'], 'known'),
                               (self.accept_keys['maybeknown'], 'known'),
                               (self.accept_keys['maybeunknown'], 'unknown'),
                               (self.accept_keys['unknown'], 'unknown')
                               ]

        # show side
        self.recall_sides = [visual.Circle(win, radius=10, lineColor=None,
                                           fillColor='yellow',
                                           units='pix',
                                           name="recall_dot%d" % x)
                             for x in range(4)]
        self.recall_txt = [visual.TextStim(win, text=str(x),
                                           color='black',
                                           units='pix',
                                           name='recall_%d' % x)
                           for x in range(4)]

    def wait_for_scanner(self, trigger, msg='Waiting for scanner (pulse trigger)'):
        """
        wait for scanner trigger press
        start any auxilary things (eyetracking for mri, ttl for eeg)
        return time of keypush
        """
        self.textbox.setText(msg % trigger)
        center_textbox(self.textbox)
        self.textbox.draw()
        self.win.flip()
        event.waitKeys(keyList=trigger)
        starttime = core.getTime()
        self.start_aux()  # eyetracking/parallel port
        self.run_iti()
        return(starttime)

    def run_iti(self, iti=0):
        """
        simple iti. flush logs
        globals:
          iti_fix visual.TextStim
        """
        self.iti_fix.draw()
        self.win.callOnFlip(self.log_and_code, 'iti', None, None)
        showtime = self.win.flip()
        logging.flush()
        if(iti > 0):
            core.wait(iti)
        return(showtime)

    def vgs_show(self, imgon, posstr, imgfile=None, imgtype=None, logh=None,
                 takeshots=False, trialno=None):
        """
        run the vgs event: show an image with a dot over it in some postiion
        """

        # set horz postion from side (left,right). center if unknown
        horz = {'Right': 1, 'Left': -1, 'NearLeft': -.5, 'NearRight': .5}.\
            get(posstr, 0)

        imgpos = replace_img(self.img, imgfile, horz, self.imgratsize,
                             vertOffset=self.vertOffset)

        self.crcl.pos = imgpos
        self.crcl.draw()
        self.win.callOnFlip(self.log_and_code, 'img', posstr, imgtype,
                            logh, takeshots, num=2, trialno=trialno)
        wait_until(imgon)
        showtime = self.win.flip()
        return(showtime)

    def sacc_trial(self, t, starttime=0, takeshots=None, logh=None):
        """
        saccade trial
         globals:
          win, cue_fix, isi_fix
        """
        if(starttime == 0):
            starttime = core.getTime()

        cueon = starttime + t['cue']
        imgon = starttime + t['vgs']
        ision = starttime + t['dly']
        mgson = starttime + t['mgs']

        # if takeshots: take_screenshot(self.win,takeshots+'_00_start')

        # give header for output if this is the first trial
        if t.thisN == 0:
            print("")
            print("ideal\tcur\tlaunch\tpos\ttype\tdly\tdiff (remaning iti)\taddTime")

        print("%.02f\t%.02f\t%.02f\t%s\t%s\t%.02f\t%.02f\t%.02f" %
              (t['cue'],
               core.getTime(),
               starttime + t['cue'],
               t['side'],
               t['imgtype'],
               t['mgs'] - t['dly'],
               starttime + t['cue'] - core.getTime(),
               self.addTime
               ))

        # get ready red target
        self.cue_fix.draw()
        self.win.callOnFlip(self.log_and_code, 'cue', t['side'], t['imgtype'],
                            logh, takeshots, 1, trialno=t['trial'])

        wait_until(cueon)
        cueflipt = self.win.flip()

        # show an image if we have one to show
        vgsflipt = self.vgs_show(imgon, t['side'], t['imgfile'], t['imgtype'],
                                 logh, takeshots, trialno=t['trial'])

        # back to fix
        self.isi_fix.draw()
        self.win.callOnFlip(self.log_and_code, 'isi', t['side'], t['imgtype'],
                            logh, takeshots, 3, trialno=t['trial'])

        wait_until(ision)
        isiflipt = self.win.flip()

        # memory guided (recall)
        # -- empty screen nothing to draw
        self.win.callOnFlip(self.log_and_code, 'mgs', t['side'], t['imgtype'],
                            logh, takeshots, 4, t['trial'])
        wait_until(mgson)
        mgsflipt = self.win.flip()

        # ----
        # N.B. after this filp we still need to wait MGS wait time
        # ---

        # send back all the flip times
        return({'cue': cueflipt, 'vgs': vgsflipt, 'dly': isiflipt,
                'mgs': mgsflipt})

        # coded with wait instead of wait_until:
        # # get ready
        # cue_fix.draw(); win.flip(); core.wait(0.5)
        # # visual guided
        # replace_img(img,imgfile,horz,.05); win.flip(); core.wait(.5)
        # # back to fix
        # isi_fix.draw(); win.flip(); core.wait(0.5)
        # # memory guided
        # win.flip(); core.wait(.5)

    def key_feedback(self, keys_text_tupple, feedback, timer, maxtime=1.5):
        """
        record button response  and reaction time
        display equally long for regardless of RT
        provide feedback after push
        globals:
          win
        """
        validkeys = [x[0] for x in keys_text_tupple]
        # validkeys = ['1','2','3','4']
        origtext = feedback.text

        # get list of tuple (keypush,rt)
        t = event.waitKeys(keyList=validkeys, maxWait=maxtime,
                           timeStamped=timer)
        # we're only going to look at single button pushes
        # already only accepting 2 or 3 keys
        if(t is not None and len(t) == 1):
            (keypressed, rt) = t[0]
            for (k, txt) in keys_text_tupple:
                if(keypressed == k):  # TODO, allow multple keys?
                    feedback.text = txt
                    break

            feedback.draw()
            self.win.flip()
            feedback.text = origtext
        # no response or too many responses means no keypress and no rt
        else:
            t = [(None, None)]
        # wait to finish
        while(maxtime != numpy.Inf and timer.getTime() < maxtime):
            pass
        # give key and rt
        return(t[0])

    def recall_instructions(self):
        """
        recall task instructions
        """

        self.textbox.pos = (-.9, 0)
        self.textbox.text = \
           'STEPS:\n\n' + \
           '1. push %s if you already saw the image.\n' % self.accept_keys['known'] + \
           '   push %s if you saw the image, but are uncertian\n' % self.accept_keys['maybeknown'] + \
           '   push %s if the image is new, but are uncertian\n' % self.accept_keys['maybeunknown'] + \
           '   push %s if the image is new\n\n' % self.accept_keys['unknown'] + \
           '2. If you have seen the image:\n' + \
           '   push %s if you saw it on the far left\n' % self.accept_keys['Left'] + \
           '   push %s if you saw it on the near left\n' % self.accept_keys['NearLeft'] + \
           '   push %s if you saw it on the near right\n' % self.accept_keys['NearRight'] + \
           '   push %s if you saw it on the far right\n' % self.accept_keys['Right'] 
           
        # '   push %s if you did not actually see it\n\n' % self.accept_keys['oops'] + \
        self.textbox.draw()
        self.instruction_flip()

    def init_recall_side(self):
        pos = [-1, -.5, .5, 1]
        keys = [self.accept_keys[x]
                for x in ['Left', 'NearLeft', 'NearRight', 'Right']]
        for i in range(len(pos)):
            self.recall_sides[i].pos = \
                    replace_img(self.img, None, pos[i], self.imgratsize)
            self.recall_txt[i].pos = self.recall_sides[i].pos
            self.recall_txt[i].text = str(keys[i])

    def recall_trial(self, imgfile, rspmax=numpy.Inf):
        """
        run a recall trial.
        globals:
         img, text_KU, text_LR, dir_key_text, known_key_text
        """
        # draw the image and the text (keep image on across flips)
        replace_img(self.img, imgfile, 0, .25)
        self.img.setAutoDraw(True)
        self.text_KU.draw()
        self.win.flip()

        self.timer.reset()
        # do we know this image?
        (knowkey, knowrt) = self.key_feedback(self.known_key_text,
                                              self.text_KU, self.timer,
                                              rspmax)

        # end early if we have not seen this before
        knownkeys = [self.accept_keys['maybeknown'], self.accept_keys['known']]
        if(knowkey not in knownkeys):
            self.img.setAutoDraw(False)
            # TODO: maybe wait so we are not incentivising unknown
            return((knowkey, None), (knowrt, None))

        # we think we remember this image, do we remember where it was
        self.text_LR.draw()
        for i in range(4):
            self.recall_sides[i].draw()
            self.recall_txt[i].draw()
        self.win.flip()

        self.timer.reset()
        (dirkey, dirrt) = self.key_feedback(self.dir_key_text,
                                            self.text_LR, self.timer,
                                            rspmax)

        self.img.setAutoDraw(False)
        return((knowkey, dirkey), (knowrt, dirrt))

    def instruction_flip(self):
        """
        quick def to flip, stall half a second, and wait for any key
        """
        self.win.flip()
        core.wait(.4)
        pressevent = event.waitKeys(keyList=['space', 'q', 'c'])
        return(pressevent)

    def instruction_flip_or_quit(self):
        """
        quick def to flip, stall half a second, and wait for any key
        """
        pressevent = self.instruction_flip()
        if('q' in pressevent):
            self.win.close()
            sys.exit()

    def draw_instruction_eyes(self, where='center'):
        self.eyeimg.image = 'img/instruction/eyes_%s.png' % where
        self.eyeimg.draw()

    def sacc_instructions(self):
        """
        saccade task instructions
        """
        self.textbox.pos = (-.5, 0)
        self.textbox.text = 'Memory Guided Saccade Task\n\n' + \
                            'Look at and remember a dot.\n' + \
                            'Wait.\n' + \
                            'Look back to where it was.\n\n' + \
                            'Ready for a walk through?'
        self.textbox.draw()
        self.instruction_flip_or_quit()

        self.textbox.pos = (-.9, .9)
        self.textbox.text = 'Prep: get ready to look at a dot'
        self.textbox.draw()
        self.cue_fix.draw()
        self.draw_instruction_eyes('center')
        self.instruction_flip_or_quit()

        self.textbox.text = 'Look: look at the dot\n' + \
                            'remember that spot until it disappears'
        imgpos = replace_img(self.img, 'img/example.png', 1, self.imgratsize,
                             vertOffset=self.vertOffset)
        self.textbox.draw()
        self.crcl.pos = imgpos
        self.crcl.draw()
        self.draw_instruction_eyes('right')
        self.instruction_flip_or_quit()

        self.textbox.text = 'Wait: go back to center and focus on the yellow cross\nuntil it disappears'
        self.textbox.draw()
        self.isi_fix.draw()
        self.draw_instruction_eyes('center')
        self.instruction_flip_or_quit()

        self.textbox.text = 'Recall: look to where dot was and focus there\nuntil a new cross appears'
        self.textbox.draw()
        self.draw_instruction_eyes('right')
        self.instruction_flip_or_quit()

        self.textbox.text = 'Relax: wait for the blue cross to signal a new round'
        self.textbox.draw()
        self.iti_fix.draw()
        self.draw_instruction_eyes('center')
        self.instruction_flip_or_quit()

        self.textbox.pos = (-.9, 0)
        self.textbox.text = \
            '1. Prep: Look at the blue cross.' + \
            ' A dot is about to appear.\n\n' + \
            '2. Look: Look at the dot inside the dot and remember that spot' + \
            ' until it goes away.\n\n' + \
            '3. Wait: Look at the yellow cross in the center.\n\n' + \
            '4. Recall: When the yellow cross goes away. ' + \
            'Look back to where you saw the dot until ... \n\n' + \
            '5. Relax: Look at the white cross in the center when it comes back.\n\n' +\
            'NOTE: you do not need to remember the images for this task ' +\
            'but you may be asked about them later'
        # 'Color Hints: \n' + \
        # 'blue = get ready\n' + \
        # 'yellow = remember\n' + \
        # 'white = relax'

        self.textbox.draw()
        self.instruction_flip_or_quit()
        self.textbox.pos = (0, 0)

        self.imgoverview.draw()
        self.instruction_flip_or_quit()

    def run_end(self, run=1, nruns=1):
        """
        show end of run screen
        send stop codes for parallel port
        close eyetracking file
        20180509: add fixation cross to center for slip correct
        20180907: add option to exit earily
        """
        self.stop_aux()  # end ttl, close eye file
        self.textbox.pos = (-.2, .5)
        runstr = ""
        if nruns > 1:
            runstr = '%d/%d!' % (run, nruns)
        self.textbox.text = 'Finished ' + runstr
        self.iti_fix.draw()
        self.textbox.draw()

        self.textbox.pos = (-.9, -.9)
        self.textbox.text = "[space continue, q quit, c calibrate]"
        self.textbox.draw()

        pressevent = self.instruction_flip()
        if('q' in pressevent):
            return("done")
        elif('c' in pressevent):
            c = showCal(self.win)
            c.calibrate()
            self.textbox.text = 'Ready for the next run?'
            self.textbox.pos = (-.5, 0)
            self.textbox.draw()
            pressevent = self.instruction_flip()

        return("next")


def gen_run_info(nruns, datadir, imgset, task='mri'):
    """
    load or make and save
    timing for all blocks at once
    - useful to guaranty unique timing files and images
    - used images saved for recall
    task is mri or eeg
    """
    # where do we save this file?
    if datadir is not None:
        runs_info_file = os.path.join(datadir, 'runs_info.pkl')
        # if we have it, just return it
        if os.path.exists(runs_info_file):
            print('reusing timing/image selection from %s' % runs_info_file)
            with open(runs_info_file, 'rU') as f:
                return(pickle.load(f))

    # images
    path_dict = {'Indoor':  ['img/' + imgset + '/inside/*png'],
                 'Outdoor': ['img/' + imgset + '/outside_man/*png',
                             'img/' + imgset + '/outside_nat/*png',
                             ]}
    imagedf = gen_imagedf(path_dict)

    # get enough timing files for all runs
    alltimingdirs = glob.glob(os.path.join('stims', task, '[0-9]*[0-9]'))
    print("loading task timing for %s: %s" % (task, alltimingdirs))

    thistimings = shuf_for_ntrials(alltimingdirs, nruns)
    # allocate array
    run_timing = []
    for runi in range(nruns):
        # find all timing files in this directory
        timingglob = os.path.join(thistimings[runi], '*')
        trialdf = parse_onsets(timingglob)
        # add images to trialdf, update imagedf with which are used
        (imagedf, trialdf) = gen_stimlist_df(imagedf, trialdf)
        #print("nused = %d for %d" % (imagedf[imagedf.used].shape[0], trialdf.shape[0]))
        # check
        if(any(numpy.diff(trialdf.vgs) < 0)):
            raise Exception('times are not monotonically increasing! bad timing!')
        run_timing.append(trialdf)

    # save to unified data structure
    subj_runs_info = {'imagedf': imagedf, 'run_timing': run_timing}

    # save what we have
    if datadir is not None:
        with open(runs_info_file, 'wb') as f:
            pickle.dump(subj_runs_info, f)

    return(subj_runs_info)


def imagedf_to_novel(imdf):
    """
    take an imagedf with imgtype,subtype and used column
    return shuffled df with just the unused images matched on number of used

    >>> ();run_data=gen_run_info(3, None, 'A', task='mri')  # doctest:+ELLIPSIS
    (...
    >>> ();novel = imagedf_to_novel(run_data['imagedf']) # doctest:+ELLIPSIS
    (...
    >>> not novel.used.any()    # no known images
    True
    >>> novel.index[1] != 1 # is shuffled
    True
    >>> novel.columns.sort_values().tolist()
    ['imgfile', 'imgtype', 'pos', 'subtype', 'used']

    """
    nused = imdf[imdf.used].\
        groupby(['imgtype', 'subtype']).\
        aggregate({'used': lambda x: x.shape[0]})
    nused['aval'] = imdf[~imdf.used].\
        groupby(['imgtype', 'subtype'])['used'].\
        apply(lambda x: x.shape[0])
    print(nused)
    if(any(nused.used > nused.aval)):
        print("WARNING: will see more repeats than novel images!")

    # use as many as we can
    # might not be balanced!
    novelimg = pandas.concat([
        imdf[(imdf.used == False) &
             (imdf.imgtype == r[0][0]) &
             (imdf.subtype == r[0][1])].
        sample(min(r[1].aval, r[1].used))
        for r in nused.iterrows()])
    # add empty position
    novelimg['pos'] = float("nan")
    return(novelimg)


def dropUnseen(seendf, imdf, drop=True):
    """
    Remove unseen trials (when excluding trials from recall)

    >>> ();run_data=gen_run_info(3, None, 'A', task='mri')  # doctest:+ELLIPSIS
    (...
    >>> # just the last trial, remove 2 * 16
    >>> seendf = pandas.concat(run_data['run_timing'][2:3])
    >>> imdf = run_data['imagedf']
    >>> ddf = dropUnseen(seendf, imdf) # doctest:+ELLIPSIS
    have ... 16 in run... with 32 to remove
    >>> ddf.groupby("used").agg('count')['imgfile'] # doctest:+ELLIPSIS
    used
    False    ...
    True     16
    Name: imgfile, dtype: int64
    >>> ddf.columns.sort_values().tolist()
    ['imgfile', 'imgtype', 'subtype', 'used']
    """

    # what did we say we saw but didn't actually see
    alldf = imdf.merge(seendf.drop(axis=1, labels='imgtype'),
                       on='imgfile', how='left')
    fortest = alldf.\
        query('(used and trial==trial) or not used').\
        filter(imdf.columns)

    # drop, dont use --  incase this is resuming
    msgstr = "have %(total)d imgs in set: " + \
             "%(task)d in task, %(actual)d in run(s) to test, " + \
             "with %(remove)d to remove"
    print(msgstr % {'total': len(alldf),
                    'task': len(alldf.query('used and imgfile == imgfile')),
                    'actual': len(fortest.query('used')),
                    'remove': len(alldf) - len(fortest)})
    if(drop):
        return(fortest)
    else:
        alldf.loc[alldf.used & (alldf.trial != alldf.trial), 'used'] = False
        return(alldf.filter(imdf.columns))


def recallFromPickle(pckl, lastrunidx=3, firstrunidx=0):
    """
    use a pckl file to define a trial list for recall
    """
    # load run info
    with open(pckl, 'rU') as p:
        print(pckl)
        run_data = pickle.load(p)

    # select what we've seen
    # put all used runs together
    seendf = pandas.concat(run_data['run_timing'][firstrunidx:lastrunidx])
    # --- pick some novel stims --
    imdf = run_data['imagedf']
    # but remove images we haven't seen (but should have)
    if(firstrunidx > 0 or lastrunidx < len(run_data['run_timing'])):
        print("using only runs %d to %d" % (firstrunidx+1, lastrunidx))
        imdf = dropUnseen(seendf, imdf)

    # from that, make a novelimg dataset
    # with columns that match
    novelimg = imagedf_to_novel(imdf)

    # get just the images and their side
    seendf = seendf[seendf.imgtype != "None"][['side', 'imgfile', 'imgtype']]
    # convert side to position (-1 '*Left', 1 if '*Right')
    seendf['pos'] = [
            ('Left' == x) * -1 + ('Right' == x) * 1 +
            ('NearLeft' == x) * -.5 + ('NearRight' == x) * .5
            for x in seendf['side']]

    # combine them
    trialdf = pandas.concat([seendf[['imgfile', 'pos', 'imgtype']],
                            novelimg[['imgfile', 'pos', 'imgtype']]]).\
        sample(frac=1, replace=False)

    # set(trialdf.imgfile[pandas.notnull(df.pos)]) == \
    # set(seendf.imgfile[pandas.notnull(seendf.imgfile)])
    return(trialdf)
