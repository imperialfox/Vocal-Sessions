/* Vocal Sessions · parts.settings.js (Q41)
   The parts kit's settings for this app: one line per decision in Ivan's register (D01–D19), with its ID in a
   comment, so searching a decision's ID finds its line. The kit itself (js/parts-kit.js, css/parts-kit.css) is a
   pinned copy of imperialfox/parts-kit, never edited here (tools/parts-kit/, MAINTAINING › Parts kit).
   The kit leads (D18): its springs, speed and Reduce Motion are the app's. Where the app differs from the kit, the
   difference gets its own line with a decision ID: a spring in springs: {…} below, a timing in css/app.css, or one
   element's style. tests/test_parts.py checks Parts.differences() against its list, which is empty today.
   D16 and D17 are stylesheet values, not settings: menus use var(--r-card) (D16) and --r-sheet is 46, the screen's
   own corners (D17), in css/app.css's value set. */
Parts.settings({
  app: 'Vocal Sessions',
  root: '#layer', // the kit's overlays go in #layer, above the app (the sheet host, ui.js)
  motion: 'kit', // D18 the kit runs the motion: its springs, speed and Reduce Motion
  springs: {}, // D18 the app's own springs, one line each with its ID (none today)
  tabBar: { fold: false, searchGap: 8 }, // D01 never folds · D02 search circle 8 pt from the bar
  segmented: { style: 'gallery' }, // D04 the gallery's knob: 350 ms spring, swells to glass, draggable
  row: { press: 'highlight' }, // D06 rows highlight while pressed, no shrink
  choices: 'actionSheet', // D07 choices are action sheets
  confirm: 'alert', // D08 "Are you sure?" is an alert with Cancel and a red action
  sheet: {
    withStops: ['sgNew'], // D09 New song (VS-051) opens at the 45% stop on Add media
    growsToFull: ['sgNew'], // D10 (option A) New song grows to full when a file is picked or Manually is chosen
    fullScreen: ['sgKey'], // D10 the Marks key (VS-053) is a full-screen cover
    dragShrink: false, // D14 sheets follow the finger without shrinking
    glass: 'strong', // D15 sheets keep the strong glass
  },
  menu: { submenus: [] }, // D11 pinned: built, not used yet
  glass: { appear: [] }, // D12 pinned: built, not used yet
  press: { glint: [] }, // D13 pinned: built, not used yet
  timing: { hold: 700, lift: 200, toast: 3000 }, // D16 hold 700 ms (Ivan, 4 Nov 2026), lift from 200 ms; toasts 3 s
  own: {
    pattern: { speedControl: 'slider' }, // D03 the pattern player's speed control is the standard slider
    datePicker: 'calendar', // D05 the practice calendar sheet stays (the app's own part)
    topBar: { barTop: 'safe area' }, // D19 the top bar's buttons at the app's own top area (--pk-bar-top in css/app.css's .bar), where Q08 measured them, not the kit's 54 pt
  },
});
