@echo off
setlocal enabledelayedexpansion

:: stop.bat
:: LifeLink AI — Environment Stopper Script
:: Architecture Reference: ARCHITECTURE.md Section 29

echo =======================================================================
echo         LIFELINK AI STOP
echo =======================================================================

:: Determine repository root from script directory
set "REPO_ROOT=%~dp0"
cd /d "%REPO_ROOT%"

:: Step 1 — Check Docker
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Docker is not installed. Please install Docker Desktop and try again."
    goto :error
)

docker info >nul 2>nul
if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Docker Desktop is installed but the Docker daemon is not running. Please start Docker Desktop and run stop.bat again."
    goto :error
)

:: Step 2 — Stop services
echo Stopping LifeLink AI containers...
docker compose down

if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Failed to cleanly bring down the Docker Compose stack."
    goto :error
)

title LifeLink Stopper

:: Step 3 — Close LifeLink log windows and launcher window
echo Closing LifeLink dedicated windows (Launcher, Frontend, Backend, AI Service)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%REPO_ROOT%\scripts\close_lifelink_windows.ps1"

:: Step 4 — Verify shutdown using docker inspect
powershell -NoProfile -ExecutionPolicy Bypass -Command "$items = [ordered]@{'Nginx'='lifelink-nginx'; 'Frontend'='lifelink-frontend'; 'Backend'='lifelink-backend'; 'AI Service'='lifelink-ai-service'; 'PostgreSQL'='lifelink-postgres'; 'Redis'='lifelink-redis'}; $allStopped = $true; foreach ($name in $items.Keys) { $container = $items[$name]; $running = (docker inspect --format='{{.State.Running}}' $container 2>$null); if ($running -eq 'true') { $allStopped = $false; write-host ('[FAIL] ' + $name + ' is still running.') } else { write-host ('[OK] ' + $name + ' stopped') } }; if (-not $allStopped) { exit 1 } else { exit 0 }"

if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=One or more containers failed to shut down properly."
    goto :error
)

:: Step 4 — Final screen
echo.
echo =======================================================================
echo        LIFELINK AI STOPPED
echo =======================================================================
echo.
echo All application containers have been stopped.
echo.
echo Persistent database volumes were NOT deleted.
echo.
echo To start again:
echo     Double-click run.bat
echo.
echo The command window will remain open.
echo =======================================================================
pause
exit /b 0

:: Step 5 — Error block
:error
echo.
echo =======================================================================
echo         LIFELINK AI - ERROR
echo =======================================================================
echo.
echo Operation failed.
echo.
echo Reason:
echo %ERR_REASON%
echo.
echo The command window will remain open
echo so you can inspect the problem.
echo =======================================================================
pause
exit /b 1
