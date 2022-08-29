#!/usr/bin/env Rscript

# 20220829WF - init

library(dplyr)
library(tidyr)

d <- read.table('mr_times.tsv', header=T)

nrep_catches <- function(s)
    lapply(strsplit(s, ','), function(x)
        grepl("_c", x) %>%
        rle() %>%
        with(lengths[values]) %>%
        max)
d_mincatch <- d %>%
    mutate(max_catch = nrep_catches(tlist)) %>%
    filter(max_catch < 3, tdur == 304.2) %>%
    select(-max_catch, -tlist, -tdur)


# make sure we can
#  (1) detect a task response, and 
#  (2) measure effects of reward rel. neutral,
#  but not trying to optimize comparisons from one epoch to another
#
#    neutral AS @ each epoch (reward cue, prep, stimulus), and
#    reward vs neutral contrast @ each epoch
d_tot <- d_mincatch %>%
    select(name,
           Neu_Cue=ring_nue_LC, Neu_Prep=prep_nue_LC,
           Neu_Stim=neu_dot_h,
           Diff_Cue=ring_neu.rew_LC, Diff_Prep=prep_neu.rew_LC,
           Diff_Stim=neu_dot.rew_dot_LC) %>%
    mutate(across(-name, function(x) x-min(x))) %>%
    rowwise() %>%
    mutate(tot=sum(c_across(-name))) %>% ungroup %>%
    mutate(r=rank(tot))%>%
    arrange(r)

write.table(d_tot,"mr_ranked.tsv", quote=F,row.names=F)
sink("seeds_top_6.txt")
d_tot %>% filter(r <= 6 ) %>% `[[`("name") %>% gsub('.*-','',.) %>% paste(sep=" ",collapse=" ") %>% cat
sink()
# ontime() { grep -Po '(neu|rew)_ring.*?[0-9] ' out/304.2s/v1_18_$1/events.txt; }
# paste <(ontime 25802) <(ontime 9980) | sed s/\)//g

