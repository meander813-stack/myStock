@echo off
echo ========================================
echo   주식 앱 실행 중...
echo ========================================
echo.

:: 백엔드 실행 (새 창)
echo [1/2] 백엔드 서버 시작...
start "백엔드 - FastAPI" cmd /k "cd /d D:\AI\myStock\backend && python main.py"

:: 잠깐 대기 (백엔드 먼저 뜨도록)
timeout /t 3 /nobreak > nul

:: 프론트엔드 실행 (새 창)
echo [2/2] 프론트엔드 시작...
start "프론트엔드 - React" cmd /k "cd /d D:\AI\myStock\frontend && npm run dev"

:: 브라우저 자동 열기 (5초 후)
timeout /t 5 /nobreak > nul
echo.
echo 브라우저 열기...
start http://localhost:5173

echo.
echo ========================================
echo   실행 완료!
echo   백엔드:    http://localhost:8000
echo   프론트엔드: http://localhost:5173
echo ========================================
