from __future__ import annotations

import json
import time
from collections import defaultdict
from typing import Any, Dict, Iterable, Optional, Tuple
from django.conf import settings
import boto3

from core.enums import Age, Gender
from core.models import (
    Vote,
    VoteProposed,
    VoteVerified,
    VotingPaperResult,
    VotingPaperResultProposed, CandidateParty,
)

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


def compute_voting_paper_result_decision(
    vp_result: VotingPaperResult, *, include_details: bool = False
) -> Tuple[Optional[object], Optional[Dict[str, Dict[str, Any]]]]:
    """Compute the accepted CandidateParty for a VotingPaperResult.

    Mirrors compute_vote_decision logic with weights:
    - Each proposed party counts as 1.0
    - Existing accepted party (if any) counts as 1.5 and is preferred on ties

    Returns (candidate_party, details). If undecidable (no data), returns (None, None).
    Details (if requested) contains weights, candidates, chosen (by identifier), reason, and counts.
    """
    # Collect proposed choices and current acceptance (if any)
    proposed_qs: Iterable[VotingPaperResultProposed] = list(
        vp_result.proposed_vp_results.all()
    )

    if not proposed_qs:
        return None, None

    undecided_party = CandidateParty.objects.get(identifier="**undecided**")

    # Build mapping from candidate IDs to objects and identifiers for consistent details
    id_to_obj: Dict[int, Any] = {}
    id_to_identifier: Dict[int, str] = {}
    for p in proposed_qs:
        if p.party_candidate_id is not None and p.party_candidate_id not in id_to_obj:
            id_to_obj[p.party_candidate_id] = p.party_candidate
            id_to_identifier[p.party_candidate_id] = p.party_candidate.identifier

    proposed_values = (p.party_candidate_id for p in proposed_qs)

    chosen_id, raw_details = _choose_value(
        proposed_values,
        None,
        use_undecided_on_tie=True,
        undecided_value="undecided",
    )

    # Map chosen ID back to CandidateParty object when possible
    chosen_party = id_to_obj.get(chosen_id) if chosen_id != "undecided" else undecided_party

    if not include_details:
        return chosen_party, None

    # Convert internal numeric-keyed details to identifier-based for readability
    weights_ident = {
        id_to_identifier.get(k, str(k)): v for k, v in raw_details.get("weights", {}).items()
    }
    candidates_ident = [
        id_to_identifier.get(k, str(k)) for k in raw_details.get("candidates", [])
    ]
    chosen_ident = id_to_identifier.get(raw_details.get("chosen"), str(raw_details.get("chosen")))

    details = {
        "party": {
            "weights": weights_ident,
            "candidates": candidates_ident,
            "reason": raw_details.get("reason"),
            "chosen": chosen_ident,
        },
        "counts": {
            "proposed": len(list(proposed_qs)),
            # Keep key name aligned with compute_vote_decision semantics
        },
    }

    return chosen_party, details


def issue_scoped_creds(poll_office_id:str, user_id:str):
    # Validate env
    missing = [k for k, v in {
        "S3_BUCKET": settings.AWS_STORAGE_BUCKET_NAME,
        "STS_UPLOAD_ROLE_ARN": settings.AWS_S3_STS_ROLE_ARN,
        "S3_STS_ENDPOINT": settings.AWS_S3_STS_ENDPOINT_URL
    }.items() if not v]
    if missing:
        raise ValueError(f"Missing env vars: {', '.join(missing)}")

    BUCKET = settings.AWS_STORAGE_BUCKET_NAME
    STS_ENDPOINT = settings.AWS_S3_STS_ENDPOINT_URL
    S3_REGION = settings.AWS_S3_REGION_NAME
    ROLE_ARN = settings.AWS_S3_STS_ROLE_ARN


    # Wasabi STS client (IMPORTANT: endpoint_url points to Wasabi STS)
    sts = boto3.client("sts", endpoint_url=STS_ENDPOINT, region_name="us-east-1",
                       aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                       aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    # Defense-in-depth: session policy restricts to EXACT office/user prefix
    session_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:PutObject", "s3:AbortMultipartUpload", "s3:ListMultipartUploadParts"],
                "Resource": f"arn:aws:s3:::{BUCKET}/{poll_office_id}/{user_id}/*"
            },
            {
                "Effect": "Allow",
                "Action": ["s3:ListBucket"],
                "Resource": f"arn:aws:s3:::{BUCKET}",
                "Condition": { "StringLike": { "s3:prefix": [f"{poll_office_id}/{user_id}/*"] } }
            }
        ]
    }

    res = sts.assume_role(
        RoleArn=ROLE_ARN,
        RoleSessionName=f"u-{user_id}-{int(time.time())}",
        DurationSeconds=43200,
        # Optional session tags (helpful if you add tag-based policies later)
        Tags=[
            {"Key": "user_id", "Value": user_id},
            {"Key": "poll_office_id", "Value": poll_office_id},
        ],
        # TransitiveTagKeys=["user_id", "poll_office_id"],
        Policy=json.dumps(session_policy),
    )
    c = res["Credentials"]
    return c
