dollar_reward_timing.png: mr_ranked.tsv
	./mr_vis.R

mr_ranked.tsv: mr_times.tsv
	./best_timing.R

mr_times.tsv:
	./mr_collect.R

# seed top made at same time as mr_ranked.tsv
# tracking depend here
seeds_top_6.txt: mr_ranked.tsv

dollarreward/304.2_trial_order_onsets.txt: seeds_top_6.txt
	./merge_times.bash > $@
