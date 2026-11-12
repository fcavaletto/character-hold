# Related work (short comparative note)

**character-hold** measures whether a *declared assistant character* (system-prompt principles) is load-bearing under conflict—not whether a fictional persona stays in lore.

| Benchmark / line | Object | Conflict | Primary metric family | Relation to this work |
|------------------|--------|----------|------------------------|------------------------|
| **PersonaGym** | Named / fictional personas | Stay-in-character vs OOC | Persona consistency / actionability | Orthogonal construct: RP fidelity ≠ principle hold |
| **CharacterEval** | Role-play characters | Dialogue / personality consistency | Character-consistent generation scores | Style/lore focus; no say→use→hold ladder for assistant principles |
| **RPEval** | Role-play adherence | Instruction vs character constraints | RP adherence rubrics | Useful contrast class; different risk model |
| **Saying-is-not-using-it** | Stated vs enacted dispositions | Endorsement vs forced action | Say vs use gap | Direct ancestor; we add **hold**, fracture taxonomy, faithfulness probes |
| **Preference / self-consistency** | Preference stability across prompts | Inconsistency under paraphrase / framing | Consistency rates | Related signature; we fix a character card and pressure types |
| **Constitution / value specs** | Written principles as training or policy targets | Spec vs behavior | Alignment to constitution | Specimens are lightweight constitutions; we test *behavioral load-bearing*, not training dynamics |

### Differentiation claim (one line)

Persona / RP suites ask “does the model *play* the role?”; character-hold asks “when the *assistant itself* is instructed to hold a principle, does saying survive into using, and using into holding under pressure?”

### Citation posture

Cite PersonaGym / CharacterEval / RPEval as **contrast**, not as competing leaderboards for the same construct. Report character-hold metrics with scorer modality (deterministic / heuristic / human / LLM-judge) explicit.
