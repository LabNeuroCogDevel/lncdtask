SET "VPXDLL=C:/Users/Luna/Desktop/lncdtask/dll/VPX_InterApp_64.dll
SET "ET_HOST=10.48.88.120"
SET "PYPATH=C:\Program Files\PsychoPy3\python.exe"
SET "TASKDIR=C:\Users\Luna\Desktop\lncdtask"
cd %TASKDIR%
"%PYPATH%" "%TASKDIR%\lncdtask\dollarreward.py" --where mr  --nruns 2  "timing/dollarreward/dollar_reward_noTR_304.2_10871.tsv"  "timing/dollarreward/dollar_reward_noTR_304.2_4341.tsv" "timing/dollarreward/dollar_reward_noTR_304.2_23695.tsv"  "timing/dollarreward/dollar_reward_noTR_304.2_5183.tsv" "timing/dollarreward/dollar_reward_noTR_304.2_25418.tsv"  "timing/dollarreward/dollar_reward_noTR_304.2_7243.tsv"
@echo off
echo ALL DONE. push anykey to close
pause
