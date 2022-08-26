SET VPXDLL="C:\Users\Clark\Desktop\lncdtask\dll\VPX_InterApp_64.dll"
SET "PYPATH=C:\Program Files\PsychoPy3\python.exe"
SET "TASKDIR=C:\Users\clark\Desktop\lncdtask"
cd %TASKDIR%
"%PYPATH%" "%TASKDIR%\test_arrington.py"
@echo off
echo ALL DONE. push anykey to close
pause
