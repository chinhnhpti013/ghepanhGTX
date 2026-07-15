@echo off
chcp 65001 >nul
title GTX - Web app Giam dinh Giay to xe
cd /d "%~dp0"

echo ============================================================
echo   GHEP ANH GIAM DINH GIAY TO XE (GTX) - PTI SOS
echo ============================================================
echo.
echo   Dang khoi dong server...
echo   Sau khi thay dong "Running on http://127.0.0.1:5000",
echo   trinh duyet se tu mo. Neu khong, hay mo thu cong:
echo.
echo        http://127.0.0.1:5000
echo.
echo   De DUNG server: bam Ctrl + C hoac dong cua so nay.
echo ============================================================
echo.

REM Mo trinh duyet sau 2 giay (server kip khoi dong)
start "" /b cmd /c "timeout /t 2 >nul & start http://127.0.0.1:5000"

python app.py

echo.
echo Server da dung. Bam phim bat ky de dong...
pause >nul
