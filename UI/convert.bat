@echo off

set pythonPath=C:\Users\nick.DIRTYCAJUNRICE\AppData\Local\Programs\Python\Python36

echo [START] converting .ui files...

for %%i in (*.ui) do (

echo %%i -- ui_%%~ni.py

%pythonPath%\python.exe -m PyQt5.uic.pyuic -x %%i -o %%~ni.py

)

echo [END] converting .ui files...