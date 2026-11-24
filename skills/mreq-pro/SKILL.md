---
name: mreq-pro
description: "Rewrite a prompt so it asks for what a top expert would do, in the expert's words: deeper, not bigger. Use only when the user invokes it: /mreq-pro, or $mreq-pro in Codex."
argument-hint: "[--no-terms] [<prompt>]"
disable-model-invocation: true
---

Sharpen the prompt below (or, if none is given, my most recent request). Make it deeper, not bigger. Depth means sharper judgment, better source material, stronger methods, an outside check and the expert's word for each thing. It does not mean more deliverables, sections or steps.

Prompt: $ARGUMENTS

When the Prompt line above holds only a placeholder word, not a prompt, my agent did not fill it in: the prompt is the text I gave with this skill.

When the prompt starts with `--no-terms`, that word is not part of the prompt: follow "With --no-terms" at the end too. When nothing follows it, sharpen my most recent request.

Start from my own material: the prompt, and the files and code it is about. Read them. Do not work from a summary of them.

If the prompt could name more than one problem, first list the two or three problems it could be, each with the one term that names it and the sign that would tell it apart from the others. Go on with the most likely one and say why you picked it.

First, answer these briefly (2-4 lines each):

1. **The crux.** What is the one hard part of this task that decides whether the result is good? What would a top professional do about it that my prompt doesn't ask for? What would a novice get wrong?
2. **Raw material.** What primary source would they start from (raw data, original documents, source code, direct measurement) instead of the summarized or pre-digested version I'm relying on?
3. **Methods and tools.** Which specific methods, tools or standards would they use? Name them. No generic advice.
4. **Outside check.** What evidence, independent of you and me, would show the result is right: a test, a benchmark, a primary source, a measurement? State it as a pass/fail condition defined before the work starts.

Then teach me the expert words for what I am building:

5. **The words.** Give 8 to 12 terms, ranked by how much each would change what gets built. For each: the term and its meaning in one plain sentence, the part of my prompt or files it names, one real project, paper or system that uses it that way, with a link, and what it lets me ask an agent for.
6. **Neighboring fields.** Pick 2 or 3 fields that solved the same shape of problem under other names. For each: what carries over, where the analogy breaks, and which terms come back.
7. **What I left out.** Name what I didn't mention but should care about.

Open every link and confirm that the page uses the term that way. Cut any citation you can't confirm; the term can stay without one. When you have no tool that opens web pages, give no citation and say so once. No padding.

If you don't know the field well enough to answer one of these, say so and ask me instead of guessing.

Then write the rewritten prompt in a single code block I can copy. It must:
- Ask for exactly the above: the crux, the raw material, the methods and the outside check.
- Use a term from 5 in place of my plain words wherever the prompt already asks for the thing the term names. Never add a term to add work.
- Keep the same scope as my original, or narrower. Cut anything that doesn't serve depth. If it ends up longer than my original, every added line must earn its place.
- Tell the agent to prototype any choice an experiment can settle, and recommend an option based on what it observed.
- List product or preference choices that no experiment can settle as open questions for me, instead of deciding them. Put each thing 7 names there too, as a question: it must not widen the scope.

After the code block, list in one line each what you removed or narrowed from my original, and why. Then list each phrase of mine that a term replaced: my phrase, then the term.

## With --no-terms

Skip 5, 6 and 7, and every rule that names them. Open no web page. Work from the prompt as I gave it: read a file only when the prompt cannot be understood without it. After the code block, list only what you removed or narrowed.
