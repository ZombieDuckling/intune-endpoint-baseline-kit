# Intune Endpoint Baseline Kit

A small, safe toolkit for reviewing Microsoft Intune endpoint configuration against a documented baseline. It uses synthetic examples and local files only, so it can be shared publicly without exposing tenant data.

## What this demonstrates

This repository maps to endpoint administration and security engineering work usually expected in a Microsoft 365 security role:

- Baseline policy review for Windows endpoints
- Configuration evidence checks using repeatable scripts
- Clear pass, warning, and fail reporting
- Safe sample data for public review
- CI validation for schemas, examples, and report output

## Repository contents

| Path | Purpose |
| --- | --- |
| `baselines/windows-endpoint-baseline.json` | Baseline controls grouped by device hardening area |
| `samples/device-configuration-export.json` | Synthetic endpoint policy export used for validation |
| `samples/compliance-export.csv` | Synthetic device compliance snapshot |
| `scripts/Test-EndpointBaseline.ps1` | Compares an exported policy file with the baseline |
| `scripts/New-ComplianceSummary.ps1` | Builds a compliance summary from a CSV export |
| `tests/test_baseline_schema.py` | Python tests for schema, sample coverage, and PowerShell syntax markers |
| `.github/workflows/validate.yml` | CI for the same checks run locally |

## Quick start

Run the Python validation suite:

```bash
python -m pytest tests
```

Run the baseline comparison in PowerShell:

```powershell
pwsh ./scripts/Test-EndpointBaseline.ps1 `
  -BaselinePath ./baselines/windows-endpoint-baseline.json `
  -ExportPath ./samples/device-configuration-export.json `
  -OutputPath ./out/baseline-report.json
```

Run the compliance summary:

```powershell
pwsh ./scripts/New-ComplianceSummary.ps1 `
  -CsvPath ./samples/compliance-export.csv `
  -OutputPath ./out/compliance-summary.json
```

## Baseline areas covered

The baseline is intentionally compact, but it covers the main areas a reviewer would expect to see:

- BitLocker state and recovery key escrow
- Local administrator control
- Firewall state across domain, private, and public profiles
- Antivirus and real-time protection settings
- Attack surface reduction configuration
- Device compliance signals for encryption, OS version, and threat state

## Using this with real exports

Do not commit tenant exports to this repository. To use the scripts in a real environment:

1. Export policy and compliance data into a private working directory.
2. Normalize field names to match the sample files.
3. Run the scripts locally.
4. Share only the generated summary after checking it for names, device IDs, user IDs, tenant IDs, and hostnames.

## VAT IT role mapping

| Role need | Evidence in this repo |
| --- | --- |
| Endpoint security administration | Baseline controls for encryption, firewall, antivirus, and compliance |
| Microsoft 365 security tooling | Intune-oriented policy review structure and PowerShell scripts |
| Automation and repeatability | Deterministic reports, CI checks, and schema validation |
| Communication with operations teams | Report output separates pass, warning, and fail items with plain remediation notes |
| Safe handling of sensitive data | Synthetic samples only, with explicit guidance for private exports |

## Safety notes

- No secrets, tenant IDs, device IDs, or user records are included.
- The sample data is synthetic.
- The scripts read local files and write reports. They do not change endpoint settings.
- The toolkit is defensive and review-focused. It does not contain exploit code or bypass logic.

## License

MIT
