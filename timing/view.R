library(dplyr)
library(ggplot2)
library(cowplot)
fits <- Sys.glob('out/3[0-9]*s/v*/stddevtests.tsv') %>%
   lapply(function(f)
          read.table(f, sep="\t", header=T) %>%
          mutate(tdur=gsub('.*/([0-9.]+)s/.*', '\\1', f))) %>%
   bind_rows
theme_set(theme_cowplot())

plot_grid(ncol=2,
 ggplot(fits %>% filter(prep_neu.rew_LC<1.5)) +
    aes(x=ring.prep_LC, y=prep_neu.rew_LC, color=neu_dot.rew_dot_LC) +
    geom_point() + theme(legend.position="none") + ggtitle('std dev contrast (decon nodata)'),
 ggplot(fits%>% filter(ring.dot_LC<.5)) +
    aes(x=ring.dot_LC, y=neu_dot.rew_dot_LC, color=neu_dot.rew_dot_LC) +
    geom_point())
