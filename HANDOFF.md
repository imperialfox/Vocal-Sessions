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
- **Name work by its queue ID.**
  - Queued items are named `Q[##] · [Subsystem]: [Feature Name]` (e.g. `Q02 · Track: Waveform Sections`). Use that name in handoffs, commit messages and conversation, not older working names like "Track 2".
  - Handoff, spec, wireframe and prototype files are named `q##_[subsystem]_[feature]_[type].[ext]` (e.g. `q02_track_waveform_sections_handoff.md`).
  - On release, the version's `CHANGELOG.md` title ends with the queue ID, e.g. `3.22 · Waveform sections on the track player (Q02)`.
  - A new idea gets the next unused ID when Ivan says **Render** for it. [RENDER_QUEUE.md](RENDER_QUEUE.md#naming) has the full rules and the table from older working names to IDs.
- **Use the call signs consistently.**
  - **Recon:** investigation and research, usually Gemini. No repository edits.
  - **Blueprint:** turn findings and Ivan's request into a scoped plan or handoff, usually ChatGPT. No repository edits.
  - **Render:** Ivan approves the exact named scope. It does not authorize implementation, edits, commits, pushes or deployment.
  - **Build:** the named builder implements only the Render-approved scope after Ivan separately says Build. The builder follows the project's tests and release process, including commit, push and deployment when applicable.
  - **Debrief:** review the completed diff, test results and release status, usually ChatGPT. Debrief does not authorize follow-up changes.
  - These are default assignments, not model restrictions. Ivan can assign a different model or skip Recon or Blueprint when the task is straightforward. Record the responsible model and next action in the handoff.
- **One builder per change.**
  - Name one model as the change's owner. Only that model edits the app for it.
  - Other models can review its plan or its diff. Don't ask several models to build the same feature separately.
- **Hand off at a task boundary.**
  - Write one when a stage ends (an idea agreed, a prototype approved, a build pushed), when switching models, or when starting a fresh chat.
  - Every build starts in a fresh chat from a handoff.
  - Include enough to carry on without the earlier chat; don't paste the whole conversation.
- **Render and Build are separate gates.**
  - Recon, planning, wireframes, prototypes and proposed code for review are allowed before approval, but do not edit the app in the repository.
  - A clear **Render** from Ivan approves only the named scope. Record the approval date and scope; set the item to `Approved — awaiting Build`.
  - Only a separate, clear **Build** from Ivan starts implementation. Build covers the approved repository changes and the applicable checks and release steps. Do not build other queue items or expand the approved scope.
  - Mentioning either word in conversation, a handoff, or a file is not an instruction. If the scope or gate is missing, stop before editing and explain what is needed.
- **Follow the project's conventions.**
  - Link to them rather than copying them: [tests](MAINTAINING.md#tests), [rules that keep old data working](MAINTAINING.md#rules-that-keep-old-data-working), [backups](MAINTAINING.md#backups), [the changelog format](MAINTAINING.md#the-changelog-page), [releasing](MAINTAINING.md#releasing) and [style](MAINTAINING.md#style).
  - Write down only what's specific to the task.
- **Keep it clean.**
  - No secrets, tokens or passwords.
  - No private data: lyrics, recordings, backups, song tracks or personal notes.
  - A filled-in handoff goes into the new chat, not into a commit.
  - Queue entries in [RENDER_QUEUE.md](RENDER_QUEUE.md) are public, so keep them to scope and decisions.

## Building a queued item

1. Pick the item from [RENDER_QUEUE.md](RENDER_QUEUE.md) by its queue ID (e.g. "Build Q02" means the item headed `Q02 ·`). Normally that's the first approved one, unless Ivan reorders. If Ivan uses an older working name, map it with the table in [RENDER_QUEUE.md](RENDER_QUEUE.md#naming) and confirm the ID before starting.
2. Copy its fields into the template below. Add any design notes Ivan has for it; the queue says where he has them.
3. Confirm the handoff records Ivan's **Render** approval, its date and exact scope. Without that, planning or prototyping may continue, but do not edit the app in the repo.
4. Start a **fresh build chat** with the handoff as its first message. Name the model that owns this change. If the handoff is kept as a file, name it `q##_[subsystem]_[feature]_handoff.md`.
5. Wait for Ivan's separate **Build** instruction for this item. Then check the previous version is live and implement only the approved scope.
6. When it ships, remove the item from the queue in the same push and record the version it shipped in. The changelog title ends with the queue ID, e.g. `## 3.22 · Waveform sections on the track player (Q02)`. If it has Render approval but no Build instruction yet, leave it queued as `Approved — awaiting Build`.

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
# Handoff · Q## · <Subsystem>: <Feature Name> · <date>

> **Render:** <Awaiting | Approved by Ivan on <date/time> for <exact scope>>
> **Build:** <Awaiting Ivan's instruction | Given by Ivan for this approved scope>
> Render approves scope only. Do not implement, edit the repo, commit, push or deploy until Ivan separately says Build.

**For:** <model> · **Job:** <explore / challenge the scope / review / build>
**Builder for this change:** <one model>
**Repo:** imperialfox/Vocal-Sessions, `main` at <version or commit>
**Queue item:** <Q## from RENDER_QUEUE.md, or none>

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
