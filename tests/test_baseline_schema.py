import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "baselines" / "windows-endpoint-baseline.json"
EXPORT = ROOT / "samples" / "device-configuration-export.json"
COMPLIANCE = ROOT / "samples" / "compliance-export.csv"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_baseline_controls_have_required_fields():
    data = load_json(BASELINE)
    assert data["schemaVersion"] == "1.0"
    controls = data["controls"]
    assert len(controls) >= 8
    seen = set()
    for control in controls:
        assert re.fullmatch(r"WIN-[A-Z]{2,3}-\d{3}", control["id"])
        assert control["id"] not in seen
        seen.add(control["id"])
        assert control["area"]
        assert control["setting"]
        assert "expected" in control
        assert control["severity"] in {"low", "medium", "high"}
        assert len(control["remediation"]) > 20


def test_sample_export_covers_every_baseline_setting():
    baseline = load_json(BASELINE)
    export = load_json(EXPORT)
    settings = export["settings"]
    missing = [c["setting"] for c in baseline["controls"] if c["setting"] not in settings]
    assert missing == []


def test_sample_export_contains_expected_mixed_results():
    export = load_json(EXPORT)["settings"]
    assert export["firewallPublicEnabled"] is False
    assert export["cloudProtectionEnabled"] is False
    assert export["bitLockerEnabled"] is True


def test_compliance_sample_uses_synthetic_users():
    with COMPLIANCE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 4
    assert all(row["PrimaryUser"].endswith("@example.invalid") for row in rows)
    assert any(row["ComplianceState"] == "NonCompliant" for row in rows)


def test_no_public_docs_claim_real_tenant_data():
    checked_suffixes = {".md", ".json", ".csv", ".ps1", ".yml"}
    text = "\n".join(
        p.read_text(encoding="utf-8")
        for p in ROOT.rglob("*")
        if p.is_file() and ".git" not in p.parts and p.suffix in checked_suffixes and "tests" not in p.parts
    )
    banned = [
        "tenant.onmicrosoft.com",
        "client" + " secret",
        "production" + " tenant",
        "customer" + " tenant",
    ]
    lower = text.lower()
    assert all(term not in lower for term in banned)


def test_powershell_scripts_have_strict_mode_and_no_write_operations():
    for script in (ROOT / "scripts").glob("*.ps1"):
        text = script.read_text(encoding="utf-8")
        assert "Set-StrictMode -Version Latest" in text
        assert "Invoke-RestMethod" not in text
        assert "Set-Intune" not in text
        assert "New-Intune" not in text
