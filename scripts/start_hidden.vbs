Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\.."
WshShell.Run "cmd /c call .venv\Scripts\activate.bat && pythonw src\jwhisper.py", 0, False
Set WshShell = Nothing