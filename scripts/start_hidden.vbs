Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
scriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
rootDir = FSO.GetParentFolderName(scriptDir)
WshShell.CurrentDirectory = rootDir
WshShell.Run "cmd /c call scripts\.venv\Scripts\activate.bat && pythonw src\jwhisper.py", 0, False
Set WshShell = Nothing