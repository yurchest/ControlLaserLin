cd  %~dp0\venv_win\Scripts

pyuic5.exe -x %~dp0\form0.ui  -o %~dp0\form0.py
pyuic5.exe -x %~dp0\form1.ui  -o %~dp0\form1.py
pyrcc5.exe %~dp0\newprefix.qrc -o %~dp0\newprefix_rc.py

pause

