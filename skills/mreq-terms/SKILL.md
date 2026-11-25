---
name: mreq-terms
description: "For a user who has an idea but not the field's words for it: give the expert terms and the knowledge behind them that fit the user's prompt and situation, each checked against a source, then rewrite the prompt with them. Use only when the user invokes it: /mreq-terms, or $mreq-terms in Codex."
argument-hint: "[<prompt>]"
disable-model-invocation: true
---

I have an idea, but I lack the expert words for it and the knowledge behind them. Teach me the ones that fit the prompt below (or, if none is given, my most recent request), so that I can ask for what I mean.

Prompt: $ARGUMENTS

When the Prompt line above holds only a placeholder word, not a prompt, my agent did not fill it in: the prompt is the text I gave with this skill.

Start from my situation, not from the field in general: the prompt, what this conversation already says, and the files and code the prompt is about. Read them; do not work from a summary of them. Every term you give must name something in that material.

If my prompt could name more than one problem, first list the two or three problems it could be, each with the one term that names it and the sign that would tell it apart from the others. Then teach the words for the most likely one and say why you picked it.

1. **The words.** Give the terms that would change what gets built, the most important first: 5 to 12, and stop when the next one would change nothing. For each:
   - the term, and its meaning in one plain sentence;
   - the part of my prompt, conversation or files it names;
   - what an expert knows about it that I should: the choice it forces, or the mistake people make without it;
   - one real project, paper or system that uses it that way, with a link;
   - what it lets me ask an agent for.
2. **Words that look right but are not.** Name up to 3 terms I might reach for that do not fit my situation. For each: what it really means, and which term from 1 to use instead. Skip this part when there is none.
3. **Neighboring fields.** Pick 2 or 3 fields that solved the same shape of problem under other names. For each: what carries over, where the analogy breaks, and which terms come back.
4. **What I left out.** Name what I didn't mention but should care about.
5. **My prompt, in the new words.** Rewrite my prompt with the terms, in a single code block I can copy. Change the words, not the work: add nothing from 4. After the code block, say in one line that `/mreq-pro` (`$mreq-pro` in Codex) with no prompt sharpens this prompt next, and that `/mreq-define` (`$mreq-define` in Codex) with no request starts the work from it.

Keep the terms correct:
- Open every link and confirm that the page uses the term that way. Cut any citation you can't confirm; the term can stay without one. When you have no tool that opens web pages, give no citation and say so once.
- Never coin a term. When the field has no settled word for something, say so and describe it in plain words.
- When two communities use different words for the same thing, give both and say who uses which.

Explain in my language, and write each term the way the field writes it.

If you don't know the field well enough to name its terms, say so and ask me instead of guessing. No padding.
