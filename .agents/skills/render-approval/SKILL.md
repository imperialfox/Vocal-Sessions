---
name: render-approval
description: Record an explicit Render approval in the Vocal Sessions repository and keep the queue, handoff, and approved scope in sync.
---

# Render approval workflow

Use this workflow whenever Ivan explicitly says **Render** for a queued Vocal Sessions item, whether the instruction arrives in Gemini Antigravity, ChatGPT, or another assistant. Render approves scope; it never authorizes implementation.

## Before changing status

1. Read the current `RENDER_QUEUE.md` from the shared GitHub repository and locate the exact item Ivan means. If the item is ambiguous, missing, or not ready for approval, stop and ask which item or decision is needed.
2. Read the matching handoff and spec from the repository or the active project's available notes. Compare them with the scope Ivan just approved. Do not silently broaden, rewrite, or infer approval for unresolved decisions.
3. Check the current repository branch and review workflow. Do not create a code change or begin implementation.

## Record the approval

1. Update the queue item to `Approved — awaiting Build` and record the Render approval date and exact approved scope.
2. Update every accessible handoff or spec that records the approval. Keep wording and scope consistent with the queue, and link the records to each other where possible.
3. Use the GitHub connector or shared repository workspace available in the current assistant to persist the documentation update to the shared location Claude reads, following the repository's existing branch and review workflow. Do not ask Ivan to pass the approval to another assistant.
4. Preserve the separate Build gate. Do not mark an item Build authorized, start implementation, or push application code.
5. If this assistant has no GitHub or shared-workspace write access, prepare the complete changes and state plainly that GitHub is not yet synced. Never claim the shared record changed when it did not.

## Verify and report

Before saying Render is recorded, reread the changed files and confirm:
- the queue and handoff/spec name the same item;
- the status is `Approved — awaiting Build`;
- the recorded scope and exclusions agree;
- the approval date is present; and
- no Build authorization or implementation has been implied.

Then reply with the item ID, files updated, shared commit/PR or workspace location, and the explicit next gate: Ivan must say **Build** before Claude implements it. Never call the queue stale without identifying the mismatch and repairing or preparing the corresponding documentation sync.
