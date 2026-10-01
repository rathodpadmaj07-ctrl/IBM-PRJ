Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strFolder = fso.GetParentFolderName(WScript.ScriptFullName)

' Set working directory to app folder
WshShell.CurrentDirectory = strFolder

' pythonw.exe is Python GUI executable for Windows (creates ZERO terminal / console window)
pythonwPath = "C:\Users\Padmaj Rathod\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe"

WshShell.Run """" & pythonwPath & """ -m streamlit run """ & strFolder & "\app.py""", 0, False
