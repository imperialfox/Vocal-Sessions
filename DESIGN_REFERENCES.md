# Design references

Where Vocal Sessions' look and motion come from, so it's clear what was borrowed and what wasn't.

**The short version:** the app copies **no code** from anyone. It takes **numbers and ideas** (blur strengths, spring timings, how far a button grows) from Apple's own guidance and from open-source projects, and rebuilds them in its own CSS and JavaScript. If code is ever copied from one of these projects, its licence notice goes in this file next to it.

Each entry says what it is, its licence, how sure its numbers are, and which queue items (`RENDER_QUEUE.md`) use it. "Measured" means the source's authors checked the number against real iPhone screen recordings. "By eye" means they tuned it to look right without measuring.

Last updated 2 Nov 2026.

---

## Apple

- **[Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/).** The app's text sizes, system colours and layers follow it (Q10, `MAINTAINING.md` › Design foundations). The "Scroll views" page (checked 2 Nov 2026) is the basis of the Scroll Behaviour Pass draft.
- **WWDC24, "Enhance your UI animations and transitions".** The source of the card zoom, transitions that can always be interrupted, and springs that carry on the finger's speed (`MAINTAINING.md` › Motion).
- **Apple's SwiftUI tutorial, "Animating views and transitions".** It covers animating the change rather than the view, entrances and exits that differ, and the staggered ripple behind the app's launch ripple.
- **Apple's own apps, as models:**
  - Music and Notes: where the bars sit on iPhone, and the tab bar's collapse (Q08).
  - Books: the Today dashboard.
  - Health: the Progress charts.
  - Photos: how the search field stretches (Q34, now Q41).

Only the ideas and measured positions are used. Nothing from Apple's apps or videos is copied into the repo.

## Open-source projects

### Used

- **[sdegenaar/liquid_glass_widgets](https://github.com/sdegenaar/liquid_glass_widgets)** (Flutter, MIT licence). Read at 1.16.1 on 2 Nov 2026. A Flutter kit that imitates iOS 26/27 Liquid Glass.
  - **What we took:** numbers only, no code. These came from its source and changelog.
  - **Measured:**
    - the press: grow 17 pt, light up, the press and release springs
    - the iOS 27 glass: tint, saturation, frost, rim and shadow in light and dark
    - glass appearing and leaving
    - the long-press menu's timing
    - the top bar buttons' morph
    - the search field's stretch
  - **By eye:** the menu material and springs, the switch, the segmented control, the toast timing, the sheet's flick and corners, and the soft edge's fade shape.
  - **Used in:** Q33 · Interface: Glass Native Tuning, Q34 · Interface: Native Menus and Controls (retired, replaced by Q41 · Interface: Parts Kit Move), the parts kit, and the Scroll Behaviour Pass draft.
  - Where its numbers were made for a GPU effect (the iOS 27 two-layer frost), the CSS version is an approximation, tuned on the phone.

### Looked at, nothing used yet

- **[iyinchao/liquid-glass-studio](https://github.com/iyinchao/liquid-glass-studio)** (MIT). A WebGL playground for bending glass (refraction, shine, shapes melting together). All its numbers are by eye.
  - Kept as a learning tool, with one idea for later: stretching draggable glass in the direction it moves, capped at the measured native 5%.
  - It can't bend live page content in Safari, so none of it is in the app.
- **[zakisheriff/Liquid-Glass](https://github.com/zakisheriff/Liquid-Glass)** (MIT). A React kit of glass controls, tuned by eye.
  - Ideas noted for later: a "tick" haptic through a hidden native switch (tested on 2 Nov 2026 and it didn't fire from code on iOS 27), a lens over a control's own copy that works in Safari, and drag-stretch maths.
  - Where its numbers differ from the measured ones above (for example a smaller press growth), the measured ones win.

### Looked at and set aside

- **ybouane/liquidglass:** it works by taking a picture of the page every frame, which is too heavy, and it has **no licence**, so its code can't be reused.
- **archisvaze/liquid-glass** (MIT): its effects only work in Chrome, or over a background image, not over real content on iPhone.
- **ChenYilong/CYLTabBarController:** native iOS only, using Apple's own glass.
- The rest of GitHub's [`ios26-liquid-glass`](https://github.com/topics/ios26-liquid-glass) topic (16 repos on 2 Nov 2026): native Swift apps, customisation tools and icon packs, with nothing to borrow for a web app.

## Other sources

- **[Can I use](https://caniuse.com/), checked 2 Nov 2026:** Safari on iPhone can't report the system's Reduce Transparency setting (`prefers-reduced-transparency`). That's why Q33 adds the app's own switch.

---

## Where the detail lives

The full notes, with the numbers, how sure each one is and where in each project it came from, are in Ivan's private project notes, not this public repo. They're named in each queue item's section in `RENDER_QUEUE.md`.
