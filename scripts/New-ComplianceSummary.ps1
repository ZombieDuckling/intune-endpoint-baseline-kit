[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$CsvPath,

    [Parameter(Mandatory = $false)]
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$rows = Import-Csv -Path $CsvPath
$summary = [pscustomobject]@{
    checkedAt = (Get-Date).ToUniversalTime().ToString("o")
    totalDevices = @($rows).Count
    compliant = @($rows | Where-Object ComplianceState -eq "Compliant").Count
    nonCompliant = @($rows | Where-Object ComplianceState -eq "NonCompliant").Count
    gracePeriod = @($rows | Where-Object ComplianceState -eq "InGracePeriod").Count
    encrypted = @($rows | Where-Object EncryptionState -eq "Encrypted").Count
    threatActive = @($rows | Where-Object ThreatState -eq "Active").Count
    devicesNeedingReview = @(
        $rows |
            Where-Object { $_.ComplianceState -ne "Compliant" -or $_.ThreatState -ne "Clear" } |
            Select-Object DeviceName, ComplianceState, EncryptionState, OsVersion, ThreatState
    )
}

$json = $summary | ConvertTo-Json -Depth 5
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
