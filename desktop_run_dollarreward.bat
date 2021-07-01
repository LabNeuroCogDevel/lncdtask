SET "VPXDLL=C:\Windows\System32\VPX_InterApp_64.dll"
SET "PYPATH=C:\Program Files\PsychoPy\python.exe"
SET "TASKDIR=C:\Users\ncanda\Desktop\lncdtask"
cd %TASKDIR%
"%PYPATH%" "%TASKDIR%\lncdtask\dollarreward.py"
@echo off
echo ALL DONE. push anykey to close
pause
