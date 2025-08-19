# UFRECS — Understanding the system, step by step

## 1) The big picture

UFRECS tracks **every vote** and **every paper ballot counted** in a transparent way:

* **During voting:** we record that a person came to vote (without exposing their choice).
* **After voting:** several observers (called “sources”) watch what happens and **submit** what they saw.
* **The voter themselves** can **verify** the information about them.
* **The system cross-checks** what the sources say with what the voter confirms.
  → If everything matches, the vote is considered **accepted**.
* **During the count,** we look at **each ballot one by one** (ballot No. 1, No. 2, No. 3, …): sources **propose** a result for that ballot, then a **final verdict** is recorded for that same ballot.

This way, we know **how many people voted**, **who observed what**, **what the voter validated**, and **how each ballot was decided**. Everything is **traceable** and **verifiable**.

---

## 2) The “boxes” (what each table represents)

### A. Around the person who votes

* **Voter** (Elector)  
  The voter’s identity (their official identifier and, optionally, full name).  
  *Purpose:* to know that a real person did vote, without disclosing their choice.

* **Vote** (Act of voting)  
  The fact that a voter **actually voted** in a **polling station**.  
  *Purpose:* to count turnout (who came to vote), station by station.

* **VoteProposed** (Vote proposed by observers)  
  The **information observed** by a **source** at the time of voting or just after (e.g., age bracket, gender, whether the ballot was torn).  
  *Purpose:* to multiply independent viewpoints to avoid errors and manipulation.

* **VoteVerified** (Vote verified by the voter)  
  After voting, the voter **receives** what the sources recorded about them and **can confirm** whether it’s correct.  
  *Purpose:* to give citizens verification power.

* **VoteAccepted** (Accepted vote)  
  When what the **sources** say and, if available, what the **voter confirms** match, we **validate** the vote.  
  *Purpose:* to lock in a “clean,” indisputable result for the “turnout / citizen oversight” part.

### B. Around the count (ballot by ballot)

* **VotingPaperResultProposed** (Proposed paper result)  
  For **a specific ballot** (by its **sequence number** in the station: 1, 2, 3, …) and **a given station**, each **source** indicates **which candidate/party** they saw on that ballot.  
  *Purpose:* to keep all proposals so we can compare and arbitrate.

* **VotingPaperResult** (Accepted paper result)  
  For **that same ballot** and **that same station**, the **final verdict** is recorded: to **which candidate/party** is this ballot ultimately attributed?  
  *Purpose:* to obtain a final **ballot-by-ballot** result that is fully auditable.

### C. Reference data

* **PollOffice** (Polling station)  
  The place where voting happens (name, identifier, country, region, city, district…).  
  *Purpose:* to attach every action and every ballot to a specific station.

* **CandidateParty** (Candidate/Party)  
  Who is running (candidate name, party name, identifier).  
  *Purpose:* to add up votes by candidate and by party.

* **Source** (Observer)  
  Where the information comes from: **official**, **political party**, **independent**, **unverified**…  
  *Purpose:* to know who saw what, and to measure each one’s reliability.

---

## 3) The full story — from the voter’s visit to the final result

### Step 1 — Someone comes to vote

1. The voter **arrives** at the station → we record a **Vote**.
2. **Sources** observe and submit their **VoteProposed** (profile, conditions).
3. The voter can **view this info** and **confirm** it → **VoteVerified** (optional).
4. The system **cross-checks**: if it matches (sources + voter), we create **VoteAccepted**.

> This part isn’t about the ballot choice (who voted for whom) but about the **proper conduct of the vote** and **citizen oversight**.

### Step 2 — Ballots are counted one by one

1. The boxes are opened and **each ballot** is processed in order: ballot **No. 1**, then **No. 2**, etc., **in each station**.
2. For **each ballot**, the **sources** propose a result (**VotingPaperResultProposed**): “This ballot goes to such-and-such candidate/party.”
3. **Transparent decision rules** are applied (e.g., majority of sources, priority to the official source, weightings by reliability, etc.).
4. Once decided, we **record the verdict** (**VotingPaperResult**): “Ballot No. X goes to such-and-such candidate/party.”
5. **Adding up the results** by candidate/party simply means **counting the verdicts** (one ballot = one vote).

