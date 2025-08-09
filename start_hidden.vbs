Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\whisper_hotkey"
WshShell.Run "cmd /c call .venv\Scripts\activate.bat && pythonw whisper_tray.py", 0, False
Set WshShell = Nothing