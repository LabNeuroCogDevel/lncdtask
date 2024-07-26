REM also see https://github.com/NPACore/mri-tasks/blob/main/change_ip.bat
@echo ====
@echo CHANGE IP: upmc or eyelink
@echo ====

REM name of network in "Network Connections"
REM at MRRC "Local Area Network". for Jones laptop="Ethernet"
@set INTERFACE="Ethernet"

:getchoice
 @set /p choice="[avotec,eyelink] "
 @if NOT "%choice%"  == "avotec" if NOT "%choice%" == "eyelink" goto getchoice
 @goto %choice%


REM 131 is new P2 test computer. 121 is P1 (as of 20240726)
:avotec
 set IP=10.48.88.131
 set GW=10.48.88.1
 goto setconnect

:eyelink
 set IP=100.1.1.2
 set GW=100.1.1.1
 goto setconnect


:setconnect
 set MASK=255.255.255.0
 netsh interface ip set address "%INTERFACE%" static %IP% %MASK% %GW% 1

 netsh int ip show config "%INTERFACE%"
 pause
