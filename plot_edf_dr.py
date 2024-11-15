#!/usr/bin/env python3
from eyelinkio import read_edf
import numpy as np
import re
import logging
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def overlapping_data(idx, data, on, off, datatype):
    overlap = []
    if not data:
        return (idx,overlap)
    while idx < len(data) and (data[idx]['stime'] < on):
        logging.debug("forward %s idx: onset %f < %f blink start",datatype, on, data[idx]['stime'])
        idx += 1
    while idx < len(data) and (data[idx]['etime'] < off):
        logging.debug("include idx: onset %f+1 < %f blink end", off, data[idx]['etime'])
        overlap.append(data[idx])
        idx += 1

    if idx >= len(data):
        idx = len(data)-1

    logging.debug("%s hold: onset %f before %f next %s start",datatype, on, data[idx]['stime'], datatype)
    return (idx, overlap)

def extract_target(fname, msg_regex):
    edf_file = read_edf(fname)
    reg = re.compile(msg_regex)
    onsets = [(onset,msg.decode())
              for (onset,msg) in edf_file['discrete']['messages']
              if reg.search(msg.decode())]

    hdr = dict(screen_x=None,screen_y=None)
    for t,msg in edf_file['discrete']['messages']:
         gaz = re.search('GAZE_COORDS [0-9.]+ [0-9.]+ ([0-9.]+) ([0-9.]+)',msg.decode())
         if gaz:
             hdr['screen_x'],hdr['screen_y'] = gaz.groups(1)
             break


    # only look at first eye tracked
    first_eye_seen =edf_file['discrete']['blinks'][0]['eye']
    blinks = [x for x in edf_file['discrete']['blinks'] if x[0] == first_eye_seen]
    saccs = [x for x in edf_file['discrete']['saccades'] if x[0] == first_eye_seen]
    times = edf_file['times']
    samp = times[1]-times[0]
    t_dur = 1 # second
    t_data = [{'blinks':[], 'saccades':[],
               'onset': x[0], 'msg': x[1],
               'samples':[],
               'times':[]}
              for x in onsets]

    idx = {'blink':0, 'sac': 0}
    t_adjust = 0
    for (i, (t, msg)) in enumerate(onsets):
        (idx['blinks'], overlap) = overlapping_data(idx['blink'], blinks, t, t+t_dur, 'blinks')
        t_data[i]['blinks'] = overlap

        (idx['sac'], overlap) = overlapping_data(idx['sac'], saccs, t, t+t_dur, 'saccs')
        t_data[i]['saccades'] = overlap

        t_s = int(t//samp)
        if abs(tdiff := t - times[t_s] ) > samp:
            t_adjust = int(tdiff//samp)
            logging.warning("stime adjusted %d samples (%f=%f-%f) on trial %d",
                            t_adjust, tdiff,times[t_s],t, i)
            t_s = int(t//samp) + t_adjust

        t_e = int((t+t_dur)//samp) + t_adjust
        if abs(tdiff := t + t_dur -times[t_e]) > samp:
            logging.warning("etime adjusted %d samples (%f) on %d", t_adjust, tdiff, i)
            t_adjust = int(tdiff*samp)
            t_e = int((t+t_dur)//samp) + t_adjust

        assert abs(times[t_s] - t) <= samp
        assert abs(times[t_e] - t - t_dur) <= samp
        t_data[i]['samples'] = edf_file['samples'][:,t_s:t_e]
        t_data[i]['times'] = edf_file['times'][t_s:t_e]

    return (t_data, hdr)


   # https://www.sr-research.com/support/thread-7675.html
   # saccade:  eye start_t end_t dur start_x starty_y end_x end_y amp peak_vel
   #  edf_file['discrete']['saccades'][0]
   # np.void((1.0, 0.236, 0.258, 792.0999755859375, 678.7999877929688, 946.2000122070312, 726.4000244140625, 185.89999389648438), dtype=[('eye', '<f8'), ('stime', '<f8'), ('etime', '<f8'), ('sxp', '<f8'), ('syp', '<f8'), ('exp', '<f8'), ('eyp', '<f8'), ('pv', '<f8')])
   #
   # blink:     eye start_t end_t [dur]
   # edf_file['discrete']['blinks'][0]
   # np.void((0.0, 28.36, 28.446), dtype=[('eye', '<f8'), ('stime', '<f8'), ('etime', '<f8')])

def plot_trials(t_data, max_x=1920):
    fig, axes = plt.subplots(6,6)
    plt.tight_layout()
    fig.suptitle('Dot X traces')
    for a in fig.axes:
        a.axis('off')

    for i, d in enumerate(t_data):
        ax= axes[i//6,i%6]
        #ax.set_title("%d"%(i+1))
        (tnum, event, rewtype, dotpos) = d['msg'].split("_")
        dotpos = float(dotpos)
        ax.set_ylim([0,max_x])
        time = d['times']
        x_eye = d['samples'][1,:]
        # use annote for easier arrow. if arrow and text together, arrow end is centered on text
        ax.text(time[0], max_x//2,f"{tnum}: {rewtype} {dotpos:.1f}", fontsize=8, zorder=-1)
        ax.annotate(f"",
                    xy=(time[0], max_x if dotpos<0 else 0),
                    xytext=(time[0], max_x//2),
                    arrowprops=dict(arrowstyle='->'))

        ax.hlines(max_x//2,min(time), max(time), linewidth=0.5, colors="green", linestyles='dashed')
        ax.plot(time, x_eye)
        for sac in d['saccades']:
            sac_rec = Rectangle((sac['stime'],sac['exp']-50),
                                sac['etime']-sac['stime'],100,
                                fill=True, facecolor='orange')
            ax.add_patch(sac_rec)
        for blink in d['blinks']:
            blink_rec = Rectangle((blink['stime'],0),
                                blink['etime']-blink['stime'],100,
                                fill=True, facecolor='red')
            ax.add_patch(blink_rec)

    return fig



if __name__ == "__main__":
    import sys
    import os
    (fname, patt) = sys.argv[1:]
    t_data, hdr = extract_target(fname,patt)
    fig = plot_trials(t_data, float(hdr['screen_x']))
    title =os.path.basename(fname)
    if ld8match := re.search("(\\d{5}_\\d{8}).*run.(\\d+)", fname):
        title = f"{ld8match.group(1)} {ld8match.group(2)} {title}"
    fig.suptitle(title)
    big_size = [xy/plt.rcParams['figure.dpi'] for xy in (1175, 704)]
    fig.set_size_inches(*big_size)
    plt.show()
