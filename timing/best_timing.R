library(dplyr)
library(tidyr)
library(ggplot2)
theme_set(cowplot::theme_cowplot())
d <- read.table('mr_times.tsv',header=T)

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
    mutate(r=rank(tot))


long <- d_tot %>% gather(m, v, -name) %>%
    separate(m, c("cond", "event"), sep="_")

d_event <-
    merge(long %>% filter(cond=="Neu"),
          long %>% filter(cond=="Diff"),
          by=c("name", "event"),
          suffixes = c("Neu", "Diff")) %>%
          merge(d_tot %>% select(name, tot, r), by="name")
picks <- d_event %>%
    filter(r <= 10) %>%
    group_by(name) %>%
    filter(vNeu==min(vNeu))

ggplot(d_event %>% filter(r < 50)) +
    aes(x=vNeu, y=vDiff, color=event, label=r) +
    #facet_wrap(~event)
    geom_line(aes(group=name,color=NULL, size=NULL), alpha=.4) +
    geom_point(aes(size=tot)) +
    geom_line(data=d_event %>% filter(r<10), aes(group=name), alpha=1, color='red') +
    geom_label(data=picks, aes(size=NULL,color=NULL),alpha=.3)+
    ggtitle("best 50 (sumLC):  neu-rew Vs neu per event")+
    labs(size = "Summed LC")

d_tot %>% filter(r %in% seq(6)) %>% `[[`("name") %>% gsub('.*-','',.) %>% paste(sep=" ",collapse=" ")
# v1-304.2-18-25802
# v1-304.2-18-9980 
# ontime() { grep -Po '(neu|rew)_ring.*?[0-9] ' out/304.2s/v1_18_$1/events.txt; }
# paste <(ontime 25802) <(ontime 9980) | sed s/\)//g


ggplot(d_event %>% filter(r<5000)) +
    aes(x=vNeu, y=vDiff, label=r, size=tot) +
    facet_wrap(~event) +
    stat_bin2d() + 
    ggtitle("top 5000")
