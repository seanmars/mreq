---
name: mreq-terms
description: "Teach the user the expert terms for what they are building, each with a source that was opened and confirmed, then rewrite their description with those terms. Use only when the user invokes it: /mreq-terms, or $mreq-terms in Codex."
argument-hint: "[<description>]"
disable-model-invocation: true
---

Teach me the expert words for what I am building, described below (or, if nothing is given, in my most recent request). Start from my own files, code and description, not from a summary of them.

Description: $ARGUMENTS

When the Description line above holds only a placeholder word, not a description, my agent did not fill it in: the description is the text I gave with this skill.

If my description could name more than one problem, first list the two or three problems it could be, each with the one term that names it and the sign that would tell it apart from the others. Then teach the words for the most likely one and say why you picked it.

1. **The words.** Give 8 to 12 terms, ranked by how much each would change what gets built. For each: the term and its meaning in one plain sentence, the part of my description it names, one real project, paper or system that uses it that way, with a link, and what it lets me ask an agent for.
2. **Neighboring fields.** Pick 2 or 3 fields that solved the same shape of problem under other names. For each: what carries over, where the analogy breaks, and which terms come back.
3. **What I left out.** Name what I didn't mention but should care about.
4. **My description, in the new words.** Rewrite my description with the terms, in a single code block I can copy. Change the words, not the work: add nothing from 3.

Open every link and confirm that the page uses the term that way. Cut any citation you can't confirm; the term can stay without one. When you have no tool that opens web pages, give no citation and say so once.

If you don't know the field well enough to name its terms, say so and ask me instead of guessing. No padding.
