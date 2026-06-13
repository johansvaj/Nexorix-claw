@echo off
setlocal enabledelayedexpansion

echo =================================================
echo    Nexcorix Claw Smart Installer v9.0 (Windows)
echo =================================================

:: Deteksi Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan. Install Python 3.8+.
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo [✓] Python %PY_VER%

:: Virtual environment
if not exist "venv" (
    echo [i] Membuat virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo [✓] Virtual environment aktif

:: Upgrade pip
python -m pip install --upgrade pip >nul 2>&1

:: Pilih mode
echo.
echo Pilih mode instalasi:
echo   1) Minimal (^<2 MB)    - hanya requests, urllib3
echo   2) Medium (~50 MB)    - + chromadb, onnxruntime
echo   3) Full (~300 MB)     - semua library (sentence-transformers ditanya)
echo   4) Custom             - pilih sendiri
set /p mode="Masukkan pilihan [1/2/3/4]: "

:: Minimal selalu
echo [i] Memeriksa library minimal...
python -c "import requests" 2>nul || python -m pip install requests
python -c "import urllib3" 2>nul || python -m pip install urllib3

if %mode%==2 goto medium
if %mode%==3 goto full
if %mode%==4 goto custom
goto run

:medium
echo [i] Memeriksa library medium...
python -c "import chromadb" 2>nul || python -m pip install chromadb
python -c "import onnxruntime" 2>nul || python -m pip install onnxruntime
:: Pre-download model ONNX (opsional)
python -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; ONNXMiniLM_L6_V2()" 2>nul
goto run

:full
echo [i] Memeriksa library medium...
python -c "import chromadb" 2>nul || python -m pip install chromadb
python -c "import onnxruntime" 2>nul || python -m pip install onnxruntime
python -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; ONNXMiniLM_L6_V2()" 2>nul
echo [i] Memeriksa library full...
python -c "import fastapi" 2>nul || python -m pip install fastapi
python -c "import uvicorn" 2>nul || python -m pip install uvicorn
python -c "import telegram" 2>nul || python -m pip install python-telegram-bot
python -c "import discord" 2>nul || python -m pip install discord.py
python -c "import schedule" 2>nul || python -m pip install schedule
python -c "import yaml" 2>nul || python -m pip install pyyaml
set /p ans="Install sentence-transformers ( ~80 MB + PyTorch ~1GB )? [y/N]: "
if /i "!ans!"=="y" (
    python -c "import sentence_transformers" 2>nul || python -m pip install sentence-transformers
)
goto run

:custom
echo Pilih library (pisah spasi): chromadb onnxruntime fastapi uvicorn python-telegram-bot discord.py schedule pyyaml sentence-transformers
set /p custom="Masukkan: "
for %%c in (%custom%) do (
    if "%%c"=="chromadb" (python -c "import chromadb" 2>nul || python -m pip install chromadb)
    if "%%c"=="onnxruntime" (python -c "import onnxruntime" 2>nul || python -m pip install onnxruntime)
    if "%%c"=="fastapi" (python -c "import fastapi" 2>nul || python -m pip install fastapi)
    if "%%c"=="uvicorn" (python -c "import uvicorn" 2>nul || python -m pip install uvicorn)
    if "%%c"=="python-telegram-bot" (python -c "import telegram" 2>nul || python -m pip install python-telegram-bot)
    if "%%c"=="discord.py" (python -c "import discord" 2>nul || python -m pip install discord.py)
    if "%%c"=="schedule" (python -c "import schedule" 2>nul || python -m pip install schedule)
    if "%%c"=="pyyaml" (python -c "import yaml" 2>nul || python -m pip install pyyaml)
    if "%%c"=="sentence-transformers" (
        set /p ans="Install sentence-transformers ( ~80 MB + PyTorch ~1GB )? [y/N]: "
        if /i "!ans!"=="y" (python -c "import sentence_transformers" 2>nul || python -m pip install sentence-transformers)
    )
)
goto run

:run
if not exist "nexcorix_claw.py" (
    echo [ERROR] nexcorix_claw.py tidak ditemukan.
    exit /b 1
)
echo [✓] Menjalankan Nexcorix Claw...
python nexcorix_claw.py
pause
