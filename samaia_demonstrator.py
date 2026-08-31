"""
SAMAIA — Minimal Bounded Demonstrator (Proof Surface v0.1)
============================================================

CLAIM UNDER TEST (declared, public, fixed):
"SAMAIA can refuse an action that lacks resolvable authority, and can
distinguish between a condition and that same condition changed --
without disclosing protected construction."

This demonstrator implements ONLY the public execution-boundary
mechanics needed to test that claim. It does NOT include:
  - the full 16-layer meta-architecture
  - invariants I5-I12 beyond what's needed for this claim
  - the admissible action space taxonomy used internally
  - any domain-specific application logic

Standing attaches only to behavior demonstrated at this fixed version.
Re-run this script to reproduce every result below independently.
"""

import json
import hashlib
from datetime import datetime, timezone


# ---------------------------------------------------------------------
# Minimal Ontology (public subset)
# ---------------------------------------------------------------------

class Decision:
    def __init__(self, decision_id, origin, proposed_action, authority_claim, context):
        self.decision_id = decision_id
        self.origin = origin
        self.proposed_action = proposed_action
        self.authority_claim = authority_claim  # what authority is being asserted
        self.context = context                  # dict of conditions

    def fingerprint(self):
        """Deterministic fingerprint of the decision + its conditions."""
        payload = json.dumps(
            {"action": self.proposed_action, "context": self.context},
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


# A tiny, fixed "authority registry" -- stands in for whatever real
# authority resolution mechanism SAMAIA uses internally. Only its
# public interface (resolve/valid/invalid) is exposed here.
_AUTHORITY_REGISTRY = {
    "operator:alice": {"scope": {"deploy", "rollback"}, "valid_until": "2026-12-31"},
}


def resolve_authority(decision):
    """
    Public subset of Authority Resolution (SAMAIA Layer 4 / I1, I4).
    Returns (authority_valid: bool, reason: str)
    """
    entity = decision.authority_claim
    entry = _AUTHORITY_REGISTRY.get(entity)
    if entry is None:
        return False, f"authority_undefined:{entity}"
    if decision.proposed_action not in entry["scope"]:
        return False, f"authority_out_of_scope:{decision.proposed_action}"
    return True, "authority_resolved"


def check_admissibility(decision, admissible_space):
    """
    Public subset of Admissibility Check (I2, I3).
    admissible_space: set of allowed (action, condition_key) tuples for
    THIS bounded demonstrator only.
    """
    key = (decision.proposed_action, decision.context.get("condition"))
    if key not in admissible_space:
        return False, f"inadmissible:{key}"
    return True, "admissible"


def execute(decision, admissible_space):
    """
    Public subset of Execution Authorization (I9, I12).
    Returns a receipt -- this is the artifact that makes the claim
    testable by a third party without access to the protected core.
    """
    receipt = {
        "decision_id": decision.decision_id,
        "fingerprint": decision.fingerprint(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": decision.proposed_action,
        "context": decision.context,
    }

    auth_ok, auth_reason = resolve_authority(decision)
    receipt["authority_check"] = auth_reason
    if not auth_ok:
        receipt["result"] = "REFUSED"
        receipt["stage"] = "authority_resolution"
        return receipt

    adm_ok, adm_reason = check_admissibility(decision, admissible_space)
    receipt["admissibility_check"] = adm_reason
    if not adm_ok:
        receipt["result"] = "REFUSED"
        receipt["stage"] = "admissibility_check"
        return receipt

    receipt["result"] = "EXECUTED"
    receipt["stage"] = "action_performed"
    return receipt


# ---------------------------------------------------------------------
# Bounded scenario for this demonstrator (fixed, public, minimal)
# ---------------------------------------------------------------------

ADMISSIBLE_SPACE = {
    ("deploy", "condition_A"),
    ("rollback", "condition_A"),
    ("rollback", "condition_B"),
    # note: ("deploy", "condition_B") is deliberately NOT admissible --
    # this is the case used to demonstrate changed-condition
    # requalification below.
}


def run_case(label, decision):
    receipt = execute(decision, ADMISSIBLE_SPACE)
    print(f"\n--- CASE: {label} ---")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    return receipt


if __name__ == "__main__":
    print("SAMAIA Proof Surface v0.1 -- Bounded Demonstrator")
    print("Claim: authority refusal + condition-change requalification")
    print("=" * 60)

    # CASE 1 -- no resolvable authority (I1, I4)
    d1 = Decision(
        decision_id="D-001",
        origin="agent:unregistered_bot",
        proposed_action="deploy",
        authority_claim="operator:unknown",
        context={"condition": "condition_A"},
    )
    r1 = run_case("No resolvable authority -> expect REFUSED", d1)

    # CASE 2 -- valid authority, admissible action (baseline EXECUTED)
    d2 = Decision(
        decision_id="D-002",
        origin="agent:ci_pipeline",
        proposed_action="deploy",
        authority_claim="operator:alice",
        context={"condition": "condition_A"},
    )
    r2 = run_case("Valid authority + admissible -> expect EXECUTED", d2)

    # CASE 3 -- SAME decision, SAME conditions, re-run for replay proof
    d3 = Decision(
        decision_id="D-003",
        origin="agent:ci_pipeline",
        proposed_action="deploy",
        authority_claim="operator:alice",
        context={"condition": "condition_A"},
    )
    r3 = run_case("Replay of Case 2 under identical conditions", d3)
    assert r2["fingerprint"] == r3["fingerprint"], "fingerprints diverged unexpectedly"
    assert r2["result"] == r3["result"] == "EXECUTED", "replay did not reproduce result"
    print("\n[REPLAY CHECK] Identical conditions -> identical fingerprint & result: PASS")

    # CASE 4 -- SAME action, CHANGED condition -> must requalify differently
    d4 = Decision(
        decision_id="D-004",
        origin="agent:ci_pipeline",
        proposed_action="deploy",
        authority_claim="operator:alice",
        context={"condition": "condition_B"},  # changed condition
    )
    r4 = run_case("Same action, CHANGED condition -> expect REFUSED (requalification)", d4)
    assert r4["fingerprint"] != r2["fingerprint"], "fingerprint failed to change with condition"
    assert r4["result"] == "REFUSED", "changed condition was not re-evaluated correctly"
    print("\n[REQUALIFICATION CHECK] Changed condition -> different fingerprint, "
          "re-evaluated, REFUSED: PASS")

    print("\n" + "=" * 60)
    print("All checks passed. Full receipt log above is the proof surface")
    print("for this claim, at this fixed version, independently reproducible.")
