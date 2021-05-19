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

