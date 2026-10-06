@echo off
setlocal enabledelayedexpansion

:: run.bat
:: LifeLink AI — Environment Runner Script
:: Architecture Reference: ARCHITECTURE.md Section 29

title LifeLink Launcher

:: Determine repository root from script directory
set "REPO_ROOT=%~dp0"
cd /d "%REPO_ROOT%"

:: Record Launcher PID for targeted lifecycle management
powershell -NoProfile -Command "$myPid = (Get-CimInstance Win32_Process -Filter ('ProcessId = ' + $PID)).ParentProcessId; [System.IO.File]::WriteAllText('%REPO_ROOT%\.lifelink_launcher.pid', $myPid)" >nul 2>&1

:: Step 1 — Check Docker
:: Ensure Docker binary path is in PATH
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    if exist "C:\Program Files\Docker\Docker\resources\bin\docker.exe" (
        set "PATH=C:\Program Files\Docker\Docker\resources\bin;!PATH!"
    ) else if exist "%ProgramFiles%\Docker\Docker\resources\bin\docker.exe" (
        set "PATH=%ProgramFiles%\Docker\Docker\resources\bin;!PATH!"
    ) else if exist "%LocalAppData%\Docker\resources\bin\docker.exe" (
        set "PATH=%LocalAppData%\Docker\resources\bin;!PATH!"
    )
)

where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Docker is not installed. Please install Docker Desktop and try again."
    goto :error
)

docker info >nul 2>nul
if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Docker Desktop is installed but the Docker daemon is not running. Please start Docker Desktop and run run.bat again."
    goto :error
)

:: Ensure Docker CLI plugins directory has docker-compose and docker-buildx plugins
if not exist "%USERPROFILE%\.docker\cli-plugins" mkdir "%USERPROFILE%\.docker\cli-plugins" >nul 2>&1
if not exist "%USERPROFILE%\.docker\cli-plugins\docker-compose.exe" (
    if exist "C:\Program Files\Docker\Docker\resources\cli-plugins\docker-compose.exe" (
        copy /y "C:\Program Files\Docker\Docker\resources\cli-plugins\docker-compose.exe" "%USERPROFILE%\.docker\cli-plugins\docker-compose.exe" >nul 2>&1
    )
)
if not exist "%USERPROFILE%\.docker\cli-plugins\docker-buildx.exe" (
    if exist "C:\Program Files\Docker\Docker\resources\cli-plugins\docker-buildx.exe" (
        copy /y "C:\Program Files\Docker\Docker\resources\cli-plugins\docker-buildx.exe" "%USERPROFILE%\.docker\cli-plugins\docker-buildx.exe" >nul 2>&1
    )
)

:: Resolve Compose command (docker compose vs docker-compose)
set "DOCKER_COMPOSE=docker compose"
docker compose version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    where docker-compose >nul 2>nul
    if !ERRORLEVEL! equ 0 (
        set "DOCKER_COMPOSE=docker-compose"
    )
)

:: Step 2 — Check .env
if not exist ".env" (
    set "ERR_REASON=.env was not found. Please run build.bat first."
    goto :error
)

:: Step 3 — Ensure required base images exist (pull only if missing locally)
set "PULL_IMAGES=nginx:alpine redis:7-alpine postgis/postgis:15-3.3-alpine"
for %%I in (%PULL_IMAGES%) do (
    docker image inspect %%I >nul 2>nul
    if !ERRORLEVEL! neq 0 (
        echo Downloading missing image %%I ...
        docker pull %%I
        if !ERRORLEVEL! neq 0 (
            set "ERR_REASON=Failed to pull image %%I. Check your internet connection and try again."
            goto :error
        )
    )
)

:: Step 3b — Start the stack
echo Starting all containers...
%DOCKER_COMPOSE% up -d
if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Failed to start the Docker Compose stack."
    goto :error
)

:: Step 4 — Wait for services to become healthy
echo.
echo Waiting for LifeLink AI services to pass health checks...
echo This checks Postgres, Redis, AI Service, Backend, Frontend, and Nginx.

set "TIMEOUT=90"
set "INTERVAL=3"
set "ELAPSED=0"

:poll_loop
powershell -NoProfile -ExecutionPolicy Bypass -Command "$containers = @('lifelink-postgres', 'lifelink-redis', 'lifelink-ai-service', 'lifelink-backend', 'lifelink-frontend', 'lifelink-nginx'); $allHealthy = $true; foreach ($c in $containers) { $status = (docker inspect --format='{{.State.Health.Status}}' $c 2>$null); if ($status) { if ($status -ne 'healthy') { $allHealthy = $false; write-host ('Container ' + $c + ' is ' + $status + '...') } } else { $running = (docker inspect --format='{{.State.Running}}' $c 2>$null); if ($running -ne 'true') { $allHealthy = $false; write-host ('Container ' + $c + ' is stopped!') } } }; if (-not $allHealthy) { exit 1 } else { exit 0 }"