> Result: a **clear total** by candidate, by station, by city, by region… rolling up to the national level.

---

## 4) Why it’s solid (even for a skeptic)

* **More witnesses:** several sources look at the same thing.
* **Voter empowerment:** the person can **confirm** the information about them.
* **Traceability:** we keep **all** proposals and the **final verdict** for **each ballot**.
* **Clear arbitration:** public rules decide how we settle disagreements.
* **Easy audit:** we can go back **ballot by ballot** to check what was proposed and what was retained.
* **Decoupling:** we separate **turnout** (who voted) from **counting** (who each ballot goes to) to preserve anonymity and avoid bias.

---

## 5) Real-world examples (concrete talk)

* *“I want to see if my visit was counted.”*  
  → Open the app; you’ll see that your **Vote** exists. If you **confirmed**, there is a **VoteVerified**. When everything matches, the system records **VoteAccepted**.

* *“They say some ballots were misattributed.”*  
  → Go to the ballots in question (by their **index**) and compare **what sources proposed** (VotingPaperResultProposed) with **what was retained** (VotingPaperResult). If needed, we **reassess** by applying the rules.

* *“We want the total per candidate in my city.”*  
  → **Count** the number of **VotingPaperResult** assigned to each candidate, **in the city’s stations**. Simple addition, no opacity.

---

## 6) Helpful Q&A

**Q1. How do you determine the number of voters per station?**  
**A.** We count the number of **voting actions** recorded (**Vote**) in each **station**. That’s the actual turnout.

**Q2. How do you calculate the number of women who voted over the whole election?**  
**A.** We look at **validated votes** (for example **VoteAccepted**) where **gender = female**, and **count** them. We can also filter by station, city, region…

**Q3. How do you get the final score per candidate?**  
**A.** We **sum the verdicts** **VotingPaperResult**: each verdict = **1 ballot = 1 vote** for a candidate/party. We aggregate by candidate/party.

**Q4. What if observers don’t agree on a ballot?**  
**A.** We apply **decision rules** (majority, priority to the official source, weighting by reliability…). If no rule resolves it, the ballot is **put in dispute** until a documented human decision is made.

**Q5. Can a source manipulate the results?**  
**A.** No, because **no single source** decides. All proposals remain **visible**, compared with each other and, if available, with the voter’s **VoteVerified**. Low-reliability sources are **detected** (low concordance) and **discredited**.

**Q6. What if a voter doesn’t confirm (no VoteVerified)?**  
**A.** It isn’t mandatory. We’ll still validate if the **sources** agree. The citizen’s confirmation is an **extra** safeguard, not a blocking condition.

**Q7. What if the network goes down during the count?**  
**A.** Proposals are **stored locally** and **sent** as soon as the network is back. The arbitration rules are then applied as usual.

**Q8. How do you link turnout (who voted) with counting (who each ballot goes to) without violating anonymity?**  
**A.** We link **statistically** at the **station** and **time** level, not at the individual level. We compare the **number of Votes** with the **number of ballots decided** (VotingPaperResult). We check they evolve consistently, without tying a choice to a person.

**Q9. How do you prove after the fact that the published figures are correct?**  
**A.** We can **recalculate** totals from the **verdicts per ballot** (VotingPaperResult) and **retrace** each ballot’s history (all proposals vs. the final decision). It’s **auditable**.

---

## 7) What decision-makers should remember

* **Every visit to vote** is recorded, **verifiable** by the voter, and **validated** by cross-checking (Vote, VoteProposed, VoteVerified, VoteAccepted).
* **Each ballot** in the count is processed **one by one**, with **multi-source proposals** (VotingPaperResultProposed), then a **final verdict** (VotingPaperResult).
* **Final scores** are nothing more than **the sum of verdicts** that are perfectly traceable.
* The system places **transparency** and **citizen power** at the heart of the process, while preserving **anonymity**.

---

## 8) Softwares

You can use StarUML to open the uml project ufrecs.mdj
