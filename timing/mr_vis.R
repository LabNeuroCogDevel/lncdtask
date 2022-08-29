#!/usr/bin/env Rscript

# 20220829WF - init

library(dplyr)
library(ggplot2)
library(cowplot)
library(tidyr)
theme_set(theme_cowplot())
d_tot <- read.table('mr_ranked.tsv',header=T)

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

p <- plot_grid(nrow=2,
 ggplot(d_event %>% filter(r < 50)) +
    aes(x=vNeu, y=vDiff, color=event, label=r) +
    #facet_wrap(~event)
    geom_line(aes(group=name,color=NULL, size=NULL), alpha=.4) +
    geom_point(aes(size=tot)) +
    geom_line(data=d_event %>% filter(r<10), aes(group=name), alpha=1, color='red') +
    geom_label(data=picks, aes(size=NULL,color=NULL),alpha=.3)+
    ggtitle("best 50 (sumLC):  neu-rew Vs neu per event")+
    labs(size = "Summed LC"),
 ggplot(d_event %>% filter(r<5000)) +
    aes(x=vNeu, y=vDiff, label=r, size=tot) +
    facet_wrap(~event) +
    stat_bin2d() + 
    ggtitle("top 5000")
 )
ggsave("dollar_reward_timing.png")
