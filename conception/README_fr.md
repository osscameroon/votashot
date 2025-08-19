# UFRECS — Comprendre le système, étape par étape

## 1) L’idée générale

UFRECS suit **chaque vote** et **chaque bulletin dépouillé** de manière transparente :

* **Pendant le vote** : on enregistre le passage d’une personne qui vote (sans exposer son choix).
* **Après le vote** : plusieurs observateurs (appelés « sources ») regardent ce qui se passe et **proposent** ce qu’ils ont vu.
* **Le votant lui-même** peut **vérifier** les informations le concernant.
* **Le système croise** ce que disent les sources et ce que confirme le votant.
  → Si tout concorde, on considère le vote **accepté**.
* **Au dépouillement**, on regarde **chaque bulletin un par un** (bulletin n°1, n°2, n°3, …) : des sources **proposent** un résultat pour ce bulletin, puis un **verdict final** est enregistré pour ce même bulletin.

Ainsi, on sait **combien de personnes ont voté**, **qui a observé quoi**, **ce que l’électeur a validé**, et **comment chaque bulletin a été décidé**. Tout est **traçable** et **vérifiable**.

---

## 2) Les « boîtes » (ce que chaque table représente)

### A. Autour de la personne qui vote

* **Voter** (Électeur)
  Identité de l’électeur (son identifiant officiel et, éventuellement, son nom complet).
  *But :* savoir qu’une personne réelle a bien voté, sans divulguer son choix.

* **Vote** (Action de voter)
  Le fait qu’un électeur a **effectivement voté** dans un **bureau de vote**.
  *But :* comptabiliser la fréquentation (qui est passé voter), bureau par bureau.

* **VoteProposed** (Vote proposé par des observateurs)
  Les **informations observées** par une **source** au moment du vote ou juste après (ex. tranche d’âge, genre, bulletin déchiré ou non).
  *But :* multiplier les regards indépendants pour éviter les erreurs et les manipulations.

* **VoteVerified** (Vote vérifié par le votant)
  Après avoir voté, l’électeur **reçoit** ce que les sources ont enregistré à son sujet et **peut confirmer** si c’est correct.
  *But :* donner au citoyen un pouvoir de vérification.

* **VoteAccepted** (Vote accepté)
  Quand ce que disent les **sources** et, si disponible, ce que **confirme l’électeur** concordent, on **valide** le vote.
  *But :* figer un résultat « propre » et incontestable pour la partie « fréquentation / contrôle citoyen ».

### B. Autour du dépouillement (bulletin par bulletin)

* **VotingPaperResultProposed** (Proposition de résultat papier)
  Pour **un bulletin précis** (par son **numéro d’ordre** dans le bureau : 1, 2, 3, …) et **un bureau donné**, chaque **source** indique **quel candidat/parti** elle a vu sur ce bulletin.
  *But :* garder toutes les propositions, pour pouvoir comparer et arbitrer.

* **VotingPaperResult** (Résultat papier accepté)
  Pour **ce même bulletin** et **ce même bureau**, le **verdict final** est enregistré : à **quel candidat/parti** ce bulletin est-il finalement attribué ?
  *But :* obtenir un résultat final **bulletin par bulletin**, totalement auditables.

### C. Référentiels

* **PollOffice** (Bureau de vote)
  Lieu du vote (nom, identifiant, pays, région, ville, district…).
  *But :* rattacher chaque action et chaque bulletin à un bureau précis.

* **CandidateParty** (Candidat/Parti)
  Qui se présente (nom du candidat, nom du parti, identifiant).
  *But :* pouvoir additionner les voix par candidat et par parti.

* **Source** (Observateur)
  D’où vient l’information : **officielle**, **parti politique**, **indépendante**, **non vérifiée**…
  *But :* savoir qui a vu quoi, et mesurer la fiabilité de chacun.

---

## 3) Le film complet — du passage de l’électeur au résultat final

### Étape 1 — Quelqu’un vient voter

1. L’électeur **arrive** au bureau → on enregistre un **Vote**.
2. Des **sources** observent et déposent leurs **VoteProposed** (profil, conditions).
3. L’électeur peut **voir ces infos** et **confirmer** → **VoteVerified** (facultatif).
4. Le système **recoupe** : si ça concorde (sources + électeur), on crée **VoteAccepted**.

> Cette partie ne concerne pas le choix du bulletin (qui a voté pour qui), mais **la bonne tenue du vote** et le **contrôle citoyen**.

### Étape 2 — On dépouille les bulletins, un par un

1. On ouvre les urnes et on traite **chaque bulletin** dans l’ordre : bulletin **n°1**, puis **n°2**, etc., **dans chaque bureau**.
2. Pour **chaque bulletin**, les **sources** proposent un résultat (**VotingPaperResultProposed**) : « Ce bulletin va à tel candidat/parti ».
3. On applique des **règles de décision** transparentes (ex. majorité des sources, priorité à la source officielle, pondérations par fiabilité, etc.).
4. Quand c’est tranché, on **enregistre le verdict** (**VotingPaperResult**) : « Le bulletin n°X va à tel candidat/parti ».
5. **Additionner les résultats** par candidat/parti revient simplement à **compter les verdicts** (un bulletin = une voix).

