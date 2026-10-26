' TimeLogApp - Silent VBScript Launcher
' Launches TimeLogApp_PySide6.py without showing command window

Set objShell = CreateObject("WScript.Shell")
strScriptPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
strPythonScript = strScriptPath & "\TimeLogApp_PySide6.py"

' Run Python silently (0 = hidden window)
objShell.Run "python """ & strPythonScript & """", 0, False
