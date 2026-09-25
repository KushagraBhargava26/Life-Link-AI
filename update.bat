@echo off
setlocal enabledelayedexpansion

:: update.bat
:: LifeLink AI — Updater Script
:: Pulls latest code from GitHub, rebuilds changed Docker images,
:: restarts all services, and re-seeds demo data.
:: After this, run.bat works normally with zero differences.
::
:: Architecture Reference: ARCHITECTURE.md Section 29

title LifeLink Updater

set "REPO_ROOT=%~dp0"
cd /d "%REPO_ROOT%"

echo =======================================================================
echo         LIFELINK AI - UPDATER
echo =======================================================================
echo.
echo This will:
echo   1. Pull the latest code from GitHub
echo   2. Rebuild Docker images (picks up requirements.txt / code changes)
echo   3. Restart all containers
echo   4. Re-seed demo accounts (keeps only demo data)
echo   5. Open your browser when everything is ready
echo.
echo WARNING: Any accounts or blood requests you created manually will be
echo          removed. Only the 4 official demo accounts will remain.
echo.
echo Press Ctrl+C to cancel, or...
pause

:: ---------------------------------------------------------------------------
:: Step 1 — Check Docker is running
:: ---------------------------------------------------------------------------
echo.
echo [1/6] Checking Docker Desktop...
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Docker is not installed. Please install Docker Desktop and try again."
    goto :error
)

docker info >nul 2>nul
if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Docker Desktop is not running. Please start Docker Desktop and try again."
    goto :error
)
echo [OK] Docker is running.

:: ---------------------------------------------------------------------------
:: Step 2 — Pull latest code from GitHub
:: ---------------------------------------------------------------------------
echo.
echo [2/6] Pulling latest code from GitHub...

where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [WARN] Git is not installed — skipping code update. Using local files.
    goto :skip_pull
)

git fetch origin
if %ERRORLEVEL% neq 0 (
    echo [WARN] Could not reach GitHub. Continuing with local files.
    goto :skip_pull
)

git pull origin main
if %ERRORLEVEL% neq 0 (
    echo [WARN] Git pull had conflicts or errors. Continuing with local files.
    goto :skip_pull
)

echo [OK] Latest code pulled from GitHub.
:skip_pull

:: ---------------------------------------------------------------------------
:: Step 3 — Stop all running containers (keep volumes / database intact)
:: ---------------------------------------------------------------------------
echo.
echo [3/6] Stopping existing containers...
docker compose down
if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Failed to stop existing containers."
    goto :error
)
echo [OK] Containers stopped.

:: ---------------------------------------------------------------------------
:: Step 4 — Rebuild all custom images (picks up any code / requirements changes)
:: ---------------------------------------------------------------------------
echo.
echo [4/6] Rebuilding Docker images (this may take several minutes)...
echo       This step ensures requirements.txt, Dockerfile, and code changes
echo       are fully applied to all services.
echo.

set "COMPOSE_HTTP_TIMEOUT=300"
set "DOCKER_CLIENT_TIMEOUT=300"

docker compose build --no-cache
if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Docker image rebuild failed. Check the error above for details."
    goto :error
)
echo.
echo [OK] All Docker images rebuilt successfully.

:: ---------------------------------------------------------------------------
:: Step 5 — Pull base images with retry (nginx, redis, postgis)
:: ---------------------------------------------------------------------------
echo.
echo [5/6] Pulling required base images...
set "PULL_IMAGES=nginx:alpine redis:7-alpine postgis/postgis:15-3.3-alpine"
for %%I in (%PULL_IMAGES%) do (
    set "PULL_OK=0"
    for /L %%A in (1,1,3) do (
        if "!PULL_OK!"=="0" (
            echo [Attempt %%A/3] Pulling %%I ...
            docker pull %%I
            if !ERRORLEVEL! equ 0 (
                set "PULL_OK=1"
                echo [OK] %%I pulled successfully.
            ) else (
                echo [WARN] Pull attempt %%A failed. Retrying...
            )
        )
    )
    if "!PULL_OK!"=="0" (
        echo [WARN] Could not pull %%I after 3 attempts. Will use cached version if available.
    )
)

:: ---------------------------------------------------------------------------
:: Step 5b — Start fresh stack
:: ---------------------------------------------------------------------------
echo.
echo Starting all updated containers...
docker compose up -d
if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Failed to start the Docker Compose stack after rebuild."
    goto :error
)

:: ---------------------------------------------------------------------------
:: Step 6 — Wait for all services to become healthy
:: ---------------------------------------------------------------------------
echo.
echo [6/6] Waiting for all services to pass health checks...
echo       (Postgres, Redis, AI Service, Backend, Frontend, Nginx)

