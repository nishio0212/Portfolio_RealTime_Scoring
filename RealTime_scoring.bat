@echo off
setlocal

set "CURRENT_DIR=%~dp0"

REM logs フォルダ作成
if not exist "%CURRENT_DIR%logs\" mkdir "%CURRENT_DIR%logs\"

REM タイムスタンプ
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%i"

set "LOG_FILE=%CURRENT_DIR%logs\Scoreing_log_%STAMP%.log"

echo -----Scoring START %DATE% %TIME%----- >> "%LOG_FILE%" 2>&1
echo. >> "%LOG_FILE%" 2>&1

pushd "%CURRENT_DIR%"

REM ==================================================
REM main.py 実行
REM ==================================================
echo [INFO] Execute main.py >> "%LOG_FILE%" 2>&1

REM 1st arg: mode (1430/1500/1530). If empty -> 1530
set "MODE=%~1"
if "%MODE%"=="" set "MODE=1530"

echo [INFO] mode=%MODE% >> "%LOG_FILE%" 2>&1
"C:\Program Files\Python310\python.exe" "%CURRENT_DIR%main.py" %MODE% >> "%LOG_FILE%" 2>&1


set "RC_MAIN=%ERRORLEVEL%"

echo [INFO] main.py exitcode=%RC_MAIN% >> "%LOG_FILE%" 2>&1
echo. >> "%LOG_FILE%" 2>&1

echo -----Scoring END %DATE% %TIME%----- >> "%LOG_FILE%" 2>&1

REM どちらかが失敗したら non-zero で返す
if not "%RC_MAIN%"=="0" exit /b %RC_MAIN%
if not "%RC_SELECT%"=="0" exit /b %RC_SELECT%

exit /b 0
