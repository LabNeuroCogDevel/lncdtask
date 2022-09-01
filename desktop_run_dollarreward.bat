SET "VPXDLL=C:\Users\Clark\Desktop\lncdtask\dll\VPX_InterApp_64.dll"
SET "ET_HOST=10.48.88.120"
SET "PYPATH=C:\Program Files\PsychoPy3\python.exe"
SET "TASKDIR=C:\Users\Clark\Desktop\lncdtask"
cd %TASKDIR%
"%PYPATH%" "%TASKDIR%\lncdtask\dollarreward.py"  --where mr dollar_reward_events.txt
@echo off
echo ALL DONE. push anykey to close
pause
