param(
    [Parameter(Mandatory=$true)][string]$JobDirectory,
    [Parameter(Mandatory=$true)][string]$Software,
    [Parameter(Mandatory=$true)][string]$ScriptsDirectory,
    [int]$TimeoutSeconds = 180,
    [string]$Python = 'py'
)
$ErrorActionPreference = 'Stop'
function Get-Sha256([string]$Path) {
    $stream = [IO.File]::OpenRead($Path)
    $hasher = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($hasher.ComputeHash($stream)).Replace('-', '').ToLowerInvariant() }
    finally { $stream.Dispose(); $hasher.Dispose() }
}
if ($env:OS -ne 'Windows_NT') { throw 'This runner supports Windows only.' }
if ($TimeoutSeconds -lt 1) { throw 'TimeoutSeconds must be positive.' }
if (-not (Test-Path -LiteralPath $Software -PathType Leaf)) { throw 'Software executable missing.' }
$exeName = [IO.Path]::GetFileNameWithoutExtension($Software)
if (Get-Process -Name @('MestReNova', 'Mnova', $exeName) -ErrorAction SilentlyContinue) {
    throw 'An application session is open. Save and close it before running. No process was terminated.'
}
$jobRoot = (Resolve-Path -LiteralPath $JobDirectory).Path
$manifest = Get-Content -LiteralPath (Join-Path $jobRoot 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
function Set-Execution([string]$State, [string]$Detail) {
    $manifest.native_execution = $State
    $manifest | Add-Member -NotePropertyName execution_detail -NotePropertyValue $Detail -Force
    $manifest | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $jobRoot 'manifest.json') -Encoding UTF8
}
if ($manifest.function -notmatch '^qNmrExport[0-9a-f]{32}$') { throw 'Invalid job function.' }
foreach ($name in @('native_report.json','native.log','success.txt','attempt.json')) {
    if (Test-Path -LiteralPath (Join-Path $jobRoot $name)) { throw 'Job already attempted. Prepare a new job directory.' }
}
foreach ($path in @($manifest.source, $manifest.working_copy)) {
    if ((Get-Sha256 $path) -ne $manifest.source_sha256) { throw 'Input hash mismatch.' }
}
if (-not (Test-Path -LiteralPath $ScriptsDirectory -PathType Container)) { throw 'Select the scripts directory recognized by this Mnova installation.' }
$pythonArgs = @()
if ([IO.Path]::GetFileNameWithoutExtension($Python) -eq 'py') { $pythonArgs = @('-3') }
& $Python @pythonArgs -B (Join-Path $PSScriptRoot 'inspect_script_startup.py') $ScriptsDirectory --output (Join-Path $jobRoot 'startup_check.json')
if ($LASTEXITCODE -ne 0) {
    Set-Execution 'BLOCKED' 'Scripts inspection detected startup effects or failed. No native launch; inspect startup_check.json. Do not change user scripts/configuration.'
    throw 'Unsafe or unresolved script startup; no native application launched.'
}
$installedScript = Join-Path (Resolve-Path -LiteralPath $ScriptsDirectory).Path ($manifest.function + '.qs')
if (Test-Path -LiteralPath $installedScript) { throw 'Script name already exists.' }
$process = $null
$created = $false
try {
    # Copy without replacing existing configuration or scripts.
    [IO.File]::Copy((Join-Path $jobRoot ($manifest.function + '.qs')), $installedScript, $false)
    $created = $true
    $attempt = @{ job_id=$manifest.job_id; started_utc=[DateTime]::UtcNow.ToString('o'); software=$Software;
        powershell_version=$PSVersionTable.PSVersion.ToString(); state='RUNNING'; process_exited=$false }
    $attempt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $jobRoot 'attempt.json') -Encoding UTF8
    Set-Execution 'RUNNING' 'Native execution started; export and visual review not verified.'
    $process = Start-Process -FilePath $Software -ArgumentList @('--sf', $manifest.function, '-w') -WindowStyle Hidden -PassThru
    $attempt.process_id = $process.Id
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    $complete = $false
    while ([DateTime]::UtcNow -lt $deadline) {
        if (Test-Path -LiteralPath (Join-Path $jobRoot 'success.txt')) {
            & $Python @pythonArgs -B (Join-Path $PSScriptRoot 'verify_export.py') $jobRoot *> (Join-Path $jobRoot 'completion_check.txt')
            if ($LASTEXITCODE -eq 0) { $complete=$true; break }
        }
        if ($process.HasExited) { break }
        Start-Sleep -Milliseconds 500
        $process.Refresh()
    }
    $attempt.export_evidence_complete = $complete
    if ($complete -and -not $process.HasExited) {
        # Only the independently launched PID, normal window close, never kill.
        $process.Refresh()
        $attempt.normal_close_requested = $process.CloseMainWindow()
        [void]$process.WaitForExit(30000)
    }
    if (-not $process.HasExited) {
        $attempt.state = 'CLEANUP_PENDING'; Set-Execution 'CLEANUP_PENDING' 'Export evidence recorded separately; own process and script retained. No retry or force termination.'
        throw 'Application still open. Inspect export evidence and finish this session before another job.'
    }
    $attempt.process_exited = $true; $attempt.exit_code = $process.ExitCode
    $attempt.finished_utc = [DateTime]::UtcNow.ToString('o')
    if ($process.ExitCode -ne 0) { throw "Native process exit code: $($process.ExitCode)" }
    foreach ($path in @($manifest.source, $manifest.working_copy)) {
        if ((Get-Sha256 $path) -ne $manifest.source_sha256) { throw 'Input changed during export.' }
    }
    $attempt.state = 'EXITED_UNVERIFIED'
    Set-Execution 'EXITED_UNVERIFIED' 'Process exited with unchanged inputs; run verify_export.py --record, then inspect every page.'
    Write-Output 'Process exited. Run verify_export.py and inspect every exported page before accepting the result.'
} catch {
    if ($manifest.native_execution -ne 'CLEANUP_PENDING') { Set-Execution 'FAILED' $_.Exception.Message }
    if ($null -ne $attempt) { $attempt.state = $manifest.native_execution; $attempt.error = $_.Exception.Message }
    throw
} finally {
    if ($null -ne $attempt) {
        $attempt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $jobRoot 'attempt.json') -Encoding UTF8
    }
    if ($created -and ($null -eq $process -or $process.HasExited)) {
        Remove-Item -LiteralPath $installedScript
    }
}
