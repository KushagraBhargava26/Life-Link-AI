@echo off
setlocal enabledelayedexpansion

:: build.bat
:: LifeLink AI — Environment Builder Script
:: Architecture Reference: ARCHITECTURE.md Section 29 & Section 30

echo =======================================================================
echo         LIFELINK AI BUILD
echo =======================================================================

:: Determine repository root from script directory
set "REPO_ROOT=%~dp0"
cd /d "%REPO_ROOT%"

:: 1. Check prerequisites
echo Checking prerequisites...

where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Docker is not installed. Please install Docker Desktop and try again."
    goto :error
)

where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo WARNING: Git is not found in path. Git features may be limited.
)

:: 2. Check Docker daemon
docker info >nul 2>nul
if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Docker Desktop is installed but the Docker daemon is not running. Please start Docker Desktop and run build.bat again."
    goto :error
)

echo [PASS] Docker daemon is available.

:: 3. Check Compose
docker compose version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Docker Compose (v2+) is not available. Please ensure Docker Desktop is updated."
    goto :error
)

:: 4. Environment configuration (.env setup)
echo Configuring environment variables...

if exist ".env" (
    echo [SKIP] .env already exists. Preserving current configuration.
    echo [OK] Environment configuration ready.
    goto :env_ready
)

if not exist ".env.example" (
    set "ERR_REASON=.env.example does not exist in root directory."
    goto :error
)

echo Creating .env file from .env.example...
copy /y ".env.example" ".env" >nul
if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Failed to copy .env.example to .env."
    goto :error
)

REM Generate random hex secrets for local development using Python
echo Generating local development secrets...
set "SECRET_KEY="
set "AI_SERVICE_API_KEY="

for /f "delims=" %%i in ('python -c "import secrets; print(secrets.token_hex(32))" 2^>nul') do set "SECRET_KEY=%%i"
for /f "delims=" %%j in ('python -c "import secrets; print(secrets.token_hex(32))" 2^>nul') do set "AI_SERVICE_API_KEY=%%j"

if defined SECRET_KEY (
    python -c "import sys; data = open('.env').read().replace('<REPLACE_WITH_256_BIT_SECRET>', '%SECRET_KEY%').replace('<REPLACE_WITH_AI_INTERNAL_API_KEY>', '%AI_SERVICE_API_KEY%'); open('.env', 'w').write(data)" 2>nul
) else (
    echo WARNING: Python unavailable to auto-generate secrets. Default placeholders remain in .env.
)

echo [OK] Environment configuration ready.
echo.
echo =======================================================================
echo  IMPORTANT CONTEXT REQUIRED:
echo  Please open the generated .env file and configure third-party services:
echo    - Firebase Credentials: base64-encoded json
echo    - SMTP Server Credentials: for email notifications
echo    - Google Maps API Key: optional, defaults to OpenStreetMap
echo =======================================================================

:env_ready

:: 5. Validate Compose configuration
echo.
echo Validating Docker Compose configuration...
docker compose config >nul 2>&1
if %ERRORLEVEL% neq 0 (
    docker compose config
    set "ERR_REASON=Docker Compose configuration is invalid."
    goto :error
)
echo [PASS] Docker Compose configuration is valid.

:: 6. Build containers
echo.
echo Building Docker containers (this may take several minutes)...
docker compose build
if %ERRORLEVEL% neq 0 (
    set "ERR_REASON=Docker image build failed."
    goto :error
)

:: 7. Success Block
echo.
echo =======================================================================
echo        BUILD COMPLETED SUCCESSFULLY
echo =======================================================================
echo.
echo Docker images have been built.
echo.
echo Next step:
echo     Double-click run.bat
echo.
echo The command window will remain open.
echo =======================================================================
pause
exit /b 0

:: 8. Error Block
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
