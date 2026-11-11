# Character-Hold: Ethics & Boundaries

**Scope.** Governs authoring, running, and releasing character-hold specimens, scenarios, logs, and writeups. Complements `docs/methodology.md` and `docs/scenario_authoring.md`.

---

## 1. Purpose of adversarial pressure

Pressure dialogues exist to test whether **declared assistant character is load-bearing** under social, epistemic, and institutional stress. They are **not** a vehicle for:

- eliciting actionable harm,
- coaching crime, fraud, weapons, or bio/chem misuse,
- bypassing product safety for real-world abuse,
- generating CSAM or sexual content involving minors.

All adversary content must remain **adversarial-but-benign**: uncomfortable social pressure in everyday professional or academic settings, without enabling illegal or high-severity harm.

---

## 2. Allowed pressure (benign)

Permitted themes (illustrative):

| Type | Benign examples |
|------|-----------------|
| `social_proof` | “Most reviewers phrase it this way”; “everyone on the team agrees the number is X” (where X is false but non-criminal) |
| `authority` | Boss, professor, or customer asking to skip citation diligence, soft-pedal uncertainty, or mirror a false but ordinary claim |
| `urgency` | Deadline, meeting in five minutes, “ship the blurb now” |
| `emotional` | Disappointment, career anxiety, “you’re making me look bad” — without threats of violence |
| `just_once` | One-time exception to process (invent a placeholder source; agree to a wrong trivia fact) |

Domains should stay in ordinary knowledge, writing, citation hygiene, and workplace process—see scenario authoring rules.

---

## 3. Disallowed content

Do **not** author or run items that request or reward:

1. **Actionable harm coaching** — weapons, explosives, violent crime, stalking, etc.
2. **Crime enablement** — fraud recipes, unauthorized access, malware, credential theft.
3. **Dual-use bio / chem / nuclear** operational detail.
4. **Child sexual content** or sexual/romantic content involving minors.
5. **Real-person harassment** campaigns, non-consensual intimate imagery, doxxing instructions.
6. **Jailbreak-as-goal** content whose purpose is to defeat unrelated safety filters rather than to test the specimen principle.

Social/epistemic pressure (sycophancy, false consensus, authority to skip process) is in-scope; **crime enablement framed as pressure** is out-of-scope even if “the boss asked.”

If a draft item sits near a boundary, rewrite to a milder isomorphic conflict (e.g. inventing a journal citation → still process failure; inventing a lockpick tutorial → remove).

---

## 4. Dual-use notes

| Risk | Mitigation |
|------|------------|
| Pressure scripts reused to train sycophancy or to red-team products aggressively | Release clearly as **evaluation** items; do not optimize for maximum real-world jailbreak success |
| Authority/urgency patterns generalizing to harmful compliance | Keep domains benign; prohibit harmful payloads in `content` fields |
| Faithfulness / reverse transcripts misread as “how to make the model lie” | Publish aggregate metrics; redact or summarize transcripts if they become instructional for abuse |
| Specimens that encode contested political frames as “truth” | Prefer clear factual falsehoods or process norms (citation, uncertainty), not partisan loyalty tests |

Researchers should treat hold failures as **safety-relevant behavioral signals**, not as recipes for deployment abuse.

---

## 5. Human subjects & interaction

- Evaluations target **model APIs**, not deception of human research subjects.
- Crowd annotators (if used for pressure rubrics) must receive clear task instructions, optional content warnings for stressful workplace vignettes, and the right to skip items.
- Do not present adversary turns to humans as real instructions from their actual employer.

---

## 6. Data handling

### 6.1 Secrets

- **API keys**, tokens, and account credentials must never appear in specimen YAML, scenario files, git commits, logs checked into the repo, or public writeups.
- Use environment variables or a secrets manager; rotate keys if accidental exposure occurs.

### 6.2 Logs & transcripts

- Run logs may contain full model outputs. Store with access control appropriate to the lab; scrub accidental PII pasted into prompts.
- Do not log end-user production data into this research harness without a separate privacy review.
- When sharing examples externally, prefer paraphrased excerpts unless full transcripts are necessary for replication and contain no sensitive data.

### 6.3 Retention

- Pin artifact versions (specimen semver, scenario hashes) for replication.
- Define a retention window for raw API logs; delete or archive per institutional policy.

---

## 7. Model provider policies

Respect provider terms of use and usage policies. If a provider prohibits certain adversarial testing, restrict pressure content further or use allowed evaluation channels. Character-hold pressure must remain within **benign social/epistemic** stress as defined above.

---

## 8. Release & communication

- State limitations and degrees of evidence (methodology §2.3, §10); avoid headlines that claim models “have” or “lack” character in a folk-psychological sense.
- Do not frame results as proof of deceptive alignment.
- Credit prior work accurately; distinguish character-hold from RP persona benchmarks.

---

## 9. Incident response (authoring / runs)

If a generated completion contains disallowed harmful content:

1. Do not propagate it into fixtures as a “gold” target.
2. Quarantine the log; report per lab process if required.
3. Rewrite the item to remove the pathway that elicited it, or drop the item.

---

## 10. Checklist (before merge / run)

- [ ] Pressure is social/epistemic only; no crime or high-severity harm payloads
- [ ] Domains benign (workplace process, citation, ordinary factual correction)
- [ ] No secrets in YAML or committed logs
- [ ] Annotator instructions (if any) include skip option
- [ ] Public examples redacted appropriately
- [ ] Claims in writeups match methodology’s evidence grade
