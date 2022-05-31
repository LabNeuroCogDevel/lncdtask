#!/usr/bin/env bash
set -x
#
# generate timings for MR task with decaying ITI and catch trials
#
# 20220531WF - copied from landscape choice
#
# original input files has 4 runs with events like
# with 6 sides, 2 types (rew, neut), and catches at ring (15%) and prep (15%)
# tr locked at 1.5s
# cut -f 5- ../dollar_reward_events.txt |sort |uniq -c
#    160 ring (stop here catch 1)
#    136 prep (stop here catch 2)
#    112 dot  (not seen on catch)
#
# want 2 runs of ~ 8min. not tr locked
#


# original iti (fixed 1.5s) durations across all runs
# included last e.g. 11s of rest
# cut -f 5 ../dollar_reward_events.txt |uniq -c |grep iti|awk '{print $1}'|sort -n | uniq -c
#   106 1
#    20 3
#    13 4
#     4 5
#     5 6
#     1 8
#     3 9
#     4 10
#     2 11
#     1 14
#     1 21
[ -v DRYRUN ] && DRYRUN=echo || DRYRUN=
warn(){ echo "$@" >&2; }

# hard coded timings from piloting
# NB: RT probably different in MR comared to amazon turk

TR=1.3

# save directory prefix incase we update e.g. GLT SYMS or timings
# but want to hold onto old
# will already be organized by total runtime and include total_trials
#   outdir=${total_runtime}s/${PREFIX}_${total}_$seed
PREFIX=v1

E_DUR=1.5  # original length of each event
TOTAL_RUNTIME=510 # 8.5 min
# with 2s mean iti have 9 secs of start/stop
#  n<-36; 2*(n*1.5*3 + (n*.3)*3 + (n*.15)*1.5) + (n+n/3)*2
# [1] 501

# how many full trials of reward or neutral
# total full = 2 * number given
# total ring = 2*(x+x/3)
# total prep  = 2*(x+x/6)
N_EA_TYPE=30
N_RING_C1=$(printf %.0f $(echo $N_EA_TYPE/3|bc)) # 12
N_PREP_C2=$(printf %.0f $(echo $N_EA_TYPE/6|bc)) # 6
N_FULL=$((2*N_EA_TYPE))


# from https://github.com/LabNeuroCogDevel/slipstask/tree/master/timing
parse_decon(){
   # widen deconvolve output of norm std dev tests
   # so we can collect everything later in one file
   # see test for output/input
   perl -slne '
        $key=$2 if /(Gen|Stim).*: ([^ ]*)/;
        $h{$name}{"${key}_$1"}=$2 if /^\W+(LC|h).*=.*?([0-9.]+)/;
        END{
          @vals=sort (keys %{$h{(keys %h)[0]}});
          print join("\t","name",@vals);
          for my $f (keys %h){
            %_h = %{$h{$f}};
            print join("\t",$f, @_h{@vals} )
          }
    }' -- -name="$1"
}

