# Ultra-Fraud-Resistant Electoral Control System

UFRECS a.k.a is an electoral control system built to be ultra-resistant to fraud.

It is meant to be used against delinquant governments which doesn't hesitate
to rig elections to stay in power.


## 1. **Techniques used to rig elections**

### **A. Manipulation Before Election Day**

* **Tampering with the voter registry**: adding fake names or deleting real voters to influence turnout.
* **Unequal distribution of voter cards**: withholding or distributing cards only to supporters of the ruling party.
* **Gerrymandering** (partisan redistricting): changing voting district boundaries to benefit one party.

### **B. Manipulation During Voting**

* **Ballot stuffing**: adding extra ballots to the box by corrupt election officials.
* **Multiple voting**: the same person voting several times using different identities.
* **Voter intimidation**: presence of militias or armed forces at polling stations to influence or discourage certain voters.
* **Physical prevention of voting**: early closing of polling stations, late openings, or lack of electoral materials in targeted areas.
* **Abusive proxy voting**: illegal use of votes for absent or deceased persons.

### **C. Manipulation During Counting and Transmission**

* **Falsifying tally sheets**: altering figures when transferring results to central authorities.
* **Rigged software**: tampering with electronic voting or counting systems to favor a candidate.
* **Inflated or reduced results**: adding or removing votes during final calculation.
* **Blocking or hiding local results**: delaying announcement of certain areas to prepare a falsified “official” version.

### **D. Indirect Influence Strategies**

* **Vote buying**: distributing money, gifts, or promises in exchange for votes.
* **Disproportionate propaganda**: exclusive access to state media, smear campaigns against opponents.
* **Using state apparatus**: public resources used to promote one candidate.

---

## 2. **Practical Measures Citizens Can Take to Prevent and Monitor Elections**

### **A. Before the Election**

1. **Citizen audit of the voter registry**

   * Local committees verify that every citizen is correctly registered.
   * Public reporting of anomalies (fake names, missing voters, duplicates).
2. **Training election observers**

   * Volunteers trained on official voting and counting procedures.
   * Collaboration with NGOs and international observers.

### **B. On Election Day**

1. **Mass presence of independent observers**

   * Independent monitors in each polling station.
   * Video recording or live monitoring (where legally possible).
2. **Transparency in the process**

   * Public display of voter lists at the entrance.
   * Counting ballots in front of witnesses.
3. **Real-time incident reporting**

   * Secure apps to report irregularities (photos, videos, testimonies).

### **C. After the Vote**

1. **Verification of tally sheets**

   * Each polling station publicly posts its results before transmission.
   * Comparison of local copies with official announced results.
2. **Citizen-based result centralization**

   * Collaborative platforms for publishing and comparing observer-collected results.
3. **Protection against digital tampering**

   * Independent audits of counting software and secure storage of data.

### **D. Public & Legal Pressure**

* Civil society mobilization to demand full, detailed results by polling station.
* Legal action and media exposure when documented fraud is found.

## 3. **Which points UFRECS solve?**

UFRECS solve the methods used during the elections day and after.

### **B. On Election Day**

1. **Mass presence of independent observers**

The citizens are confident on the control app and they are certain they can use it
without infriging the law.

2. **Transparency in the process**

The reporters can publicly take account of their observation.
The app and the backend code sources are open source and can be checked.
Many people can report for the same vote's office. Thus increasing the transparency.

3. **Real-time incident reporting**

The app reports the deballing in real time. The voting process can also be livestreamed.
The couting of voting happens in real time so the confidence of the voters increase.

### **C. After the Vote**

Because the couting was in real time, at the end of the couting the results are known.
The different reports can be compared by voting office in case of discrepancies.
Those people who are in zones with no network to live-sync the counting can
move rapidly to zone covered by a network a let the sync happen.

All these videos, audios and reports can be presented as proof in case
any wrong results are presented.

## 4. **How it works?**


### A. General Overview of the UFRECS System

The **UFRECS** system (U-F-R-E-C-S) is based on three main applications:

1. **A back-end application**
2. **A mobile application for reporters**
3. **A mobile application for citizens**

These three components interact to enable accurate, real-time or deferred monitoring of voting and counting operations in each polling station.

---

### B. Back-End Application

The **back-end** is designed to handle extremely high loads, capable of supporting **over 100 million simultaneous users**.
It uses **event messaging** technologies to quickly distribute updates to connected clients.

Example of technology used: **RabbitMQ**, which sends events to the various client applications.

---

### C. Mobile Application for Reporters

The reporter application is designed to be simple and intuitive, offering two main modes:

* **"Ongoing Vote" Mode**

  * Displays a button **"A person has entered"** which triggers the capture of a photo of the citizen entering **the voting booth**.
  * This button then changes into two options:

    * **"The person has exited"**
    * **"The person has exited and has torn"** (referring to the ballot)
  * Additional options allow specifying gender (male/female) and age group (youth/adult/elderly).
  * Once confirmed, the information is sent to the back-end to update the voter count.

* **"Vote Counting" Mode**

  * Initial setup: choose the source of truth (audio or video).
  * In audio mode: records an audio track of the count.
  * In video mode: records a video of the counting process.
  * The interface displays buttons corresponding to each **party** and **candidate**. Each click records a vote, sent immediately or stored for later if no network is available.
  * This feature enables **real-time** or **delayed but accurate** counting.
  * Multiple reporters can cover the same polling station, allowing **cross-checking of reports**.

---

### D. Mobile Application for Citizens

The citizen application offers two main options:

* **Global Monitoring**: view the real-time progress of votes nationwide.
* **Local Monitoring**: select a specific polling station and follow its updates.

It also allows a voter to **verify that their vote has been counted**. When leaving the polling station, the reporter marks them as "exited," which sends an event to the back-end and immediately updates the citizen’s application (with gender and age statistics).

---

### E. Overall Functioning

1. Reporters record entries/exits and the vote counting via their application.
2. Data is sent to the back-end, which broadcasts it to citizens and other connected systems.
3. Citizens can check the evolution of results in real time or afterwards.
4. The system is designed for **scalability**, **resilience to network outages**, and **transparency** in the electoral process.




## 5. **Roadmap**

[] Decide how it will work
