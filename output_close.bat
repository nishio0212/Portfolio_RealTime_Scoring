@echo off
setlocal

set "CURRENT_DIR=%~dp0"

REM logsフォルダ作成
if not exist "%CURRENT_DIR%logs\" mkdir "%CURRENT_DIR%logs\"

REM タイムスタンプ
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%i"

set "LOG_FILE=%CURRENT_DIR%logs\OutputClose_log_%STAMP%.log"

echo -----OutputClose START %DATE% %TIME%----- >> "%LOG_FILE%" 2>&1
echo. >> "%LOG_FILE%" 2>&1

pushd "%CURRENT_DIR%"

REM ==================================================
REM output_close.py 実行
REM ==================================================
echo [INFO] Execute output_close.py >> "%LOG_FILE%" 2>&1

REM ※Pythonのパスはあなたの環境に合わせて必要なら変更
"C:\Program Files\Python310\python.exe" "%CURRENT_DIR%output_close.py" >> "%LOG_FILE%" 2>&1
set "RC_CLOSE=%ERRORLEVEL%"

echo [INFO] output_close.py exitcode=%RC_CLOSE% >> "%LOG_FILE%" 2>&1
echo. >> "%LOG_FILE%" 2>&1

echo -----OutputClose END %DATE% %TIME%----- >> "%LOG_FILE%" 2>&1

popd

REM 失敗したら non-zero で返す
if not "%RC_CLOSE%"=="0" exit /b %RC_CLOSE%

exit /b 0
