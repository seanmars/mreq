---
name: mreq-pro
description: "Rewrite a prompt so it asks for what a top expert would do: deeper, not bigger. Use only when the user invokes it: /mreq-pro, or $mreq-pro in Codex."
argument-hint: "[<prompt>]"
disable-model-invocation: true
---

Sharpen the prompt below (or, if none is given, my most recent request). Make it deeper, not bigger. Depth means sharper judgment, better source material, stronger methods and an outside check. It does not mean more deliverables, sections or steps.

Prompt: $ARGUMENTS

When the Prompt line above holds only a placeholder word, not a prompt, my agent did not fill it in: the prompt is the text I gave with this skill.

First, answer these briefly (2-4 lines each):

1. **The crux.** What is the one hard part of this task that decides whether the result is good? What would a top professional do about it that my prompt doesn't ask for? What would a novice get wrong?
2. **Raw material.** What primary source would they start from (raw data, original documents, source code, direct measurement) instead of the summarized or pre-digested version I'm relying on?
3. **Methods and tools.** Which specific methods, tools or standards would they use? Name them. No generic advice.
4. **Outside check.** What evidence, independent of you and me, would show the result is right: a test, a benchmark, a primary source, a measurement? State it as a pass/fail condition defined before the work starts.

If you don't know the field well enough to answer one of these, say so and ask me instead of guessing.

Then write the rewritten prompt in a single code block I can copy. It must:
- Ask for exactly the above: the crux, the raw material, the methods and the outside check.
- Keep the same scope as my original, or narrower. Cut anything that doesn't serve depth. If it ends up longer than my original, every added line must earn its place.
- Tell the agent to prototype any choice an experiment can settle, and recommend an option based on what it observed.
- List product or preference choices that no experiment can settle as open questions for me, instead of deciding them.

After the code block, list in one line each what you removed or narrowed from my original, and why.