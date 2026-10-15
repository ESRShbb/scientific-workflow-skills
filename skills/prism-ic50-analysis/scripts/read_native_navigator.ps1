param(
    [Parameter(Mandatory=$true)][string]$InputProject,
    [Parameter(Mandatory=$true)][string]$Software,
    [Parameter(Mandatory=$true)][string]$OutputDirectory,
    [string]$ResultsSection = 'Results',
    [string]$PlaceholderPattern = '^(New analysis|新的分析)',
    [int]$TimeoutSeconds = 90
)
$ErrorActionPreference='Stop'
function Get-Sha256([string]$Path) {
    $stream=[IO.File]::OpenRead($Path);$hasher=[Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($hasher.ComputeHash($stream)).Replace('-','').ToLowerInvariant() }
    finally { $stream.Dispose();$hasher.Dispose() }
}
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public static class PrismTaskWindow { [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l); }'
$source=(Resolve-Path -LiteralPath $InputProject).Path
if ([IO.Path]::GetExtension($source) -ne '.pzfx') { throw 'PZFX required' }
if (-not (Test-Path -LiteralPath $Software -PathType Leaf)) { throw 'Executable missing' }
if (Test-Path -LiteralPath $OutputDirectory) { throw 'Fresh output directory required' }
if (Get-Process -Name ([IO.Path]::GetFileNameWithoutExtension($Software)) -ErrorAction SilentlyContinue) { throw 'Close the existing Prism session first. No session was changed.' }
New-Item -ItemType Directory -Path $OutputDirectory | Out-Null
$out=(Resolve-Path -LiteralPath $OutputDirectory).Path
$work=Join-Path $out 'working.pzfx'
Copy-Item -LiteralPath $source -Destination $work
$sourceHash=Get-Sha256 $source
$proc=$null
$report=@{source=$source;source_sha256=$sourceHash;working_copy=$work;section=$ResultsSection;state='RUNNING';sheets=@()}
try {
    # This is a native GUI inspection; the navigator must be exposed to UIAutomation.
    $proc=Start-Process -FilePath $Software -ArgumentList ('"'+$work+'"') -WindowStyle Normal -PassThru
    $report.process_id=$proc.Id
    $cond=New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
    $deadline=[DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    $section=$null
    while ([DateTime]::UtcNow -lt $deadline -and $null -eq $section) {
        $windows=[System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children,$cond)
        foreach ($window in $windows) {
            if ($window.Current.ControlType -ne [System.Windows.Automation.ControlType]::Window) { continue }
            $nameCond=New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty,$ResultsSection)
            $candidates=$window.FindAll([System.Windows.Automation.TreeScope]::Descendants,$nameCond)
            foreach($candidate in $candidates) {
                if ($candidate.Current.ControlType -eq [System.Windows.Automation.ControlType]::TreeItem) { $section=$candidate; $mainWindow=$window; break }
            }
            if ($null -ne $section) { break }
        }
        if ($null -eq $section) { Start-Sleep -Milliseconds 500 }
    }
    if ($null -eq $section) { throw 'Results section not found. Specify its exact native UI title with -ResultsSection.' }
    try { $section.GetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern).Expand() } catch { }
    $children=$section.FindAll([System.Windows.Automation.TreeScope]::Children,[System.Windows.Automation.Condition]::TrueCondition)
    $raw=@();$sheets=@();$number=0
    foreach($child in $children) {
        if ($child.Current.ControlType -ne [System.Windows.Automation.ControlType]::TreeItem) { continue }
        $title=$child.Current.Name
        $raw+=@{title=$title;automation_id=$child.Current.AutomationId;placeholder=($title -match $PlaceholderPattern)}
        if ($title -match $PlaceholderPattern) { continue }
        $number++
        $sheets+=@{number=$number;expected_title=$title;verified=$true;evidence="Native UIAutomation results-section direct child $number; navigator.json"}
    }
    if ($sheets.Count -eq 0) { throw 'No results children found. Inspect section/placeholder settings, do not guess indices.' }
    $report.raw_children=$raw;$report.sheets=$sheets;$report.state='NAVIGATOR_READ'
} catch { $report.state='BLOCKED';$report.error=$_.Exception.Message }
finally {
    if ($null -ne $proc) {
        $proc.Refresh()
        if (-not $proc.HasExited) {
            if ($null -ne $mainWindow) {
                $report.normal_close_requested=[PrismTaskWindow]::PostMessage([IntPtr]$mainWindow.Current.NativeWindowHandle,0x10,[IntPtr]::Zero,[IntPtr]::Zero)
            } else { $report.normal_close_requested=$proc.CloseMainWindow() }
            [void]$proc.WaitForExit(30000)
        }
        $report.process_exited=$proc.HasExited
        if (-not $proc.HasExited) { $report.cleanup='PENDING';$report.state='PARTIAL' }
    }
    $report.source_unchanged=((Get-Sha256 $source) -eq $sourceHash)
    $report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $out 'navigator.json') -Encoding UTF8
}
$report | ConvertTo-Json -Depth 12
if ($report.state -ne 'NAVIGATOR_READ' -or -not $report.source_unchanged) { exit 2 }
