from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, Optional, Tuple

from core.enums import Age, Gender
from core.models import Vote, VoteProposed, VoteVerified

Weight = float


def _choose_value(
    proposed_values: Iterable[Any],
    verified_value: Optional[Any],
    *,
    use_undecided_on_tie: bool = False,
    undecided_value: Optional[Any] = None,
) -> Tuple[Any, Dict[str, Any]]:
    """Choose a field value using weighted rules.

    - Each proposed value counts as 1.0
    - Verified value (if present) counts as 1.5
    - If tie and use_undecided_on_tie: return undecided_value
    - Else if tie and verified is among max candidates: return verified
    - Else deterministic: smallest by string representation
    Returns the chosen value and a details dict (weights, candidates, reason).
    """
    weights: Dict[Any, Weight] = defaultdict(float)
    for val in proposed_values:
        weights[val] += 1.0
    if verified_value is not None:
        weights[verified_value] += 1.5

    details: Dict[str, Any] = {
        "weights": dict(weights),
        "verified_value": verified_value,
        "candidates": [],
        "reason": "",
    }

    if not weights:
        details["reason"] = "no_data"
        return verified_value, details

    max_weight = max(weights.values())
    candidates = [k for k, w in weights.items() if w == max_weight]
    details["candidates"] = candidates

    if len(candidates) > 1 and use_undecided_on_tie and undecided_value is not None:
        details["reason"] = "tie_undecided"
        chosen = undecided_value
    elif verified_value in candidates and len(candidates) > 1:
        details["reason"] = "tie_verified_preferred"
        chosen = verified_value
    else:
        # Single winner or deterministic tie-break
        if len(candidates) == 1:
            details["reason"] = "single_max"
        else:
            details["reason"] = "tie_deterministic"
        chosen = sorted(candidates, key=lambda x: str(x))[0]

    details["chosen"] = chosen
    return chosen, details


def compute_vote_decision(
    vote: Vote, *, include_details: bool = False
) -> Tuple[Optional[Tuple[str, str, bool]], Optional[Dict[str, Dict[str, Any]]]]:
    """Compute the (gender, age, has_torn) decision for a Vote.

    Returns (result, details) where result is a tuple or None if undecidable.
    Details (if requested) is a dict per field containing weights, candidates, chosen, reason.
    """
    proposed_qs: Iterable[VoteProposed] = list(vote.proposed_votes.all())
    verified: Optional[VoteVerified] = getattr(vote, "voteverified", None)

    if not proposed_qs and not verified:
        return None, None

    gender, gender_details = _choose_value(
        (p.gender for p in proposed_qs),
        verified.gender if verified else None,
        use_undecided_on_tie=True,
        undecided_value=Gender.UNDECIDED,
    )
    age, age_details = _choose_value(
        (p.age for p in proposed_qs),
        verified.age if verified else None,
        use_undecided_on_tie=True,
        undecided_value=Age.UNDECIDED,
    )
    has_torn, torn_details = _choose_value(
        (p.has_torn for p in proposed_qs),
        verified.has_torn if verified else None,
        use_undecided_on_tie=False,
    )

    if isinstance(gender, str) and gender not in Gender.values():
        raise ValueError(f"Invalid gender decided: {gender}")
    if isinstance(age, str) and age not in Age.values():
        raise ValueError(f"Invalid age decided: {age}")
    if not isinstance(has_torn, bool):
        has_torn = bool(has_torn)

    result = (gender, age, has_torn)
    if not include_details:
        return result, None

    return result, {
        "gender": gender_details,
        "age": age_details,
        "has_torn": torn_details,
        "counts": {
            "proposed": len(list(proposed_qs)),
            "verified": 1 if verified else 0,
        },
    }
