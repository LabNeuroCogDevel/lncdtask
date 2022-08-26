SET "PYPATH=C:\Program Files\PsychoPy\python.exe"
SET "TASKDIR=C:\Users\Luna\Desktop\lncdtask"
cd %TASKDIR%
"%PYPATH%" "%TASKDIR%\lncdtask\dollarreward.py" "timing/dollar_reward_eeg1.tsv" "timing/dollar_reward_eeg2.tsv" "timing/dollar_reward_eeg3.tsv" "timing/dollar_reward_eeg4.tsv"
@echo off
echo ALL DONE. push anykey to close
pause
