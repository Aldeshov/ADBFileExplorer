call .\venv\Scripts\activate.bat
set PYTHONUNBUFFERED=1
set PYTHONPATH=%cd%\src\app;%cd%\src;%cd%
python.exe .\src\app