if %ERRORLEVEL% equ 0 (
    goto :services_ready
)

set /a ELAPSED+=INTERVAL
if %ELAPSED% geq %TIMEOUT% (
    goto :timeout_error
)

echo [%ELAPSED%/%TIMEOUT%s] Waiting...
powershell -NoProfile -Command "Start-Sleep %INTERVAL%" >nul 2>&1
goto :poll_loop

:timeout_error
echo.
echo =======================================================================
echo         STARTUP FAILED
echo =======================================================================
echo.
echo One or more containers failed to become healthy within %TIMEOUT% seconds.
echo Current container states:
%DOCKER_COMPOSE% ps
echo.
echo Printing recent backend logs for troubleshooting:
%DOCKER_COMPOSE% logs backend --tail 20
set "ERR_REASON=Startup failed. Inspect container health status and logs above."
goto :error

:services_ready
echo.
echo [OK] PostgreSQL
echo [OK] Redis
echo [OK] AI Service
echo [OK] Backend
echo [OK] Frontend
echo [OK] Nginx
echo.
echo All Docker container health checks passed!

:: Step 5 — Verify that the actual public frontend is reachable
echo Verifying frontend HTTP availability at http://localhost...
set "HTTP_OK=0"
for /L %%I in (1,1,15) do (
    if "!HTTP_OK!"=="0" (
        for /f %%C in ('curl.exe -s -o NUL -w "%%{http_code}" http://localhost 2^>nul') do (
            if "%%C"=="200" (
                set "HTTP_OK=1"
            )
        )
        if "!HTTP_OK!"=="0" (
            powershell -NoProfile -Command "Start-Sleep 1" >nul 2>&1
        )
    )
)

if "!HTTP_OK!"=="0" (
    set "ERR_REASON=Frontend is not reachable at http://localhost via Nginx proxy."
    goto :error
)

echo [OK] Frontend is fully reachable.

:: Step 6 — Launch browser
echo Opening browser...
start "" "http://localhost"

:: Step 7 — Launch dedicated live log windows
echo.
echo Launching dedicated application log windows...
start "LifeLink Logs - Frontend" cmd.exe /k "title LifeLink Logs - Frontend && cd /d "%REPO_ROOT%" && echo ======================================================================= && echo         LIFELINK AI - FRONTEND LOGS (NEXT.JS) && echo ======================================================================= && echo. && %DOCKER_COMPOSE% logs -f frontend"
start "LifeLink Logs - Backend" cmd.exe /k "title LifeLink Logs - Backend && cd /d "%REPO_ROOT%" && echo ======================================================================= && echo         LIFELINK AI - BACKEND LOGS (FASTAPI) && echo ======================================================================= && echo. && %DOCKER_COMPOSE% logs -f backend"
start "LifeLink Logs - AI Service" cmd.exe /k "title LifeLink Logs - AI Service && cd /d "%REPO_ROOT%" && echo ======================================================================= && echo         LIFELINK AI - AI SERVICE LOGS (FASTAPI / ML) && echo ======================================================================= && echo. && %DOCKER_COMPOSE% logs -f ai-service"

:: Step 8 — Live Stream in Main Terminal
echo.
echo =======================================================================
echo        LIFELINK AI RUNNING — LIVE STACK LOGS
echo =======================================================================
echo.
echo Frontend:
echo http://localhost
echo.
echo Browser:
echo Opened automatically.
echo.
echo Services:
echo [OK] Nginx
echo [OK] Frontend
echo [OK] Backend
echo [OK] AI Service
echo [OK] PostgreSQL
echo [OK] Redis
echo.
echo Dedicated log windows launched:
echo   - [Window 1] Frontend (Next.js)
echo   - [Window 2] Backend (FastAPI)
echo   - [Window 3] AI Service (FastAPI / ML)
echo.
echo Streaming overall stack logs below (Press Ctrl+C to detach):
echo To shut down all services and close log windows: run stop.bat
echo =======================================================================
echo.
%DOCKER_COMPOSE% logs -f --tail 20
echo.
echo =======================================================================
echo Log streaming ended or interrupted.
echo The command window will remain open.
echo To shut down all services and log windows, run stop.bat.
echo =======================================================================
pause
exit /b 0

:: Step 8 — Error block
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