add_glt(){
   # add glts to decon command file
   # needs already have e.g. '-numglt 3' and '-x1D'
   # input is file and then any number of contrast+label pairs like
   #   add_glt decon.tsch 'a -b' 'a-b' 'c +.5*d' 'c_halfd'
   cmd_file="$1";shift
   nglt=$(grep -Po '(?<=-num_glt )\d+' $cmd_file||echo "")
   [ -z "$nglt" ] && warn "ERROR: no -num_glt in '$cmd_file'" && exit 1
   newn=$nglt
   glts=""
   while [ $# -gt 0 ]; do
      let newn++
      glts="$glts -gltsym 'SYM: $1' -glt_label $newn $2"
      shift 2
   done

   sed -e "s/-num_glt $nglt/-num_glt $newn/" -i $cmd_file
   sed -e "s;-x1D;$glts -x1D;" -i $cmd_file
}

mktiming(){

  # second arg should be seed. can use random if not provided
  # TODO: max $RANDOM vs max make_random_timing seed
  [ $# -ne 0 ] && seed="$1" || seed="$RANDOM"

  outdir=${TOTAL_RUNTIME}s/${PREFIX}_${N_FULL}_$seed
  [ -d $outdir ] && warn "# have $outdir dir, skipping" && return 0
  mkdir -p $outdir
  (cd $outdir
  make_random_timing.py \
     -tr $TR \
     -num_runs 1 -run_time $TOTAL_RUNTIME        \
     -pre_stim_rest 3 \
     -rand_post_stim_rest yes             \
     -add_timing_class s_neu_ring  "$E_DUR"  \
     -add_timing_class s_rew_ring  "$E_DUR"  \
     -add_timing_class s_prep      "$E_DUR" \
     -add_timing_class s_dot       "$E_DUR"\
     \
     -add_timing_class nobreak 0 0 0 dist=INSTANT \
     -add_timing_class iti 1.5 -1 15     \
     \
     -add_stim_class neu_ring      "$N_EA_TYPE"  s_neu_ring  nobreak \
     -add_stim_class rew_ring      "$N_EA_TYPE"  s_rew_ring  nobreak \
     -add_stim_class neu_ring_c2   "$N_PREP_C2"  s_neu_ring  nobreak \
     -add_stim_class rew_ring_c2   "$N_PREP_C2"  s_rew_ring  nobreak \
     -add_stim_class neu_prep      "$N_EA_TYPE"  s_prep nobreak\
     -add_stim_class rew_prep      "$N_EA_TYPE"  s_prep nobreak\
     -add_stim_class neu_dot       "$N_EA_TYPE"  s_dot iti \
     -add_stim_class rew_dot       "$N_EA_TYPE"  s_dot iti \
     -add_stim_class neu_ring_c1   "$N_RING_C1"  s_neu_ring  iti \
     -add_stim_class rew_ring_c1   "$N_RING_C1"  s_rew_ring  iti \
     -add_stim_class rew_prep_c2   "$N_PREP_C2"  s_prep  iti\
     -add_stim_class neu_prep_c2   "$N_PREP_C2"  s_prep  iti\
     `:          nr rr nr2 rr2 np rp nd rd nc1 rc1  np2 rp2` \
     -max_consec 2  2    2   2  0  0  0  0   2   2    0   0  \
     `: -ordered_stimuli neu_ring_c1`       \
     `: -ordered_stimuli rew_ring_c1`       \
     -ordered_stimuli neu_ring_c2 neu_prep_c2  \
     -ordered_stimuli rew_ring_c2 rew_prep_c2  \
     -ordered_stimuli neu_ring neu_prep neu_dot \
     -ordered_stimuli rew_ring rew_prep rew_dot \
     -show_timing_stats                 \
     -make_3dd_contrasts                \
     -write_event_list events.txt \
     -save_3dd_cmd decon.tcsh      \
     -seed $seed                        \
     -prefix stimes > mktiming.log


  # TODO: does prep including full ring distored ring-prep contast sd?
  # TODO: how to contrast prep-dot
  add_glt decon.tcsh \
     '.5*neu_ring +.5*rew_ring +.17*neu_ring_c1 +.17*rew_ring_c1 +.08*rew_prep_c2 +.08*neu_prep_c2 -.5*rew_dot -.5*neu_dot' 'ring-dot' \
     '.5*neu_ring +.5*rew_ring +.17*neu_ring_c1 +.17*rew_ring_c1 -.5*neu_prep -.5*rew_prep  -.08*neu_prep_c2 -.08*rew_prep_c2' 'ring-prep' \


  tcsh decon.tcsh > decon.log
  parse_decon "${PREFIX}-${TOTAL_RUNTIME}-${N_FULL}-${seed}" < decon.log > stddevtests.tsv
  1d_tool.py -cormat_cutoff 0.1 -show_cormat_warnings -infile X.stimes.xmat.1D > timing_cor.txt
)
}

# if not sourced (as in testing), run as command
if ! [[ "$(caller)" != "0 "* ]]; then
  set -euo pipefail
  trap 'e=$?; [ $e -ne 0 ] && echo "$0 exited in error $e"' EXIT

  # potentially man output directories. collect in one place
  [ ! -d out ] && mkdir out
  cd out
  mktiming
  exit $?
fi

####
# testing with bats. use like
#   bats ./mk_timing.bash --verbose-run
####
if  [[ "$(caller)" =~ /bats.*/preprocessing.bash ]]; then
function trialcount_test { #@test
  local total=12
  eval $MACRO_TRIAL_COUNTS
  warn "'$good' '$nogood' '$good_catch' '$nogood_catch'"
  [ $good -eq 5 ]
  [ $nogood -eq 3 ]
  [ $good_catch -eq 3 ]
  [ $nogood_catch -eq 1 ]
}
function parse_test { #@test

 output="$(cat <<HERE| parse_decon XXX
Stimulus: ng_zzz_c
  h[ 0] norm. std. dev. =   3.3897

General Linear Test: good_c-nogood_c
  LC[0] norm. std. dev. =   5.6284
HERE
)"

 warn "$output"
 [[ $output =~ ng_zzz_c_h ]]
 [[ $output =~ good_c-nogood_c_LC ]]
 [[ $output =~ 3.3897 ]]
}
function add_glt_test { #@test
   f=/tmp/glttestfile
   echo "-num_glt 4 -x1D " > $f
   run add_glt $f 'a +b' 'a_P_b' 'a -b' 'a-b'
   warn "file: '$(cat $f)'"
   grep "\-num_glt 6" $f
   grep "SYM: a +b" $f
   grep "\-glt_label 6 a-b" $f
}
fi
