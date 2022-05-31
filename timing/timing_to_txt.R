#!/usr/bin/env Rscript

#
# 20220531 WF - read make_random_timing.py output and shape like ../dollar_reward_events.txt
# as read by [[file:~/src/work/lncdtask/lncdtask/dollarreward.py::onset_df =]]
# and used by events like [[file:~/src/work/lncdtask/lncdtask/dollarreward.py::self.add_event_type]] 
# and only cares about onset, ring_type, and position (translated from initial input)
#

library(dplyr)
library(tidyr)

afni_to_task <- function(fname="out/510s/v1_60_26546/events.txt", total_runtime=510) {
    # parse event.csv from make_random_timing.py and add balenced position
    d <- read.table(fname,skip=3)
    names(d) <- c("n","event","onset","dur","rest")
    d <- d %>% mutate(event=gsub("\\(|\\)","",event),
                rest=as.numeric(rest),
                trial = 1 + cumsum(lag(rest, default=0)!=0)) %>% select(-n)

    d_py <- d %>%
        split(d$trial) %>%
        lapply(function(d){
          iti<-last(d$rest)
          #              event      onset          dur rest trial
          new_row <- c("iti_iti",last(d$onset)+iti,iti, 0, last(d$trial))
          rbind(d, new_row) %>%
            mutate(trial_type=first(event))
        }) %>%
        bind_rows %>%
        select(-rest) %>% 
        separate(event,c("ring_type","event_name", "catch"),remove=FALSE)

    row.names(d_py)<-NULL


    #  only care about position if not a catch trial. 
    # have 4 positions, but only 2 sides.
    # first divy up left and right. then divy that into position.
    # this hopefully minimizes any left/right asymetry
    trial_type <- d_py %>% group_by(trial) %>% filter(row_number()==1, is.na(catch)) %>%
        select(trial,ring_type) %>%
        mutate(side=NA, position=NA)
    mk_reps <- function(vals, len) sample(rep(vals,ceiling(len/length(vals))))[1:len]

    # make sure we don't repeat a side too often
    mx_rep <- 99; n_mx <- 99
    while(mx_rep>3 || n_mx > 3) {
    trial_type$side[trial_type$ring_type=="rew"] <- mk_reps(c("left","right"), sum(trial_type$ring_type=="rew"))
    trial_type$side[trial_type$ring_type=="neu"] <- mk_reps(c("left","right"), sum(trial_type$ring_type=="neu"))
    n_reps <- rle(trial_type$side)$lengths
    mx_rep <- max(n_reps)
    n_mx <- sum(n_reps==3)
    }
    # split side into position. also check repeats there
    mx_rep <- 99; n_mx <- 99
    while(mx_rep>3 || n_mx > 3) {
        trial_type$position[trial_type$side=="left"] <- mk_reps(c(7,108), sum(trial_type$ring_type=="rew"))
        trial_type$position[trial_type$side=="right"]<- mk_reps(c(532,633), sum(trial_type$ring_type=="neu"))
        n_reps <- rle(abs(trial_type$position-640/2)>300)$lengths
        mx_rep <- max(n_reps)
        n_mx <- sum(n_reps==3)
    }

    onset_type <- left_join(d_py, trial_type) %>% select(onset, ring_type, position) %>%
        mutate(onset=as.numeric(onset))

    # task waits 1.5 after last onset (iti)
    if(max(onset_type$onset) + 1.5 < total_runtime)
        onset_type <- rbind(onset_type, c(total_runtime - 1.5, "iti", NA))
}
