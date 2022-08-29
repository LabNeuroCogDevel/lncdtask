ontime() { grep -Po '(neu|rew)_ring.*?[0-9] ' out/304.2s/v1_18_$1/events.txt; }
paste <(ontime 25802 ) <(ontime  27385) <(ontime 27944) <(ontime 30709) <(ontime 4342) <(ontime 9980) | sed s/\)//g> dollarreward/304.2_trial_order_onsets.txt
