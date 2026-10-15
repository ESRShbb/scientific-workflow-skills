param([Parameter(Mandatory=$true)][string]$Software, [string]$ScriptsDirectory)
# Read-only capability clues, not license/API acceptance. No configuration change.
$ErrorActionPreference = 'Stop'
$file = [IO.FileInfo]::new($Software)
if (-not $file.Exists) { throw 'Software executable missing.' }
$version = [Diagnostics.FileVersionInfo]::GetVersionInfo($file.FullName)
$commands = @{}
foreach ($name in @('Start-Process','Get-Process','ConvertFrom-Json','ConvertTo-Json','Get-Content','Set-Content','Remove-Item')) {
    $commands[$name] = [bool](Get-Command $name -ErrorAction SilentlyContinue)
}
@{ status='FOUND_NOT_NATIVE_READY'; software=$file.FullName; version=$version.FileVersion;
    powershell=$PSVersionTable.PSVersion.ToString(); commands=$commands;
    scripts_directory=$ScriptsDirectory; scripts_directory_exists=[IO.Directory]::Exists($ScriptsDirectory);
    licensing='UNVERIFIED'; scripting_api='UNVERIFIED'; hashing='DOTNET_SHA256' } | ConvertTo-Json -Depth 6
