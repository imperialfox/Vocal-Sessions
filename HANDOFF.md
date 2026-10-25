# Handing off work

How to pass Vocal Sessions work between AI models (Gemini, ChatGPT, Claude) or into a fresh chat, with a template for the note itself.
- [MAINTAINING.md](MAINTAINING.md) covers how the app is built.
- [RENDER_QUEUE.md](RENDER_QUEUE.md) lists the app work that's queued.
- This file covers how a task moves from one chat to the next.

## How it works

- **The repository is the source of truth.**
  - The code on `main`, the [README](README.md), [MAINTAINING.md](MAINTAINING.md) and the [CHANGELOG](CHANGELOG.md) say what exists.
  - A handoff only summarises what one task needs: what's agreed, what's done and what's next.
  - If a handoff and the code disagree about what's built, the code wins. If they disagree about what Ivan decided, ask him.
- **Give each model one job.**
  - For example, one helps explore an idea, another challenges the scope or reviews a focused change, and Claude builds an approved feature in a fresh build chat.
  - These are suggested roles, not fixed limits on what a model can do. Name the job in the handoff.
- **One builder per change.**
  - Name one model as the change's owner. Only that model edits the app for it.
  - Other models can review its plan or its diff. Don't ask several models to build the same feature separately.
- **Hand off at a task boundary.**
  - Write one when a stage ends (an idea agreed, a prototype approved, a build pushed), when switching models, or when starting a fresh chat.
  - Every build starts in a fresh chat from a handoff.
  - Include enough to carry on without the earlier chat; don't paste the whole conversation.
- **"Render" is the gate for app changes.**
  - Planning, wireframes, prototypes and code written for review are always fine.
  - Changing the app in the repo, or pushing, waits until Ivan says **"render"** for that work.
  - The handoff records whether he has, when, and for what scope. If it says he hasn't, the receiving model stops at a plan, prototype or proposed change.
- **Follow the project's conventions.**
  - Link to them rather than copying them: [tests](MAINTAINING.md#tests), [rules that keep old data working](MAINTAINING.md#rules-that-keep-old-data-working), [backups](MAINTAINING.md#backups), [the changelog format](MAINTAINING.md#the-changelog-page), [releasing](MAINTAINING.md#releasing) and [style](MAINTAINING.md#style).
  - Write down only what's specific to the task.
- **Keep it clean.**
  - No secrets, tokens or passwords.
  - No private data: lyrics, recordings, backups, song tracks or personal notes.
  - A filled-in handoff goes into the new chat, not into a commit.
  - Queue entries in [RENDER_QUEUE.md](RENDER_QUEUE.md) are public, so keep them to scope and decisions.

## Building a queued item

1. Pick the item from [RENDER_QUEUE.md](RENDER_QUEUE.md). Normally that's the first one, unless Ivan reorders.
2. Copy its fields into the template below. Add any design notes Ivan has for it; the queue says where he has them.
3. Fill in **Approval**:
   - If Ivan has said "render" for it, write when and what it covers.
   - If not, the new chat can plan or prototype, but not build.
4. Start a **fresh Claude chat** (or whichever model owns the build) with the handoff as the first message.
5. The build checks the previous version is live and builds only that item.
6. When it ships, remove the item from the queue in the same push and record the version it shipped in.

## Receiving one

1. Read the handoff, then check it against the repo: the version on `main`, and the files it names.
2. Before starting, say anything that doesn't match, and any open question that blocks the next action.
3. Do the next action it names, and stop where it says.
4. If the work carries on elsewhere, end with a new handoff.

## Choosing checks

Pick the checks that fit the task, and name them in the handoff:
- **Documentation only:** check the links and review the diff. No app tests.
- **App work, while building:** `python tests/run.py quick`, or just the test files for what you're changing.
- **Before pushing app changes:** the full suite, once. Everything must pass.
- **Saved data changes** (new fields, a data version, IndexedDB stores, backup format): also the backup and data tests, including the old-backup fixtures. Follow [rules that keep old data working](MAINTAINING.md#rules-that-keep-old-data-working) and [backups](MAINTAINING.md#backups).
- **Releases:** follow [releasing](MAINTAINING.md#releasing) and run its release check.
- **Things only Ivan's phone can tell** (feel, real iOS behaviour): list them for him to check.

## Template

Copy this into the new chat. Fill in what applies and delete what doesn't.
- Aim for one screen.
- Keep **Agreed** for settled decisions. Put guesses under **Assumptions**.
- Link to longer notes rather than pasting them.

```markdown
# Handoff · <task> · <date>

> **Approval:** <Awaiting "render" | "render" given by Ivan on <date/time> for <scope>>
> Without "render": plan, prototype or propose changes only. Don't edit the app in the repo or push.

**For:** <model> · **Job:** <explore / challenge the scope / review / build>
**Builder for this change:** <one model>
**Repo:** imperialfox/Vocal-Sessions, `main` at <version or commit>
**Queue item:** <RENDER_QUEUE.md item, or none>

**Goal:** <what this work is for, in a line or two>
**Current task:** <the part this chat does>

**Status:** <what's agreed, prototyped, built or pushed so far>

**Agreed:**
- <settled decision, and who made it>

**Out of scope:**
- <what not to change or add>

**Where to look:** <files, functions or MAINTAINING.md sections>

**Constraints:** MAINTAINING.md for tests, data, changelog, releases and style. Also: <anything specific to this task>

**Open questions:**
- <needs Ivan's answer>

**Assumptions:**
- <taken as true for now, and to confirm>

**Risks:**
- <what could break, e.g. old backups, one sound at a time, layout at 375 px>

**Next action:** <the one thing to do first, and where to stop>

**Done when:** <acceptance criteria>
**Checks:** <from "Choosing checks": e.g. quick tests while building; full suite before pushing; backup tests if saved data changes; what Ivan checks on his iPhone>
```
