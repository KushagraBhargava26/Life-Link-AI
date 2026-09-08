# scripts/close_lifelink_windows.ps1
# LifeLink AI — Targeted Console Window Termination
# Architecture Reference: ARCHITECTURE.md Section 29
# Strictly terminates ONLY LifeLink processes; never touches unrelated terminals.

$repoRoot = Split-Path -Parent $PSScriptRoot

# 1. Terminate cmd.exe processes specifically running LifeLink Logs or LifeLink Launcher
$lifelinkProcs = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -eq 'cmd.exe' -and (
        $_.CommandLine -like '*LifeLink Logs - *' -or
        $_.CommandLine -like '*LifeLink Launcher*'
    )
}

foreach ($proc in $lifelinkProcs) {
    try {
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
    } catch {}
}

# 2. Terminate tracked LifeLink launcher PID if still running
$pidFile = Join-Path $repoRoot ".lifelink_launcher.pid"
if (Test-Path $pidFile) {
    try {
        $launcherPid = (Get-Content $pidFile -Raw).Trim()
        if ($launcherPid) {
            $p = Get-CimInstance Win32_Process -Filter "ProcessId = $launcherPid" -ErrorAction SilentlyContinue
            if ($p -and ($p.CommandLine -like '*run.bat*' -or $p.CommandLine -like '*LifeLink*')) {
                Stop-Process -Id $launcherPid -Force -ErrorAction SilentlyContinue
            }
        }
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    } catch {}
}
