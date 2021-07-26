set app=yw-timeline
set basedir="%APPDATA%\PyWriter"
if not exist %basedir% md %basedir%
set appdir="%APPDATA%\PyWriter\%app%"
if not exist %appdir% md %appdir%
copy %app%.pyw %appdir%

set TARGET='%APPDATA%\PyWriter\%app%\%app%.pyw'
set SHORTCUT='%USERPROFILE%\desktop\%app%.lnk'
set PWS=powershell.exe -ExecutionPolicy Bypass -NoLogo -NonInteractive -NoProfile

%PWS% -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut(%SHORTCUT%); $S.TargetPath = %TARGET%; $S.Save()"

set cnfdir="%APPDATA%\PyWriter\%app%\config"
if not exist %cnfdir% md %cnfdir%
rem echo "N" | copy/-Y sample\%app%\*.* %cnfdir%
