# How to grill

The method `mreq-grill` and `mreq-define` use to pressure-test a subject. The subject is a `.mreq/` task document, or a restatement the user confirmed in the conversation. The skill that sent you here says which one, and what to do with the outcome.

## The aim

A plan fails on what nobody checked or said, not on what it wrote down. Grill until every assumption is named, and every open question is answered or parked on purpose. Running out of questions is not the end: the user's confirmation is.

## The four quadrants

Sweep them in this order. The last two hide the real risk.

1. **Known knowns**: the claims the subject rests on. Verify each against the code. A false known is the most dangerous kind.
2. **Known unknowns**: the open questions. Ask each as an option question (see "Asking the user" in the skill): your suggested answer first, with its reason in the description, then the real alternatives, and **Leave it open** last when the decision can wait.
3. **Unknown knowns**: the premises nobody said out loud. Name each and confirm it holds.
4. **Unknown unknowns**: the blind spots. Ask "what would have to be true for this to fail?" and follow the answers.

Report the four quadrants separately, in this order. Write "none found" under a quadrant with nothing. A later round sweeps and reports less: see "A later round".

## A later round

A round is one sweep and the restatement after it. When this conversation already grilled this subject, the next round is a later round. Grill only what is new:

- Sweep only three things: what the last round changed, what is still open, and the focus the user named.
- Do not verify again a claim that held, and do not confirm again a premise the user confirmed. Check one again only when a change since the last round touches it.
- Report only the quadrants with a new finding, in the same order. When no quadrant has one, say so in one line.
- Change the four lists (see "What the grill produces") only where this round changed them.

When the user asks for a full sweep, do a full one. A new conversation always starts with a full sweep.

## Interview rules

- Look up facts in the code; ask the user for decisions.
- A fact you bring in yourself is a known too: verify it in the code or the docs before you rely on it. A fact you cannot verify goes into the restatement as an assumption, never into a decision's reason.
- Ask unrelated questions together. Hold a question that depends on an open one.
- Ask what each answer implies that nobody said.
- To confirm an unknown known, ask with **It holds** and **It does not hold** as options, and your reason in the description of the one you recommend.

## What the grill produces

Four lists, for the skill's next restatement: the claims that held and the ones that fell, the assumptions now explicit, the decisions made (each with its reason and the alternative ruled out), and what is still open.

## Limits

- Edit no source code and create no files, even temporary ones. When a claim needs a measurement, it becomes a task or an open item.
- Write nothing before the user confirms the restatement.