> Résultat : un **total clair** par candidat, par bureau, par ville, par région… en remontant jusqu’au national.

---

## 4) Pourquoi c’est solide (même pour un sceptique)

* **Multiplication des témoins** : plusieurs sources regardent la même chose.
* **Pouvoir de l’électeur** : la personne peut **confirmer** les infos qui la concernent.
* **Traçabilité** : on garde **toutes** les propositions et le **verdict final** pour **chaque bulletin**.
* **Arbitrage clair** : des règles publiques décident comment on tranche quand il y a désaccord.
* **Audit facile** : on peut revenir **bulletin par bulletin** pour vérifier ce qui a été proposé et retenu.
* **Découplage** : on sépare **la fréquentation** (qui a voté) du **dépouillement** (à qui va chaque bulletin) pour préserver l’anonymat et éviter les biais.

---

## 5) Exemples vécus (parler concret)

* *« Je veux voir si mon passage a été compté »*
  → Ouvrez l’application, vous voyez que votre **Vote** existe. Si vous avez **confirmé**, il y a un **VoteVerified**. Quand tout concorde, le système inscrit **VoteAccepted**.

* *« On dit que des bulletins ont été mal attribués »*
  → On va sur les bulletins concernés (par leur **index**) et on compare **ce qu’ont proposé les sources** (VotingPaperResultProposed) et **ce qui a été retenu** (VotingPaperResult). Si besoin, on **rejuge** en appliquant les règles.

* *« On veut le total par candidat dans ma ville »*
  → On **compte** le nombre de **VotingPaperResult** attribués à chaque candidat, **dans les bureaux de la ville**. Simple addition, pas d’opacité.

---

## 6) Questions / Réponses utiles

**Q1. Comment déterminez-vous le nombre de votants par bureau ?**
**R.** On compte le nombre d’**actions de vote** enregistrées (**Vote**) dans chaque **bureau**. C’est la fréquentation réelle.

**Q2. Comment calculez-vous le nombre de femmes ayant voté pendant toute l’élection ?**
**R.** On regarde les **votes validés** (par exemple **VoteAccepted**) où le **genre = femme**, et on **compte**. On peut aussi filtrer par bureau, ville, région…

**Q3. Comment obtenez-vous le score final par candidat ?**
**R.** On **additionne les verdicts** **VotingPaperResult** : chaque verdict = **1 bulletin = 1 voix** pour un candidat/parti. On agrège par candidat/parti.

**Q4. Et si les observateurs ne sont pas d’accord sur un bulletin ?**
**R.** On applique des **règles de décision** (majorité, priorité à la source officielle, pondération par fiabilité…). Si aucune règle ne permet de trancher, le bulletin est **mis en litige** jusqu’à décision humaine documentée.

**Q5. Une source peut-elle manipuler les résultats ?**
**R.** Non, car **aucune source seule** ne décide. Toutes les propositions restent **visibles**, comparées entre elles et, si disponible, au **VoteVerified** du votant. Les sources peu fiables sont **détectées** (faible concordance) et **décrédibilisées**.

**Q6. Que se passe-t-il si un électeur ne confirme pas (pas de VoteVerified) ?**
**R.** Ce n’est pas obligatoire. On validera quand même si les **sources** concordent. La confirmation du citoyen est un **plus** de sécurité, pas une condition bloquante.

**Q7. Et si le réseau tombe pendant le dépouillement ?**
**R.** Les propositions sont **stockées localement** et **envoyées** dès que le réseau revient. Les règles d’arbitrage s’appliquent ensuite, comme d’habitude.

**Q8. Comment relier la fréquentation (qui a voté) au dépouillement (à qui va chaque bulletin) sans violer l’anonymat ?**
**R.** On relie **statistiquement** au **niveau du bureau** et du **temps**, pas au niveau individuel. On compare le **nombre de Votes** et le **nombre de bulletins tranchés** (VotingPaperResult). On contrôle qu’ils évoluent de manière cohérente, sans associer un choix à une personne.

**Q9. Comment prouver après coup que les chiffres publiés sont justes ?**
**R.** On peut **recalculer** les totaux à partir des **verdicts par bulletin** (VotingPaperResult) et **retracer** l’historique de chaque bulletin (toutes les propositions vs la décision finale). C’est **auditable**.

---

## 7) Ce que les décideurs doivent retenir

* **Chaque passage au vote** est enregistré, **vérifiable** par l’électeur, et **validé** par croisement (Vote, VoteProposed, VoteVerified, VoteAccepted).
* **Chaque bulletin** du dépouillement est traité **un par un**, avec des **propositions multi-sources** (VotingPaperResultProposed), puis un **verdict final** (VotingPaperResult).
* Les **scores finaux** ne sont rien d’autre que **la somme de verdicts** parfaitement traçables.
* Le système met la **transparence** et le **pouvoir citoyen** au cœur du processus, tout en préservant l’**anonymat**.

---


## 8) Logiciels

Vous pouvez utiliser le logiciel StarUML pour ouvrir le projet uml ufrecs.mdj