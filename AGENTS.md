# Repository guidance

When creating wireframes or prototypes, read `PROTOTYPE_DEFAULTS.md` and follow those defaults unless the user specifies otherwise.

## Render approval

Whenever Ivan explicitly says **Render** for a queued item, whichever assistant receives it must follow [the Render approval workflow](.agents/skills/render-approval/SKILL.md) and update the shared GitHub record directly. Do not ask Ivan to relay the approval to another assistant. Render approves that item's exact scope only; it does not authorize implementation. Keep the queue, handoff and spec consistent, and do not report approval as recorded until the Git-tracked record has been updated. A separate **Build** instruction is required before implementation.
