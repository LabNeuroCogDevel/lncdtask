2021-05-18WF
 - copied DollarReward task and ViewPoint 2.9.2.5
 TODO:
 - need eyetracking computer password (kvm bottom labeled "unused")
 - setup crossover cable link? (ipconfig has no interface, need admin)
 - debug DLL loading


>>> sys.version
'3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]'
>>> VPXDLL = "C:/Users/Clark/Desktop/ViewPoint 2.9.2.5/VPX_InterApp.dll"
>>> os.path.exists(VPXDLL)
True
>>> from ctypes import cdll, CDLL
>>> cdll.LoadLibrary(VPXDLL)
OSError: [WinError 193] %1 is not a valid Win32 application



2021-06-29 - on laptop
>>> VPXDLL="C:/ARI/VP/VPX_InterApp.dll"
>>> os.path.exists(VPXDLL)
True
>>> cdll.LoadLibrary(VPXDLL)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Program Files\PsychoPy\lib\ctypes\__init__.py", line 426, in LoadLibrary
    return self._dlltype(name)
  File "C:\Program Files\PsychoPy\lib\ctypes\__init__.py", line 348, in __init__
    self._handle = _dlopen(self._name, mode)
OSError: [WinError 126] The specified module could not be found

same error when it doesn't exit
>>> cdll.LoadLibrary(VPXDLL+'x')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Program Files\PsychoPy\lib\ctypes\__init__.py", line 426, in LoadLibrary
    return self._dlltype(name)
  File "C:\Program Files\PsychoPy\lib\ctypes\__init__.py", line 348, in __init__
    self._handle = _dlopen(self._name, mode)
OSError: [WinError 126] The specified module could not be found


####
# not sending?
#####

>>> from ctypes import cdll, CDLL
>>> vpx = CDLL(r"C:/Windows/System32/VPX_InterApp_64.dll")
>>> vpx.VPX_GetStatus(1)
1
>>> vpx.VPX_SendCommand('dataFile_NewName "%s"' % "abc")
0
>>> vpx.VPX_SendCommand('dataFile_NewName "%s"' % "abc")
0
>>> vpx.VPX_SendCommand('dataFile_Close 0')
0
>>> vpx.VPX_SendCommand('dataFile_InsertString "%s"' % "1")
0
>>> vpx.VPX_SendCommand('dataFile_NewName "%s"' % "abc")
0
>>> vpx.VPX_SendCommand('dataFile_InsertString "%s"' % "1")
0