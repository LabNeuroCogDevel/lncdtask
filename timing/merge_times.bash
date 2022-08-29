ontime() { grep -Po '(neu|rew)_ring.*?[0-9] ' out/304.2s/v1_32_$1/events.txt; }
eval paste $(sed 's/ /) <(ontime /g;s/^/<(ontime /;s/$/)/;' < seeds_top_6.txt ) | sed 's/)//g'
