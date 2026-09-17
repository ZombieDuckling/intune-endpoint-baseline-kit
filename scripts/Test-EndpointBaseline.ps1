[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$BaselinePath,

    [Parameter(Mandatory = $true)]
    [string]$ExportPath,

    [Parameter(Mandatory = $false)]
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Compare-VersionAtLeast {
    param(
        [string]$Actual,
        [string]$Expected
    )

    try {
        return ([version]$Actual -ge [version]$Expected)
    }
    catch {
        return $false
    }
}

$baseline = Get-Content -Raw -Path $BaselinePath | ConvertFrom-Json
$export = Get-Content -Raw -Path $ExportPath | ConvertFrom-Json
$settings = $export.settings
$results = @()

foreach ($control in $baseline.controls) {
    $settingName = $control.setting
    $actual = $settings.$settingName
    $operator = if ($control.PSObject.Properties.Name -contains "operator") { $control.operator } else { "equals" }

    if ($null -eq $actual) {
        $state = "fail"
        $detail = "Setting missing from export"
    }
    elseif ($operator -eq "version_at_least") {
        $state = if (Compare-VersionAtLeast -Actual ([string]$actual) -Expected ([string]$control.expected)) { "pass" } else { "fail" }
        $detail = "Actual '$actual', expected at least '$($control.expected)'"
    }
    elseif ($actual -eq $control.expected) {
        $state = "pass"
        $detail = "Actual matches expected value"
    }
    else {
        $state = "fail"
        $detail = "Actual '$actual', expected '$($control.expected)'"
    }

    $results += [pscustomobject]@{
        id = $control.id
        area = $control.area
        setting = $settingName
        severity = $control.severity
        state = $state
        detail = $detail
        remediation = $control.remediation
    }
}

$summary = [pscustomobject]@{
    baselineName = $baseline.baselineName
    checkedAt = (Get-Date).ToUniversalTime().ToString("o")
    total = $results.Count
    pass = @($results | Where-Object state -eq "pass").Count
    fail = @($results | Where-Object state -eq "fail").Count
    results = $results
}

$json = $summary | ConvertTo-Json -Depth 6
if ($OutputPath) {
    $parent = Split-Path -Parent $OutputPath
    if ($parent -and -not (Test-Path $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }
    $json | Set-Content -Path $OutputPath -Encoding UTF8
}
else {
    $json
}
