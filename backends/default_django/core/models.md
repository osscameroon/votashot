# UFRECS UML — Markdown Documentation

## **Vote**

**Attributes:**

* `index: integer`
* `created_at: datetime`

**Relationships:**

* 1 → \* `VoteProposed` (proposed\_votes)
* 0..1 → 1 `VoteAccepted` (accepted)
* 0..1 → 1 `VoteVerified` (verified)
* * → 1 `PollOffice` (poll\_office)

---

## **VoteProposed**

**Attributes:**

* `gender: string`
* `age: string`
* `has_torn: boolean = False`
* `created_at: datetime`

**Relationships:**

* * → 1 `Source` (source)
* * → 1 `Vote` (vote)

---

## **VoteAccepted**

**Attributes:**

* `gender: string`
* `age: string`
* `has_torn: boolean = False`
* `created_at: datetime`

**Relationships:**

* 0..1 → 1 `Vote` (vote)

---

## **VoteVerified**

**Attributes:**

* `gender: string`
* `age: string`
* `has_torn: boolean = False`
* `created_at: datetime`

**Relationships:**

* 0..1 → 1 `Vote` (vote)
* 0..1 → 1 `Voter` (voter)

---

## **Voter**

**Attributes:**

* `elector_id: string`
* `full_name: string[0..1]`
* `created_at: datetime`

**Relationships:**

* 1 → \* `VoteVerified` (vote)

---

## **Source**

**Attributes:**

* `elector_id: string`
* `password: string`
* `type: string`
* `official_org: string[0..1]`
* `full_name: string[0..1]`
* `email: string[0..1]`
* `phone_number: string[0..1]`
* `created_at: datetime`

**Relationships:**

* 1 → \* `VoteProposed` (proposed\_votes)
* 1 → \* `VotingPaperResultProposed` (proposed\_vp\_results)
* 1 → \* `SourceToken` (source\_tokens)

---

## **SourceToken**

**Attributes:**

* `token: string {unique}`
* `s3_credentials: json[0..1]`
* `created_at: datetime`

**Relationships:**

* * → 1 `Source` (source)

---

## **VotingPaperResult**

**Attributes:**

* `index: integer`
* `created_at: datetime`

**Relationships:**

* 1 → \* `VotingPaperResultProposed` (proposed\_vp\_results)
* 1 → \* `CandidateParty` (accepted\_candidate\_party)
* * → 1 `PollOffice` (poll\_office)

---

## **VotingPaperResultProposed**

**Attributes:**

* `created_at: datetime`

**Relationships:**

* * → 1 `VotingPaperResult` (vp\_result)
* * → 1 `CandidateParty` (party\_candidate)
* * → 1 `Source` (source)

---

## **CandidateParty**

**Attributes:**

* `party_name: string`
* `candidate_name: string`
* `identifier: string`
* `created_at: datetime`

**Relationships:**

* 1 → \* `VotingPaperResult` (vp\_results)
* 1 → \* `VotingPaperResultProposed` (proposed\_in\_vp\_results)

---

## **PollOffice**

**Attributes:**

* `name: string`
* `identifier: string`
* `country: string`
* `state: string[0..1]`
* `region: string[0..1]`
* `city: string[0..1]`
* `county: string[0..1]`
* `district: string[0..1]`
* `created_at: datetime`

**Relationships:**

* 1 → \* `Vote` (votes)
* 1 → \* `VotingPaperResult` (vp\_results)
* 1 → \* `SourceToken` (source\_tokens)

---

## Some explanations

[0..1] => means the field is nullable.