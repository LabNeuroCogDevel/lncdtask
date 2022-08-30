#!/usr/bin/env Rscript

#
# 20220531 WF - read make_random_timing.py output and shape like ../dollar_reward_events.txt
# as read by [[file:~/src/work/lncdtask/lncdtask/dollarreward.py::onset_df =]]
# and used by events like [[file:~/src/work/lncdtask/lncdtask/dollarreward.py::self.add_event_type]] 
# and only cares about onset, ring_type, and position (translated from initial input)
#

library(dplyr)
library(tidyr)

mk_reps <- function(vals, len) sample(rep(vals,ceiling(len/length(vals))))[1:len]

max_side <- function(trial_type){

  nrew <- sum(trial_type$ring_type=="rew")
  nneu <-  sum(trial_type$ring_type=="neu")
  # make sure we don't repeat a side too often
  mx_rep <- 99; n_mx <- 99
  while(mx_rep>3 || n_mx > 3) {
    trial_type$side[trial_type$ring_type=="rew"] <- mk_reps(c("left","right"), nrew)
    trial_type$side[trial_type$ring_type=="neu"] <- mk_reps(c("left","right"), nneu)
    n_reps <- rle(trial_type$side)$lengths
    mx_rep <- max(n_reps)
    n_mx <- sum(n_reps==3)
  }
  return(trial_type)
}

max_pos <- function(trial_type, max_pos_diff=1) {
   # split side into position. also check repeats there
   # initial version had 4 positions per side but was too tight
   # three used by newest eprime dollar rewards
   #  007 108 214 |=center=320=| 426 532 633
   # but dont need all of those. using 2 per side
   nrew <- sum(trial_type$ring_type=="rew")
   nneu <-  sum(trial_type$ring_type=="neu")
   mx_rep <- 99; n_mx <- 99
   while(mx_rep>3 || n_mx > 3) {
       trial_type$position[trial_type$side=="left"] <- mk_reps(c(7, 214), nrew)
       trial_type$position[trial_type$side=="right"]<- mk_reps(c(426,633), nneu)
       n_reps <- rle(abs(trial_type$position-640/2)>300)$lengths
       mx_rep <- max(n_reps)
       n_mx <- sum(n_reps==3)
       # also dont want to be too unequal across sides
       rng <- with(trial_type, split(position,ring_type) %>%
                   sapply(function(p) diff(range(rle(sort(p))$lengths))))
       if(max(rng)>max_pos_diff) mx_rep <- 99
   }
  return(trial_type)
}

add_rest<-function(d){
   #cols: rest onset trial rest
   iti<-last(d$rest)
   new_row <- data.frame(event="iti_iti",
                         onset=last(d$onset)+last(d$dur),
                         dur=iti,
                         rest=0,
                         trial=last(d$trial))
   rbind(d, new_row) %>%
      mutate(trial_type=first(event))
}

afni_to_task <- function(fname="out/510s/v1_60_26546/events.txt", total_runtime=510) {
    # parse event.csv from make_random_timing.py and add balenced position
    d <- read.table(fname,skip=3)
    names(d) <- c("n","event","onset","dur","rest") # rest is time between events
    d <- d %>% mutate(event=gsub("\\(|\\)","",event),
                rest=as.numeric(rest),
                trial = 1 + cumsum(lag(rest, default=0)!=0)) %>% select(-n)

    d_py <- d %>%
        split(d$trial) %>%
        lapply(add_rest) %>%
        bind_rows %>%
        select(-rest) %>% 
        separate(event,c("ring_type","event_name", "catch"),remove=FALSE,fill="right")

    row.names(d_py)<-NULL


    #  only care about position if not a catch trial. 
    # have 4 positions, but only 2 sides.
    # first divy up left and right. then divy that into position.
    # this hopefully minimizes any left/right asymetry
    trial_type <- d_py %>% group_by(trial) %>% filter(row_number()==1, is.na(catch)) %>%
        select(trial,ring_type) %>%
        mutate(side=NA, position=NA)

    trial_type <- max_side(trial_type)
    trial_type <- max_pos(trial_type)
    # trial_type %>% group_by(ring_type,position) %>% tally -- all 2s and 3s

    onset_type <- left_join(d_py, trial_type) %>% select(onset, event_name, ring_type, position) %>%
        mutate(onset=as.numeric(onset))

    # need iti event at start to clear screen
    # NB. list() b/c c() will coearse 0 to character to match type of "iti"
    if(min(onset_type$onset) > 0)
        onset_type <- rbind(list(0, "iti", "iti", NA), onset_type)
    # task waits 1.5 after last onset (iti)
    if(max(onset_type$onset) + 1.5 < total_runtime)
        onset_type <- rbind(onset_type, list(total_runtime - 1.5, "iti",NA, NA))



    # python requires 'event_name' column name ('onset' and 'position' already good)
    return(onset_type)
}

collect_timings <- function(stddev_patt="out/*/*/stddevtests.tsv"){
  # takes a loonnnng time on remote filesystem
  collected_fname <- 'std_dev_tests.tsv'
  if(file.exists(collected_fname))
      return(read.table(collected_name,header=T,sep="\t"))

  flist <- Sys.glob(stddev_patt)
  d <- flist %>% lapply(function(f) read.table(f,header=T) %>% mutate(fname=f)) %>% bind_rows
  write.table(d, 'std_dev_tests.tsv', row.names=F)
  return(d)
}
save_events <- function(fname, total_dur) {
    event_fname <- gsub('stddevtests.tsv','events.txt',fname)
    seed <- stringr::str_extract(fname, '(?<=v1_32_)[0-9]+')
    outname <- glue::glue("dollar_reward_noTR_{total_dur}_{seed}.tsv")
    onset_pos <- afni_to_task(event_fname, total_dur)
    write.table(onset_pos,file=outname,sep="\t", row.names=F, quote=F)
    return(outname)
}
find_best <- function(cols=c("neu_ring-rew_ring_LC", "neu_dot-rew_dot_LC")){
    stddevs <- collect_timings('/Volumes/Hera/Projects/lncdtask/timing/out/*/v*/stddevtests.tsv')
    cols <- cols %>% gsub('-','.',.)
    rank_i <- order(apply(stddevs[,cols],1,sum))
    stddevs[head(rank_i),c("fname",cols)] %>% print
    return(stddevs[rank_i[1:4],'fname'])
}

# previously using less relevant columns
#find_best(c("neu_ring-rew_ring_LC", "neu_dot-rew_dot_LC")) %>% lapply(save_events)

# 20220829 - updated for shorter events
#top_times <- unlist(read.table(file='seeds_top_6.txt',sep=" ",header=F))
mr_times <- read.table('mr_ranked.tsv',header=T) %>%
   filter(r<=6) %>%
   tidyr::separate(name,c('ver','rdur','tcnt','seed'),sep="-") %>%
   mutate(fname=glue::glue("out/{rdur}s/{ver}_{tcnt}_{seed}/stddevtests.tsv"))
outputs <- sapply(mr_times$fname, save_events, total_dur=304.2)

lapply(outputs, function(x) {
 x <- read.table(x,header=T)
 list(pos=x %>% filter(event_name=='dot') %>% group_by(ring_type,position) %>% tally,
      rew=x %>% filter(event_name=='dot') %>% group_by(ring_type) %>% tally)})




test_add_rest <- function(){
   x<- add_rest(data.frame(event="dot",onset=1,rest=3,trial=1,dur=1.5))
   testthat::expect_equal(last(x$onset), 2.5)
}
