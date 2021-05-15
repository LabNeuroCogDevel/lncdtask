import glob
import os
def read_timing(onsetprefix):
    """
    read onsets files given a pattern. will append *1D to pattern
    #everything not in pattern is stripped from returned onset dict
    only file name is used
    use with parse_onsets()
       # input looks like
       with open('stims/example_0001_01_cue.1D','w') as f:
            f.write(" ".join(["%.02f:dur" % x
                      for x in numpy.cumsum(.5+numpy.repeat(2,10) ) ]));
       stims/4060499668621037816/
         dly.1D
         mgs.1D
         vgs_Left_Indoor.1D
         vgs_Left_None.1D
         vgs_Left_Outdoor.1D
         vgs_Right_Indoor.1D
         vgs_Right_None.1D
         vgs_Right_Outdoor.1D
    """
    onsetdict = {}
    onsetfiles = glob.glob(onsetprefix + '*1D')
    if(len(onsetfiles) <= 0):
        msg = 'no onset files in %s' % onsetprefix
        raise Exception(msg)
    for onset1D in onsetfiles:
        # key name will be file name but
        # remove the last 3 chars (.1D) and the glob part
        # onsettype = onset1D[:-3].replace(onsetprefix, '')
        onsettype = os.path.basename(onset1D)[:-3]
        with open(onset1D) as f:
            onsetdict[onsettype] = [float(x.split(':')[0])
                                    for x in f.read().split()]
    return(onsetdict)

