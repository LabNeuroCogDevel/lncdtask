SET "PYPATH=C:\Program Files\PsychoPy3\python.exe"
SET "TASKDIR=C:\lncdtask"
cd %TASKDIR%
"%PYPATH%" "%TASKDIR%\lncdtask\rest.py"
@echo off
echo ALL DONE. push anykey to close. see Desktop/task_data for rest data
pause
