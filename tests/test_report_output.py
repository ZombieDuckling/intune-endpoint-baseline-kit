import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PWSH = shutil.which("pwsh") or ""

pytestmark = pytest.mark.skipif(not PWSH, reason="PowerShell 7 (pwsh) is required for report output checks")


def run_powershell_script(script: str, *args: str) -> dict:
    completed = subprocess.run(
        [PWSH, str(ROOT / "scripts" / script), *args],
        check=True,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_endpoint_baseline_report_matches_sample_findings():
    report = run_powershell_script(
        "Test-EndpointBaseline.ps1",
        "-BaselinePath",
        str(ROOT / "baselines" / "windows-endpoint-baseline.json"),
        "-ExportPath",
        str(ROOT / "samples" / "device-configuration-export.json"),
    )

    assert report["baselineName"] == "Windows endpoint security baseline"
    assert report["total"] == 10
    assert report["pass"] == 7
    assert report["fail"] == 3

    failing_ids = {item["id"] for item in report["results"] if item["state"] == "fail"}
    assert failing_ids == {"WIN-FW-003", "WIN-AV-002", "WIN-CMP-001"}
    assert {item["state"] for item in report["results"]} <= {"pass", "fail"}
    assert all(item["remediation"] for item in report["results"])


def test_compliance_summary_matches_sample_findings():
    summary = run_powershell_script(
        "New-ComplianceSummary.ps1",
        "-CsvPath",
        str(ROOT / "samples" / "compliance-export.csv"),
    )

    assert summary["totalDevices"] == 4
    assert summary["compliant"] == 2
    assert summary["nonCompliant"] == 1
    assert summary["gracePeriod"] == 1
    assert summary["encrypted"] == 3
    assert summary["threatActive"] == 1

    review_devices = {device["DeviceName"] for device in summary["devicesNeedingReview"]}
    assert review_devices == {"LAPTOP-002", "LAPTOP-004"}
