# Handing off work

How to pass Vocal Sessions work between AI models (Gemini, ChatGPT, Claude) or into a fresh chat, and a template for the note itself. [MAINTAINING.md](MAINTAINING.md) covers how the app is built; this covers how a task moves from one chat to the next.

## How it works

- **The repository is the source of truth.** The code on `main`, the [README](README.md), [MAINTAINING.md](MAINTAINING.md) and the [CHANGELOG](CHANGELOG.md) say what exists. A handoff only summarises what one task needs: what's agreed, what's done and what's next. If a handoff and the code disagree about what's built, the code wins. If they disagree about what Ivan decided, ask him.
- **Give each model one job.** For example, one helps explore an idea, another challenges the scope or reviews a focused change, and Claude builds an approved feature in a fresh build chat. These are suggested roles, not fixed limits on what a model can do. Name the job in the handoff.
- **One builder per change.** Only one model writes the code for a change. Others can review its plan or its diff, but don't ask several models to build the same feature separately.
- **Hand off at a task boundary.** Write one when a stage ends (an idea agreed, a prototype approved, a build pushed), when switching models, or when starting a fresh chat. Every build starts in a fresh chat from a handoff. Include enough to carry on without the earlier chat; don't paste the whole conversation.
- **"Render" is still the gate.** Plan, discuss and prototype freely, but nothing is built into the app or pushed until Ivan says **"render"**. The handoff records whether he has, and for what. Without it, the receiving model stops at a plan or prototype.
- **Follow the project's conventions.** Link to them rather than copying them: [tests](MAINTAINING.md#tests) (quick while building, the full suite once before pushing), [rules that keep old data working](MAINTAINING.md#rules-that-keep-old-data-working), [the changelog format](MAINTAINING.md#the-changelog-page), [releasing](MAINTAINING.md#releasing) and [style](MAINTAINING.md#style). Write down only what's specific to the task.
- **Keep it clean.** No secrets, tokens or passwords, and no private data: lyrics, recordings, backups, song tracks or personal notes. The repo is public, so a filled-in handoff goes into the new chat (or Ivan's own project notes), not into a commit.

## Receiving one

1. Read the handoff, then check it against the repo: the version on `main`, and the files it names.
2. Say anything that doesn't match, or any open question that blocks the next action, before starting.
3. Do the next action it names, and stop where it says. End with a new handoff if the work carries on elsewhere.

## Template

Copy this into the new chat, fill in what applies and delete what doesn't. Aim for one screen. Link to longer design notes rather than pasting them.

```markdown
# Handoff · <task> · <date>

**For:** <model> · **Job:** <explore / challenge the scope / review / build>
**Repo:** imperialfox/Vocal-Sessions, `main` at <version or commit>

**Goal:** <what this work is for, in a line or two>
**Current task:** <the part this chat does>

**Status:** <what's agreed, prototyped, built or pushed so far>

**Agreed:**
- <requirement or decision, and who made it>

**Out of scope:**
- <what not to change or add>

**Where to look:** <files, functions or MAINTAINING.md sections>

**Constraints:** MAINTAINING.md for tests, data, changelog, releases and style. Also: <anything specific to this task>

**Open questions, risks, assumptions:**
- <…>

**Next action:** <the one thing to do first, and where to stop>

**Done when:** <acceptance criteria>
**Checks:** <e.g. `python tests/run.py quick` while building, the full suite once before pushing, what Ivan checks on his iPhone>

**Render:** <not given | given on <date> for <scope>>. Without it, plan or prototype only: no app changes, no push.
```
