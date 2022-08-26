library(dplyr)
library(glue)
tdf <- read.table('dollar_reward_events.txt', sep="\t", col.names = c("run","tname","position","ring_type","event_name"))

# remove catch trials; remove repeated fix
rmmr <- tdf %>% filter(!grepl("Catch", tname)) %>% mutate(rep=event_name==lag(event_name, default="first")) %>% filter(!rep) 

rmmr %>% split(.$run) %>%
    lapply(function(d) d %>%
                       mutate(onset=1.5*(1:n()-1)) %>%
                       select(onset, event_name, ring_type, position) %>% 
           write.table(file=glue("dollar_reward_eeg{first(d$run)}.tsv"), quote=F, row.names=F,sep="\t"))
  
