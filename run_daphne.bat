@echo off
if exist .venv\Scripts\activate (
  call .venv\Scripts\activate
)
echo Starting Daphne ASGI server...
daphne -b 127.0.0.1 -p 8000 storeproj.asgi:application
