SET "VPXDLL=C:/Windows/System32/VPX_InterApp_64.dll"
SET "ET_HOST=10.48.88.120"
SET "PYPATH=C:\Program Files\PsychoPy\python.exe"
SET "TASKDIR=C:\Users\Luna\Desktop\lncdtask"
cd %TASKDIR%
"%PYPATH%" "%TASKDIR%\lncdtask\dollarreward.py" "timing/dollar_reward_noTR_12228.tsv" "timing\dollar_reward_noTR_23337.tsv"
@echo off
echo ALL DONE. push anykey to close
pause
