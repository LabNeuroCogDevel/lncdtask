#!/usr/bin/env Rscript

# collapse stddev tests into single file
# include event list for limiting catch trial repeats
# and maybe rew or neu repeats
# 2022082xWF - init

library(dplyr)
library(glue)
list_rings <- function(f) {
   f <- gsub('stddevtests.tsv','events.txt', f)
   glue("grep -o '[^(]*ring[^)]*' {f} |paste -sd,") %>%
      system(intern=T) }
flist <- Sys.glob('out/3[0-9]*s/v*/stddevtests.tsv')
fits <- flist %>%
   lapply(function(f)
        tryCatch(
          read.table(f, sep="\t", header=T) %>%
          mutate(tdur=gsub('.*/([0-9.]+)s/.*', '\\1', f),
                 tlist=sapply(f,list_rings)),
        error=function(f )NULL)) %>%
   bind_rows
write.table(file='mr_times.tsv', fits, row.names=F,quote=F)
