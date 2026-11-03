# Repository guidance

When creating wireframes or prototypes, read `PROTOTYPE_DEFAULTS.md` and follow those defaults unless the user specifies otherwise.

## Render approval

Whenever Ivan explicitly says **Render** for a queued item, whichever assistant receives it must follow [the Render approval workflow](.agents/skills/render-approval/SKILL.md) and update the shared GitHub record directly. Do not ask Ivan to relay the approval to another assistant. Render approves that item's exact scope only; it does not authorize implementation. Keep the queue, handoff and spec consistent, and do not report approval as recorded until the Git-tracked record has been updated. A separate **Build** instruction is required before implementation.

## Screen IDs

Every screen, sheet and main part has a permanent ID (`VS-001`, `VS-001 › start-session-button`) and the main journeys have flow IDs (`F-01`), all in `js/register.js`. Use them in notes, wireframes, prototypes, handoffs and Debriefs, pair an ID with its name on first mention, and add, rename or retire them as [MAINTAINING › Screen IDs](MAINTAINING.md#screen-ids) says. IDs are never reused or renumbered.
