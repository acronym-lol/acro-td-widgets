$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
[System.Environment]::SetEnvironmentVariable('ACRO_TD_WIDGETS', $ScriptDir, 'User')
$env:ACRO_TD_WIDGETS = $ScriptDir
Write-Host "ACRO_TD_WIDGETS set to $ScriptDir"