set "TIMEOUT=180"
set "INTERVAL=5"
set "ELAPSED=0"

:poll_loop
powershell -NoProfile -ExecutionPolicy Bypass -Command "$containers = @('lifelink-postgres', 'lifelink-redis', 'lifelink-ai-service', 'lifelink-backend', 'lifelink-frontend', 'lifelink-nginx'); $allHealthy = $true; foreach ($c in $containers) { $status = (docker inspect --format='{{.State.Health.Status}}' $c 2>$null); if ($status) { if ($status -ne 'healthy') { $allHealthy = $false; write-host ('  Waiting: ' + $c + ' is ' + $status + '...') } } else { $running = (docker inspect --format='{{.State.Running}}' $c 2>$null); if ($running -ne 'true') { $allHealthy = $false; write-host ('  Stopped: ' + $c) } } }; if (-not $allHealthy) { exit 1 } else { exit 0 }"

if %ERRORLEVEL% equ 0 (
    goto :services_ready
)

set /a ELAPSED+=INTERVAL
if %ELAPSED% geq %TIMEOUT% (
    echo.
    echo [FAIL] Services did not become healthy within %TIMEOUT% seconds.
    docker compose ps
    set "ERR_REASON=Startup timed out. Check container logs with: docker compose logs"
    goto :error
)

echo   [%ELAPSED%/%TIMEOUT%s] Still waiting...
powershell -NoProfile -Command "Start-Sleep %INTERVAL%" >nul 2>&1
goto :poll_loop

:services_ready
echo.
echo [OK] PostgreSQL
echo [OK] Redis
echo [OK] AI Service
echo [OK] Backend
echo [OK] Frontend
echo [OK] Nginx
echo.

:: ---------------------------------------------------------------------------
:: Re-seed demo data (cleans non-demo accounts, keeps only official accounts)
:: ---------------------------------------------------------------------------
echo Resetting database to official demo state...
echo (Removes manually created accounts/requests, keeps only demo personas)
echo.
docker exec lifelink-backend python scripts/reset_to_demo.py
if %ERRORLEVEL% neq 0 (
    echo [WARN] Demo data reset had issues — check above. Continuing anyway.
)

:: ---------------------------------------------------------------------------
:: Verify frontend is reachable
:: ---------------------------------------------------------------------------
echo.
echo Verifying frontend at http://localhost...
set "HTTP_OK=0"
for /L %%I in (1,1,20) do (
    if "!HTTP_OK!"=="0" (
        for /f %%C in ('curl.exe -s -o NUL -w "%%{http_code}" http://localhost 2^>nul') do (
            if "%%C"=="200" (
                set "HTTP_OK=1"
            )
        )
        if "!HTTP_OK!"=="0" (
            powershell -NoProfile -Command "Start-Sleep 2" >nul 2>&1
        )
    )
)

if "!HTTP_OK!"=="0" (
    set "ERR_REASON=Frontend is not reachable at http://localhost. Try running run.bat."
    goto :error
)

:: ---------------------------------------------------------------------------
:: Done!
:: ---------------------------------------------------------------------------
echo.
echo =======================================================================
echo         LIFELINK AI - UPDATE COMPLETE
echo =======================================================================
echo.
echo All services are running with the latest code and fresh demo data.
echo.
echo  Demo Accounts (use at http://localhost/admin/login):
echo  +-----------------------+-----------------------------+------------------+
echo  ^| Role                  ^| Email                       ^| Password         ^|
echo  +-----------------------+-----------------------------+------------------+
echo  ^| Super Admin           ^| admin@lifelink.ai           ^| Admin@12345      ^|
echo  ^| Hospital Admin        ^| hospital.admin@apollo.org   ^| Hospital@12345   ^|
echo  ^| Blood Bank Manager    ^| bloodbank.manager@redcross.org ^| BloodBank@12345^|
echo  ^| Donor (Priya Verma)   ^| priya.verma@gmail.com       ^| Priya@12345      ^|
echo  +-----------------------+-----------------------------+------------------+
echo.
echo Opening browser...
start "" "http://localhost"

echo.
echo =======================================================================
pause
exit /b 0

:error
echo.
echo =======================================================================
echo         LIFELINK AI - UPDATE ERROR
echo =======================================================================
echo.
echo Operation failed.
echo.
echo Reason:
echo %ERR_REASON%
echo.
echo The command window will remain open so you can inspect the problem.
echo =======================================================================
pause
exit /b 1
