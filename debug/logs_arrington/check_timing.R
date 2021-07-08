d <- read.table(text=system(" grep ^12 sub-000_ses-01_task-DR_run-3", intern=T), col.names=c("et","time","msg"), sep="\t")
d$diff <- c(0, diff(d$time))
d$onset <- d$time - d$time[1]

hist(d[d$msg!="END"&d$diff>0,'diff'])

# 14 of these!!
d[d$diff>1.8, ]

# > d[67:76,]
#    et     time                msg     diff
# 67 12 108.4943                iti 1.749933
# 68 12 110.2443                iti 1.749928
# 69 12 111.7442  13 ring rew 0.065 1.499931
# 70 12 113.2441   13 cue rew 0.065 1.499938
# 71 12 114.9940   13 dot rew 0.065 1.749919
# 72 12 116.7439                iti 1.749883
# 73 12 118.2438 14 ring rew -0.465 1.499913
# 74 12 120.4938  14 cue rew -0.465 2.249916 # *!!!!!*
# 75 12 121.9937  14 dot rew -0.465 1.499962


l <- read.table(
    text=system("sed 's/ /\t/' log/sub-000_ses-01_task-DR_run-3-1625165763.log", inter=T),
    col.names=c("time", "msg"), sep="\t")
l$diff <- c(0, diff(l$time))
l$onset <- l$time - l$time[1]
# > l[68:77,]
#          time                msg    diff
# 68 1625165873                iti 1.50098
# 69 1625165874                iti 1.66655
# 70 1625165876  13 ring rew 0.065 1.33043
# 71 1625165877   13 cue rew 0.065 1.50398
# 72 1625165879   13 dot rew 0.065 1.49602
# 73 1625165880                iti 1.49897
# 74 1625165882 14 ring rew -0.465 1.49999
# 75 1625165883  14 cue rew -0.465 1.50017
# 76 1625165885  14 dot rew -0.465 1.49881
# 77 1625165886                iti 1.49999


m <- merge(d[d$msg!="iti",], l[l$msg!="iti",], by="msg", suffixes=c(".et",".log"))
m %>% select(msg,onset.et, onset.log, diff.et, diff.log) %>% arrange(onset.log) %>% head

# onsets should be 1.5 fixed
e <- read.csv("onsets_03-1625166081.csv")
e$diff <- c(0, diff(e$onset0))

#>  e[67:76,c('event_name','ring_type','onset0','diff')]
#    event_name ring_type onset0 diff
# 67        iti             99.0  1.5
# 68        iti            100.5  1.5
# 69       ring       rew  102.0  1.5
# 70       prep       rew  103.5  1.5
# 71        dot       rew  105.0  1.5
# 72        iti            106.5  1.5
# 73       ring       rew  108.0  1.5
# 74       prep       rew  109.5  1.5
# 75        dot       rew  111.0  1.5



# > NCmisc::textogram(d[d$diff>0 & d$msg!="END",'diff'])
# 1.2   .....
# 1.3
# 1.4   .................................................
# 1.5
# 1.6
# 1.7   .......................................
# 1.8
# 1.9   ......
#   2
# 2.1
# 2.2
# > NCmisc::textogram(l$diff[l$diff>.1])
#  using halved %'s as maximum freq is too big for terminal
# 0.2
# 0.4
# 0.6
# 0.8
#   1
# 1.2
# 1.4   .................................................
# 1.6
# 1.8
#   2
# 2.2
# 2.4
# 2.6

library(dplyr); library(tidyr); library(ggplot2)

long <- d %>%
   select(msg, onset, diff) %>%
   mutate(from="ET", i=1:n()) %>%
   rbind(l %>%
         select(msg, onset, diff) %>%
         mutate(from="log", i=1:n())) %>%
   separate(msg,c('trial', 'event', 'rew', 'side')) %>%
   mutate(trial=as.numeric(trial))

ggplot(long %>% filter(!is.na(trial)))+
   aes(y=diff, x=trial, color=from) +
   geom_point() + facet_wrap(~event) +
   ggtitle("time from prev for each event in a trial (cue->dot->ring). Eye file vs psychopy time log")
ggsave("diff_by_trial_event.png", height=3, width=12)

long$event[is.na(long$event)] <- 'iti'
ggplot(long %>% filter(diff < 2.2 & diff > 1, event!='task')) +
   aes(x=diff, fill=event) +
   geom_histogram() +
   facet_wrap(~from, scales="free_x") +
   ggtitle("time from prev event")
ggsave("diff_distribution.png")

ggplot(long %>% filter(diff < 3)) +
   aes(x=i, y=onset, shape=event, color=from) +
   geom_point() +
   ggtitle("second are larger for ET?")
ggsave("ET_constantly_higher_times.png", width=12, height=3)
