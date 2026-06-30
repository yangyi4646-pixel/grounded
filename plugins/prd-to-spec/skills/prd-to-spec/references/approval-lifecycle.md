# Approval / Lifecycle Gate

Use this gate when a requirement touches approval, publish/release, offline, deletion, withdrawal, resubmission, callback, external processing, lifecycle state, configuration switches, version activation, or downstream consumption.

This is a generic mechanism. Do not encode project routes, enums, tokens, services, or object names here.

## Rule

For lifecycle-control work, every high-risk operation is a confirmation item until proven by PRD, user confirmation, source evidence, or explicit `N/A + reason`.

In Chinese-facing specs: `输入未提 / PRD 未写 / 待确认 / 需后续确认 / gap / 阻塞` are gap reasons, not N/A reasons. Use N/A only when the requirement explicitly does not trigger that risk, with source evidence.

Do not silently move destructive, batch, pending-editability, repeat-submit, callback, external-readonly, config-surface, or consumption-read effects to Later/V1 just because V0 would be easier.

## Required Output

Copy `templates/approval-lifecycle-gate.md` into the SPEC or gaps file.

Each row must answer:

- Is this operation/risk in scope, out of scope, or pending confirmation?
- What default is being recommended, and why is it only a default?
- What source supports the row: PRD, user confirmation, source recon, evidence profile, or model inference?
- Which SPEC unit is blocked if the row is unresolved?

## Required Risk Rows

| Risk row | Why it exists |
| --- | --- |
| Destructive operations | Delete/offline/archive often carry the business risk that approval is meant to control. |
| Batch/bulk operations | Batch flows often bypass single-item UI guards and need explicit inclusion/exclusion. |
| Pending editability / repeat submit | Locking, allowing parallel edits, and duplicate submissions are product contracts, not engineering defaults. |
| Withdraw / resubmit | These define whether rejection and cancellation recover cleanly. |
| Callback / external handling | Third-party or backend callbacks decide who can act and where truth lives. |
| Config surface | Switches, modes, approver rules, and external endpoints are separate product surfaces. |
| Version / consumption read | Pending or rejected versions must not silently change what downstream users consume. |

## Mechanical Check

Run:

```bash
python3 <skill>/scripts/check_approval_lifecycle_gate.py <SPEC-or-gaps.md>
```

The script checks that triggered documents contain the gate, required columns, and the generic risk rows. It does not decide business correctness.
