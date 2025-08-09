Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\whisper_hotkey"
WshShell.Run "cmd /c call .venv\Scripts\activate.bat && python whisper_server_simple.py", 7
Set WshShell = Nothing