# SAMAIA — Proof Surface v0.1
**Bounded Demonstrator**

## Claim under test (fixed at this version)

> SAMAIA can refuse an action that lacks resolvable authority, and can distinguish between a condition and that same condition changed — without disclosing protected construction.

Nothing beyond what this fixed version demonstrates is claimed. This is not a description of the full SAMAIA architecture. It is a bounded, public, independently reproducible test of one specific claim.

## What this demonstrator does NOT include

- The full 16-layer meta-architecture
- Invariants beyond those required for this claim (I1, I2, I4, I9, I12)
- The internal admissible-action-space taxonomy
- Domain-specific application logic
- The protected core (Blocks 1–7)

## How to reproduce

```bash
python3 samaia_demonstrator.py
```

- No external dependencies
- No network access required
- Deterministic decision logic — fingerprints and results are stable across runs; only the timestamp field will differ

## Cases

| Case | What it tests | Expected result |
|---|---|---|
| D-001 | No resolvable authority | REFUSED at authority_resolution |
| D-002 | Valid authority + admissible action | EXECUTED |
| D-003 | Exact replay of D-002 (identical conditions) | EXECUTED + identical fingerprint |
| D-004 | Same action, changed condition | REFUSED + different fingerprint (requalification) |

## What a third party should verify

1. D-001 is refused for lack of resolvable authority.
2. D-002 is executed.
3. D-003 produces the same fingerprint and result as D-002.
4. D-004 produces a different fingerprint and is refused.

These four outcomes together constitute the proof surface for the claim above.

## Versioning policy

- This is v0.1.
- Any future change that affects the behavior covered by the claim must be published as a new version (v0.2+) — a new file or tagged release, not an in-place edit of this one.
- Previous versions and their receipts remain available for comparison.

## Status

Public proof surface only. The protected core is not included and is not required to verify the claim demonstrated here.
