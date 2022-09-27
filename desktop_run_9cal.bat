SET "VPXDLL=C:/Users/Luna/Desktop/lncdtask/dll/VPX_InterApp_64.dll
SET "ET_HOST=10.48.88.120"
SET "PYPATH=C:\Program Files\PsychoPy3\python.exe"
SET "TASKDIR=C:\Users\Luna\Desktop\lncdtask"
cd %TASKDIR%
"%PYPATH%" "%TASKDIR%\lncdtask\cal_points.py" --tracker arrington --fullscreen yes
@echo off
echo ALL DONE. push anykey to close
pause
