---
name: render-approval
description: Record an explicit Render approval in the Vocal Sessions repository and keep the queue, handoff, and approved scope in sync.
---

# Render approval workflow

Use this workflow when Ivan explicitly says **Render** for a queued Vocal Sessions item. Render approves scope; it never authorizes implementation.

## Before changing status

1. Read the current `RENDER_QUEUE.md` and locate the exact item Ivan means. If the item is ambiguous, missing, or not ready for approval, stop and ask which item or decision is needed.
2. Read the matching handoff and spec that are available in the active workspace or project notes. Compare the scope there with the scope Ivan just approved. Do not silently broaden, rewrite, or infer approval for unresolved decisions.
3. Check the current branch and repository workflow. Keep edits on the intended shared branch; do not create a code change or begin implementation.

## Record the approval

1. Update the queue item to `Approved — awaiting Build` and record the Render approval date and the exact approved scope.
2. Update every accessible handoff or spec that records the approval. Keep the wording and scope consistent with the queue. Link the records to each other where possible.
3. Preserve the separate Build gate. Do not mark an item Build authorized, start implementation, or push application code.
4. Persist the documentation changes to the shared repository location Claude uses, following its existing branch and review workflow. If access or permission prevents that, leave the complete documentation changes ready in the workspace and state plainly that GitHub is not yet synced.

## Verify and report

Before saying Render is recorded, reread the changed files and confirm:
- the queue and handoff/spec name the same item;
- the status is `Approved — awaiting Build`;
- the recorded scope and exclusions agree;
- the approval date is present; and
- no Build authorization or implementation has been implied.

Then reply with the item ID, the files updated, the shared commit/PR or workspace location, and the explicit next gate: Ivan must say **Build** before Claude implements it. Never call the queue stale without also identifying the mismatch and repairing or preparing the corresponding documentation sync.
