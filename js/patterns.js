/* Vocal Sessions · patterns.js (3.48, Q32)
   The shared pattern player (PAT): piano-like notes the app makes itself, from a library of 60 practice patterns.
   It owns everything about playing a pattern: the sound library and the notes it makes (Web Audio, no recordings),
   the pattern library, the drawing with its red playhead, the dock and its pills, the Patterns page, the speed slider,
   the range check against your voice, the vowel cue, the chord before each round, the held note underneath and the
   home ending. A page that uses it passes in only what it knows (use()): a route (the key notes of each round, or none),
   a default pattern and the syllables sung, plus its colour and two facts about the exercise. The exercise page is its
   first user; nothing in it is tied to exercises, so other places (a Today widget, say) can reuse it as it is.
   - Every sound starts through NOW.start('pattern', …) (one sound at a time). Stop fades out over about a third of a
     second; a route that finishes goes back to its first key (the home ending).
   - Plays with the iPhone's silent switch on: the first tap starts a tiny silent looping <audio>, which puts the page in
     media playback (paused whenever the page is hidden), and navigator.audioSession is set to 'playback' where it exists.
   - The screen stays awake while it plays (the shared AWAKE lock); where Screen Wake Lock is missing nothing breaks.
   - Saved choices travel with backups in D.prefs.pat (see clean()): the pattern and starting note per exercise, each
     pattern's speed, Favourites, your voice range, and the sound options. Fields it doesn't know are kept as they are.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

const PAT = (() => {
  /* ===== The pattern library =====
     [number, name, group, steps, semitones from the key (null: a breath), family (riffs), lengths (1 = one beat;
     under 0.5 is a quick touch: played lighter and drawn smaller), what it trains]. Groups: w Warm-ups, a Agility,
     r Riffs and runs (families s, t, l, m), x Flips. Numbers are the order they show and are saved, so never renumber. */
  // prettier-ignore
  const LIB = [
    [1, 'Five-note scale', 'w', '1 2 3 4 5 4 3 2 1', [0, 2, 4, 5, 7, 5, 4, 2, 0], 0, 0, 'Smooth, even steps through the middle of your voice'],
    [2, 'Triad', 'w', '1 3 5 3 1', [0, 4, 7, 4, 0], 0, 0, 'Clean jumps between the notes of a chord'],
    [3, 'Octave arpeggio', 'w', '1 3 5 8 5 3 1', [0, 4, 7, 12, 7, 4, 0], 0, 0, 'Reaching a full octave without straining for it'],
    [4, 'Octave jump', 'w', '1 5 8 5 1', [0, 7, 12, 7, 0], 0, 0, 'Landing the top note cleanly, with no slide'],
    [5, 'Pentatonic', 'w', '1 2 3 5 6 5 3 2 1', [0, 2, 4, 7, 9, 7, 4, 2, 0], 0, 0, 'The five notes most riffs are built from'],
    [6, 'Walk down', 'w', '5 4 3 2 1', [7, 5, 4, 2, 0], 0, 0, 'Coming down smoothly, with the same tone all the way'],
    [7, 'Octave scale', 'w', '1 2 3 4 5 6 7 8 7 6 5 4 3 2 1', [0, 2, 4, 5, 7, 9, 11, 12, 11, 9, 7, 5, 4, 2, 0], 0, 0, 'Every step of the full scale, evenly'],
    [8, 'Repeated note', 'w', '1 1 1 1 1', [0, 0, 0, 0, 0], 0, 0, 'Keeping one pitch steady each time you restart it'],
    [9, 'Build-up', 'a', '1 · 12 · 123 · 1234 · 12345', [0, null, 0, 2, null, 0, 2, 4, null, 0, 2, 4, 5, null, 0, 2, 4, 5, 7], 0, 0, 'Adding one note at a time while staying accurate'],
    [10, 'Quick five down', 'a', '5 5 5 4 3 2 1', [7, 7, 7, 5, 4, 2, 0], 0, 0, 'Repeated notes, then a quick, clean descent'],
    [11, 'Bounce', 'a', '5 3 1 3 5 3 1', [7, 4, 0, 4, 7, 4, 0], 0, 0, 'Moving lightly between the notes of a chord'],
    [12, 'Nine-note scale', 'a', '1 2 3 4 5 6 7 8 9 8 … 1', [0, 2, 4, 5, 7, 9, 11, 12, 14, 12, 11, 9, 7, 5, 4, 2, 0], 0, 0, 'A longer line on one breath'],
    [13, 'Thirds', 'a', '1 3 2 4 3 5 4 2 1', [0, 4, 2, 5, 4, 7, 5, 2, 0], 0, 0, 'Skipping up and stepping back, which sharpens your tuning'],
    [14, 'Octave-and-a-half', 'a', '1 3 5 8 10 12 11 9 7 5 4 2 1', [0, 4, 7, 12, 16, 19, 17, 14, 11, 7, 5, 2, 0], 0, 0, 'Range: easing through your break and back down'],
    [15, 'Octave leaps', 'a', '1 8 1 8 5 3 1', [0, 12, 0, 12, 7, 4, 0], 0, 0, 'Big jumps that land in tune both ways'],
    [16, '3-note riff', 'r', '3 2 1', [4, 2, 0], 's', 0, 'The basic riff: three clear notes, the first one longest'],
    [17, 'Rising 3-note riff', 'r', '1 2 3', [0, 2, 4], 's', 0, 'The same riff, going up'],
    [18, 'Hook riff', 'r', '5 – 4 3', [7, 5, 4], 's', [2, 1, 1], 'Riff timing: one held note, then two quick ones'],
    [19, 'Minor 3-note riff', 'r', '4 ♭3 1', [5, 3, 0], 's', 0, 'A short riff with a darker, minor sound'],
    [20, '4-note fall', 'r', '5 – 3 2 1', [7, 4, 2, 0], 's', [2, 1, 1, 1], 'A held note, then a quick pentatonic fall'],
    [21, '5-note riff', 'r', '3 2 1 6 5 (6 and 5 below)', [4, 2, 0, -3, -5], 's', 0, 'The classic ending riff, dipping below the key'],
    [22, 'Pentatonic fall', 'r', '6 5 3 2 1', [9, 7, 4, 2, 0], 's', 0, 'The staple pop and R&amp;B run'],
    [23, 'Change of direction', 'r', '8 7 6 7 6 5', [12, 11, 9, 11, 9, 7], 's', 0, 'Turning back up mid-run without smudging the notes'],
    [24, 'Slingshot', 'r', '8 8 8 6 5 6 8', [12, 12, 12, 9, 7, 9, 12], 't', 0, 'Dropping down and springing back to where you started'],
    [25, 'Minor slingshot', 'r', '8 8 8 ♭7 5 ♭7 8', [12, 12, 12, 10, 7, 10, 12], 't', 0, 'The slingshot with a minor colour'],
    [26, '“Mum” drop', 'r', '8 8 8 8 5 3 1', [12, 12, 12, 12, 7, 4, 0], 't', 0, 'Repeated top notes, then a clean drop home'],
    [27, 'Pentatonic turn', 'r', '3 5 3 2 1', [4, 7, 4, 2, 0], 't', 0, 'A small up-and-down turn before you land'],
    [28, 'R&amp;B trill', 'r', '3 2 3 2 3 2 1', [4, 2, 4, 2, 4, 2, 0], 't', [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1], 'A fast, even shake between two notes'],
    [29, 'Ninth riff', 'r', '5 6 8 9 – 8 6 5', [7, 9, 12, 14, 12, 9, 7], 't', [1, 1, 1, 2, 1, 1, 1], 'Reaching for, and resting on, the soulful 9th'],
    [30, 'Turnaround', 'r', '121 · 343 · 565 · 343 · 1', [0, 2, 0, 4, 5, 4, 7, 9, 7, 4, 5, 4, 0], 't', [1, 0.5, 1.5, 1, 0.5, 1.5, 1, 0.5, 1.5, 1, 0.5, 1.5, 1], 'Little neighbour-note turns, climbing and coming back'],
    [31, 'Pentatonic run', 'r', '1 2 3 5 6 8 6 5 3 2 1', [0, 2, 4, 7, 9, 12, 9, 7, 4, 2, 0], 'l', 0, 'Up and down the riff scale in one go'],
    [32, 'Scale skip', 'r', '8 7 6 5 3 2 1', [12, 11, 9, 7, 4, 2, 0], 'l', 0, 'A fast falling run that skips one step'],
    [33, 'Climb and fall', 'r', '1 · 235 · 568 · 653 · 321', [0, 2, 4, 7, 7, 9, 12, 9, 7, 4, 4, 2, 0], 'l', [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'A wide run sung in small groups'],
    [34, 'Extended riff', 'r', '6 5 3 2 1 2 3 2 1 1', [9, 7, 4, 2, 0, 2, 4, 2, 0, 0], 'l', 0, 'A long riff that turns back on itself'],
    [35, 'Falling threes', 'r', '865 · 653 · 532 · 321', [12, 9, 7, 9, 7, 4, 7, 4, 2, 4, 2, 0], 'l', 0, 'Sequencing: one small shape, repeated a step lower'],
    [36, 'Falling fours', 'r', '8653 · 6532 · 5321', [12, 9, 7, 4, 9, 7, 4, 2, 7, 4, 2, 0], 'l', 0, 'The gospel move: a four-note shape stepping down'],
    [37, 'Rising threes', 'r', '123 · 235 · 356 · 568', [0, 2, 4, 2, 4, 7, 4, 7, 9, 7, 9, 12], 'l', 0, 'Sequencing on the way up'],
    [38, 'Long pentatonic run', 'r', '1 2 3 5 6 8 9 10 9 8 6 5 3 2 1', [0, 2, 4, 7, 9, 12, 14, 16, 14, 12, 9, 7, 4, 2, 0], 'l', 0, 'Stamina and agility over a wide range'],
    [39, 'Falsetto flip', 'r', '1 5 8 – 6 5 3 2 1', [0, 7, 12, 9, 7, 4, 2, 0], 'l', [1, 1, 2, 0.5, 0.5, 0.5, 0.5, 1], 'Flipping into falsetto at the top, then running down'],
    [40, 'Soulful minor run', 'r', '8 ♭7 5 4 ♭3 1', [12, 10, 7, 5, 3, 0], 'm', 0, 'The minor pentatonic run, coming down'],
    [41, 'Minor five-note scale', 'r', '1 2 ♭3 4 5 4 ♭3 2 1', [0, 2, 3, 5, 7, 5, 3, 2, 0], 'm', 0, 'Tuning the minor 3rd'],
    [42, 'Minor pentatonic', 'r', '1 ♭3 4 5 ♭7 8 ♭7 5 4 ♭3 1', [0, 3, 5, 7, 10, 12, 10, 7, 5, 3, 0], 'm', 0, 'The minor riff scale, up and down'],
    [43, 'Dorian scale', 'r', '1 2 ♭3 4 5 6 ♭7 8 ♭7 6 5 4 ♭3 2 1', [0, 2, 3, 5, 7, 9, 10, 12, 10, 9, 7, 5, 3, 2, 0], 'm', 0, 'The neo-soul minor, with its brighter 6th'],
    [44, 'Blues run', 'r', '8 ♭7 5 ♭5 4 ♭3 1', [12, 10, 7, 6, 5, 3, 0], 'm', 0, 'A falling run through the blue note'],
    [45, 'Blues scale', 'r', '1 ♭3 4 ♭5 5 ♭7 8 ♭7 5 ♭5 4 ♭3 1', [0, 3, 5, 6, 7, 10, 12, 10, 7, 6, 5, 3, 0], 'm', 0, 'The full blues scale, up and down'],
    [46, 'Gospel run', 'r', '8 6 5 3 ♭3 2 1', [12, 9, 7, 4, 3, 2, 0], 'm', 0, 'A run with the slide from ♭3 into the 3rd'],
    [47, 'Gospel climb', 'r', '1 2 ♭3 3 5 6 8', [0, 2, 3, 4, 7, 9, 12], 'm', 0, 'The same gospel colour, going up'],
    [48, 'Chromatic five', 'r', '1 ♯1 2 ♯2 3 ♯2 2 ♯1 1', [0, 1, 2, 3, 4, 3, 2, 1, 0], 'm', 0, 'Tiny half-steps, each one in tune'],
    [49, 'Octave flip', 'x', '1 8 · 1 8 · 1 8', [0, 12, 0, 12, 0, 12], 0, 0, 'The big flip from full voice into falsetto'],
    [50, 'Fifth flip', 'x', '1 5 · 1 5 · 1 5', [0, 7, 0, 7, 0, 7], 0, 0, 'A smaller flip, to find where your voice breaks'],
    [51, 'Flip ladder', 'x', '1 3 · 1 5 · 1 6 · 1 8', [0, 4, 0, 7, 0, 9, 0, 12], 0, 0, 'Flipping on bigger and bigger jumps'],
    [52, 'Quick flips', 'x', '5 8 5 8 5 8 5', [7, 12, 7, 12, 7, 12, 7], 0, [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1], 'Switching fast between full voice and falsetto'],
    [53, 'Flip and fall', 'x', '5 8 – 6 5 ×3', [7, 12, 9, 7, 7, 12, 9, 7, 7, 12, 9, 7], 0, [1, 2, 0.5, 1, 1, 2, 0.5, 1, 1, 2, 0.5, 1], 'Flipping up, then settling back into full voice'],
    [54, 'Reverse flip', 'x', '8 1 · 8 1 · 8 1', [12, 0, 12, 0, 12, 0], 0, 0, 'Coming from falsetto back into full voice'],
    [55, 'Run-up flip', 'x', '1 2 3 5 8 – ×2', [0, 2, 4, 7, 12, 0, 2, 4, 7, 12], 0, [0.5, 0.5, 0.5, 0.5, 2, 0.5, 0.5, 0.5, 0.5, 1], 'A quick run that flips on the top note'],
    [56, 'Glide-up flip', 'x', '1 (5) 8 ×3', [0, 7, 12, 0, 7, 12, 0, 7, 12], 0, [1, 0.35, 1.65, 1, 0.35, 1.65, 1, 0.35, 1.65], 'Gliding through the middle so the flip lands on top'],
    [57, 'Glide-down flip', 'x', '8 (5) 1 ×3', [12, 7, 0, 12, 7, 0, 12, 7, 0], 0, [1, 0.35, 1.65, 1, 0.35, 1.65, 1, 0.35, 1.65], 'Coming down from falsetto without catching on the way'],
    [58, 'Flick flip', 'x', '5 (8) 6 ×3', [7, 12, 9, 7, 12, 9, 7, 12, 9], 0, [1, 0.35, 1.65, 1, 0.35, 1.65, 1, 0.35, 1.65], 'Touching falsetto lightly and landing on the note below'],
    [59, 'Small flick', 'x', '3 (6) 5 ×3', [4, 9, 7, 4, 9, 7, 4, 9, 7], 0, [1, 0.35, 1.65, 1, 0.35, 1.65, 1, 0.35, 1.65], 'The flick on a smaller jump, lower in your voice'],
    [60, 'Flick and run', 'x', '5 (8) 6 5 3 2 1', [7, 12, 9, 7, 4, 2, 0], 0, [1, 0.35, 1.15, 0.5, 0.5, 0.5, 1], 'A flick that leads straight into a run down'],
  ].map(([n, name, g, steps, semi, sub, rh, line]) => ({
    n,
    name,
    g,
    steps,
    semi,
    sub: sub || null,
    rh: rh || null,
    line,
  }));
  const byN = (n) => LIB.find((p) => p.n === +n) || null;
  const GROUPS = [
    ['f', 'Favourites'],
    ['w', 'Warm-ups'],
    ['a', 'Agility'],
    ['r', 'Riffs and runs'],
    ['x', 'Flips'],
  ];
  const SUBS = [
    ['s', 'Short riffs'],
    ['t', 'Turns and slingshots'],
    ['l', 'Long runs'],
    ['m', 'Minor, blues and gospel'],
  ];
  // Favourites start with riffs in Bruno Mars's style: pentatonic runs, the falsetto flip, gospel-soul runs and
  // minor-pentatonic funk. Removing them all leaves an empty state
  const FAV_SEED = [22, 31, 33, 36, 39, 46, 40, 44];
  const GROUP_NOTE = {
    f: 'Started with riffs in Bruno Mars’s style: pentatonic runs, the falsetto flip, gospel-soul runs and minor-pentatonic funk. Tap the star on any pattern to add or remove it.',
    r: 'A dash ( – ) means hold the note before it a little longer. Riffs use the pentatonic scale unless they show a ♭ or ♯.',
    x: 'Sing the low notes in full voice and flip into falsetto on the high ones. Let the break be clean and light, and repeat it until the flip is easy. A note in brackets is a quick touch: glide through it on the way rather than landing on it. These are checked against your falsetto top.',
  };
  // a pattern is minor if it uses the ♭3 or ♭7 and never the major 3rd (minor pentatonic, blues, Dorian, the minor
  // slingshot): its round chord and home chord are then minor, so you never sing a ♭3 over a major chord
  const isMinor = (p) => {
    const m = new Set(p.semi.filter((v) => v !== null).map((v) => ((v % 12) + 12) % 12));
    return !m.has(4) && (m.has(3) || m.has(10));
  };
  const quick = (p, i) => !!(p.rh && p.rh[i] < 0.5); // a quick touch
  const lenOf = (p, i) => (p.rh && p.rh[i]) || 1;
  const lo = (p) => Math.min(...p.semi.filter((v) => v !== null));
  const hi = (p) => Math.max(...p.semi.filter((v) => v !== null));

  /* ===== Speeds, voices and notes ===== */
  // 12 fixed stops; beat = 0.36 s at 1×
  const SPEEDS = [0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.35, 1.5, 1.75, 2];
  const ONE = 5;
  const spLabel = (i) => String(SPEEDS[i]) + '×';
  const beatOf = (i) => 0.36 / SPEEDS[i];
  // [lowest comfortable, highest comfortable, falsetto top] as MIDI notes (tenor G♯2 · A4 · D5)
  const VOICES = {
    Bass: [40, 64, 72],
    Baritone: [45, 67, 72],
    Tenor: [44, 69, 74],
    Alto: [53, 74, 77],
    Mezzo: [57, 77, 81],
    Soprano: [60, 81, 84],
  };
  const NAMES = ['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B'];
  const nameOf = (m) => NAMES[((m % 12) + 12) % 12] + (Math.floor(m / 12) - 1);
  // 'C3 B2 A♯2…' (♯ or #) → MIDI numbers, moved by shift semitones
  function notes(str, shift) {
    return String(str || '')
      .split(/\s+/)
      .filter(Boolean)
      .map((s) => {
        const m = /^([A-G])([#♯]?)(-?\d)$/.exec(s);
        return m ? 12 * (+m[3] + 1) + 'C D EF G A B'.indexOf(m[1]) + (m[2] ? 1 : 0) + (shift || 0) : null;
      })
      .filter((x) => x !== null);
  }

  /* ===== Saved choices (D.prefs.pat, in backups) ===== */
  const SOUND_IDS = ['soft', 'piano', 'ep'];
  const ENDINGS = ['chord', 'note', 'off'];
  const VOWELS = ['ex', 'all', 'off'];
  const DRAWN = ['dots', 'notes'];
  const DEF = {
    sound: 'soft',
    drone: true,
    cue: true,
    ending: 'chord',
    vowel: 'ex',
    notes: 'dots',
    stopTop: false,
    ramp: false,
    stopLast: false, // Q38 Stop one past last time
    bcue: true, // Q38 the bridge cue ("Thinner · quieter")
    listen: false, // Q38 Listen while I sing
  };
  const isInt = (x, a, b) => Number.isInteger(x) && x >= a && x <= b;
  // checks what's saved, dropping only what's malformed and keeping anything it doesn't know (a newer version's)
  function clean(p) {
    if (!p || typeof p !== 'object' || Array.isArray(p)) return undefined;
    const o = Object.assign({}, p);
    if (o.ex != null) {
      if (!o.ex || typeof o.ex !== 'object' || Array.isArray(o.ex)) delete o.ex;
      else {
        o.ex = Object.assign({}, o.ex);
        for (const k in o.ex) {
          const e = o.ex[k];
          if (!e || typeof e !== 'object' || Array.isArray(e)) {
            delete o.ex[k];
            continue;
          }
          const c = Object.assign({}, e);
          if (c.p != null && !(isInt(c.p, 1, 999) && byN(c.p))) delete c.p;
          if (c.off != null && !isInt(c.off, -36, 36)) delete c.off;
          // Q38 Last time: the highest round top held cleanly while listening, {m, at}
          if (c.last != null && !(c.last && isInt(c.last.m, 24, 108) && isFinite(c.last.at) && c.last.at > 0)) delete c.last;
          else if (c.last != null) c.last = Object.assign({}, c.last);
          o.ex[k] = c;
        }
      }
    }
    if (o.spd != null) {
      if (!o.spd || typeof o.spd !== 'object' || Array.isArray(o.spd)) delete o.spd;
      else {
        o.spd = Object.assign({}, o.spd);
        for (const k in o.spd) if (!isInt(o.spd[k], 0, SPEEDS.length - 1)) delete o.spd[k];
      }
    }
    if (o.fav != null) {
      if (!Array.isArray(o.fav)) delete o.fav;
      else o.fav = o.fav.filter((n, i, a) => isInt(n, 1, 999) && byN(n) && a.indexOf(n) === i);
    }
    if (o.voice != null) {
      const v = o.voice;
      if (
        !v ||
        typeof v !== 'object' ||
        !(VOICES[v.type] || v.type === 'Custom') ||
        !isInt(v.lo, 24, 108) ||
        !isInt(v.hi, 24, 108) ||
        !isInt(v.fal, 24, 108)
      )
        delete o.voice;
      else {
        o.voice = Object.assign({}, v);
        // Q38 your bridge, {lo, hi}: a bad one goes, the voice stays
        const b = o.voice.bridge;
        if (b != null) {
          if (!b || !isInt(b.lo, 24, 108) || !isInt(b.hi, 24, 108) || b.lo > b.hi) delete o.voice.bridge;
          else o.voice.bridge = Object.assign({}, b);
        }
      }
    }
    if (o.sound != null && typeof o.sound !== 'string') delete o.sound; // an unknown sound id falls back to Soft tone
    ['drone', 'cue', 'stopTop', 'ramp', 'stopLast', 'bcue', 'listen'].forEach((k) => {
      if (o[k] != null && typeof o[k] !== 'boolean') delete o[k];
    });
    if (o.ending != null && !ENDINGS.includes(o.ending)) delete o.ending;
    if (o.vowel != null && !VOWELS.includes(o.vowel)) delete o.vowel;
    if (o.notes != null && !DRAWN.includes(o.notes)) delete o.notes;
    return o;
  }
  function P() {
    if (!D.prefs || typeof D.prefs !== 'object') D.prefs = {};
    if (!D.prefs.pat || typeof D.prefs.pat !== 'object') D.prefs.pat = {};
    return D.prefs.pat;
  }
  const opt = (k) => {
    const v = D.prefs && D.prefs.pat ? D.prefs.pat[k] : undefined;
    return v == null ? DEF[k] : v;
  };
  function put(k, v) {
    P()[k] = v;
    save();
  }
  const voice = () => {
    const v = D.prefs && D.prefs.pat && D.prefs.pat.voice;
    if (v) return v;
    const t = VOICES.Tenor;
    return { type: 'Tenor', lo: t[0], hi: t[1], fal: t[2] };
  };
  const favs = () => {
    const f = D.prefs && D.prefs.pat && D.prefs.pat.fav;
    return Array.isArray(f) ? f : FAV_SEED.slice();
  };
  // Q38 your bridge: {lo, hi} (MIDI), saved with Your voice, or null
  const bridge = () => {
    const b = voice().bridge;
    return b && isFinite(b.lo) && isFinite(b.hi) ? b : null;
  };
  const inZone = (n) => {
    const b = bridge();
    return !!b && n >= b.lo && n <= b.hi;
  };
  const zoneName = (b) => nameOf(b.lo) + (b.hi === b.lo ? '' : '–' + nameOf(b.hi));
  function setBridge(lo, hi) {
    const o = Object.assign({}, voice());
    o.bridge = { lo: Math.min(lo, hi), hi: Math.max(lo, hi) };
    put('voice', o);
  }
  // Q39: a guest (Practise in <key>, from a song) keeps its pattern and starting note in memory only, so opening the
  // player from outside never changes an exercise's saved choices
  const guestOf = (k) => (cfg && cfg.guest && cfg.key === k ? cfg.gx : null);
  const exPref = (k) => guestOf(k) || (D.prefs && D.prefs.pat && D.prefs.pat.ex && D.prefs.pat.ex[k]) || {};
  function putEx(k, f, v) {
    const g = guestOf(k);
    if (g) {
      if (v == null) delete g[f];
      else g[f] = v;
      return;
    }
    const p = P();
    p.ex = p.ex || {};
    const e = Object.assign({}, p.ex[k] || {});
    if (v == null) delete e[f];
    else e[f] = v;
    if (Object.keys(e).length) p.ex[k] = e;
    else delete p.ex[k];
    save();
  }

  /* ===== The page using it (use) =====
     {key: saved under (the exercise id), name, col: its colour, route: key notes (MIDI) of each round, or none,
      def: the default pattern's number, syl: what you sing ('hmmm', 'hoo hee hoh'), vowels: sung on open vowels (the
      vowel cue shows with scale patterns), fal: high notes are in falsetto (checked against the falsetto top)} */
  let cfg = null;
  const S = { playing: false, round: 0, hold: false, rampOff: 0, played: 0, preview: null, group: null, homeUntil: 0, lastSnap: null };
  function use(o) {
    const was = cfg;
    cfg = o || null;
    if (was && cfg && (was.key !== cfg.key || String(was.route) !== String(cfg.route))) {
      if (S.playing) stop();
      S.round = 0;
      S.hold = false;
    }
  }
  const pat = () => (cfg && byN(exPref(cfg.key).p || cfg.def)) || byN((cfg && cfg.def) || 1);
  const off = () => (cfg ? exPref(cfg.key).off || 0 : 0);
  const baseIx = () => {
    const v = (D.prefs && D.prefs.pat && D.prefs.pat.spd ? D.prefs.pat.spd : {})[pat().n];
    return v == null ? ONE : v;
  };
  // Speed up each round: one stop faster each round while playing, up to 2×. The saved speed isn't changed
  const spdIx = () => Math.min(SPEEDS.length - 1, baseIx() + (S.playing ? S.rampOff : 0));
  const useFal = () => !!(cfg && cfg.fal) || pat().g === 'x'; // flips go up into falsetto
  const top = () => (useFal() ? voice().fal : voice().hi);
  function full() {
    if (!cfg || !cfg.route || !cfg.route.length) return [];
    const out = [];
    cfg.route.forEach((m) => {
      const k = m + off();
      if (out[out.length - 1] !== k) out.push(k);
    });
    return out;
  }
  // Q38 Last time on this exercise ({m, at}): while playing, as it was when Play was pressed, so the route holds still
  const lastNow = () => (cfg ? exPref(cfg.key).last || null : null);
  const lastFor = () => (S.playing ? S.lastSnap : lastNow());
  // Stop at my top note: the route ends before the first round that goes above your top (low dips come early).
  // Q38 Stop one past last time: it ends with the first round whose top goes past Last time. Both on: the earlier wins
  function route() {
    const f = full(),
      p = pat();
    let n = f.length;
    if (opt('stopTop')) {
      const ix = f.findIndex((k) => k + hi(p) > top());
      if (ix >= 0) n = Math.min(n, Math.max(1, ix));
    }
    const lt = opt('stopLast') && lastFor();
    if (lt) {
      const ix = f.findIndex((k) => k + hi(p) > lt.m);
      if (ix >= 0) n = Math.min(n, ix + 1);
    }
    return n < f.length ? f.slice(0, n) : f;
  }
  const keyNow = () => {
    const r = route();
    return r.length ? r[Math.min(S.round, r.length - 1)] : 60;
  };
  // where the route goes outside your range: {lo, hi, out: [{kind, note, at}]}
  function rangeCheck() {
    const r = full(),
      p = pat();
    if (!r.length) return null;
    let l = 1e9,
      h = -1e9,
      hAt = 0,
      lAt = 0;
    r.forEach((k, i) => {
      if (k + hi(p) > h) {
        h = k + hi(p);
        hAt = i;
      }
      if (k + lo(p) < l) {
        l = k + lo(p);
        lAt = i;
      }
    });
    const out = [];
    if (h > top()) out.push({ kind: 'high', note: h, at: hAt });
    if (l < voice().lo) out.push({ kind: 'low', note: l, at: lAt });
    return { lo: l, hi: h, out };
  }
  const outOf = (n) => n > top() || n < voice().lo;
  const roundOut = (k) => k + hi(pat()) > top() || k + lo(pat()) < voice().lo;
  const yourT = () => (voice().type === 'Custom' ? 'your' : 'your ' + voice().type.toLowerCase());
  function warnText(w, short) {
    return w.kind === 'high'
      ? short
        ? 'reaches ' + nameOf(w.note) + ', above ' + yourT() + ' top'
        : 'Reaches ' +
          nameOf(w.note) +
          ' by round ' +
          (w.at + 1) +
          ' · above ' +
          yourT() +
          ' top (' +
          nameOf(top()) +
          ')'
      : short
        ? 'dips to ' + nameOf(w.note) + ', below ' + yourT() + ' bottom'
        : 'Dips to ' +
          nameOf(w.note) +
          ' in round ' +
          (w.at + 1) +
          ' · below ' +
          yourT() +
          ' bottom (' +
          nameOf(voice().lo) +
          ')';
  }

  /* ===== Sound ===== */
  let AC = null,
    master = null,
    bus = null,
    keep = null;
  // a tiny silent WAV, looped, so iOS treats the page as playing media and the silent switch doesn't mute it
  function silent() {
    const n = 800,
      b = new Uint8Array(44 + n),
      dv = new DataView(b.buffer),
      w = (o, s) => [...s].forEach((c, i) => (b[o + i] = c.charCodeAt(0)));
    w(0, 'RIFF');
    dv.setUint32(4, 36 + n, true);
    w(8, 'WAVEfmt ');
    dv.setUint32(16, 16, true);
    dv.setUint16(20, 1, true);
    dv.setUint16(22, 1, true);
    dv.setUint32(24, 8000, true);
    dv.setUint32(28, 8000, true);
    dv.setUint16(32, 1, true);
    dv.setUint16(34, 8, true);
    w(36, 'data');
    dv.setUint32(40, n, true);
    b.fill(128, 44);
    let s = '';
    b.forEach((x) => (s += String.fromCharCode(x)));
    return 'data:audio/wav;base64,' + btoa(s);
  }
  function unmute() {
    try {
      if (!keep) {
        keep = new Audio(silent());
        keep.loop = true;
        keep.setAttribute('playsinline', '');
        keep.setAttribute('x-webkit-airplay', 'deny');
      }
      if (keep.paused) {
        const p = keep.play();
        if (p && p.catch) p.catch(() => {});
      }
    } catch (e) {}
  }
  // in a tap: the context made or woken, and the silent loop started
  function audio() {
    unmute();
    if (!AC) {
      try {
        if (navigator.audioSession) navigator.audioSession.type = 'playback';
      } catch (e) {}
      const C = window.AudioContext || window.webkitAudioContext;
      if (!C) return null;
      try {
        AC = new C();
      } catch (e) {
        return null;
      }
      const comp = AC.createDynamicsCompressor();
      comp.threshold.value = -14;
      comp.ratio.value = 4;
      master = AC.createGain();
      master.gain.value = 0.9;
      master.connect(comp);
      comp.connect(AC.destination);
    }
    if (AC.state !== 'running')
      try {
        Promise.resolve(AC.resume()).catch(() => {});
      } catch (e) {}
    return AC;
  }
  const hz = (m) => 440 * Math.pow(2, (m - 69) / 12);
  /* The sound library. Each sound is one entry: an id that's saved, a name, and play(), which makes one note:
     frequency f, start t, length d, into the gain node out, at volume v. Adding a sound is adding an entry here. */
  const SOUNDS = [
    {
      id: 'soft',
      name: 'Soft tone',
      play(f, t, d, out, v) {
        const o = AC.createOscillator(),
          o2 = AC.createOscillator(),
          g2 = AC.createGain();
        o.type = 'sine';
        o2.type = 'triangle';
        o.frequency.value = f;
        o2.frequency.value = f;
        g2.gain.value = 0.18;
        o.connect(out);
        o2.connect(g2);
        g2.connect(out);
        out.gain.setValueAtTime(0, t);
        out.gain.linearRampToValueAtTime(0.32 * v, t + 0.03);
        out.gain.setValueAtTime(0.32 * v, t + d);
        out.gain.linearRampToValueAtTime(0, t + d + 0.09);
        [o, o2].forEach((x) => {
          x.start(t);
          x.stop(t + d + 0.12);
        });
      },
    },
    {
      id: 'piano',
      name: 'Piano-ish',
      play(f, t, d, out, v) {
        const hold = Math.max(d, 0.25),
          end = t + hold + 0.5,
          low = f < 165;
        out.gain.value = v;
        [
          [1, 1, 1.6],
          [2, 0.55, 1.1],
          [3, 0.32, 0.8],
          [4, 0.2, 0.6],
          [5, 0.12, 0.45],
          [6, 0.07, 0.35],
          [8, 0.035, 0.25],
        ].forEach(([n, a, dec]) => {
          const o = AC.createOscillator(),
            pg = AC.createGain(),
            peak = 0.3 * a,
            rest = Math.max(peak * 0.18, 0.0004);
          o.frequency.value = f * n * (1 + 0.00035 * n * n);
          o.connect(pg);
          pg.connect(out);
          pg.gain.setValueAtTime(0, t);
          pg.gain.linearRampToValueAtTime(peak, t + 0.004);
          pg.gain.exponentialRampToValueAtTime(rest, t + dec * (low ? 1.4 : 1));
          pg.gain.setValueAtTime(rest, t + hold);
          pg.gain.exponentialRampToValueAtTime(0.0001, end);
          o.start(t);
          o.stop(end + 0.02);
        });
      },
    },
    {
      id: 'ep',
      name: 'Electric piano',
      play(f, t, d, out, v) {
        const c = AC.createOscillator(),
          md = AC.createOscillator(),
          mg = AC.createGain(),
          b = AC.createOscillator(),
          bg = AC.createGain();
        c.frequency.value = f;
        md.frequency.value = f;
        b.frequency.value = f * 14;
        md.connect(mg);
        mg.connect(c.frequency);
        b.connect(bg);
        bg.connect(c.frequency);
        c.connect(out);
        mg.gain.setValueAtTime(f * 1.6, t);
        mg.gain.exponentialRampToValueAtTime(f * 0.25, t + 0.6);
        bg.gain.setValueAtTime(f * 0.9, t);
        bg.gain.exponentialRampToValueAtTime(1, t + 0.12);
        const end = t + d + 0.35;
        out.gain.setValueAtTime(0, t);
        out.gain.linearRampToValueAtTime(0.34 * v, t + 0.006);
        out.gain.exponentialRampToValueAtTime(0.12 * v, t + Math.min(1.2, d + 0.2));
        out.gain.setValueAtTime(0.12 * v, t + d);
        out.gain.exponentialRampToValueAtTime(0.0005, end);
        [c, md, b].forEach((x) => {
          x.start(t);
          x.stop(end + 0.02);
        });
      },
    },
  ];
  const soundOf = (id) => SOUNDS.find((x) => x.id === id) || SOUNDS[0];
  function note(m, t, d, out, id, v) {
    const g = AC.createGain();
    g.connect(out);
    soundOf(id).play(hz(m), t, d, g, v || 1);
  }
  // a fresh output for what's about to play; the old one fades out (Stop: about a third of a second)
  function newBus(fade) {
    if (bus) {
      const b = bus;
      b.gain.setTargetAtTime(0, AC.currentTime, fade || 0.04);
      setTimeout(() => b.disconnect(), 700);
    }
    bus = AC.createGain();
    bus.connect(master);
    return bus;
  }
  // a chord, rolled slightly like a hand on the keys
  function chord(ns, t, d, out, v) {
    ns.forEach((m, i) => note(m, t + i * 0.03, d, out, opt('sound'), v));
  }
  const triad = (k, p) => [k - 12, k, k + (isMinor(p || pat()) ? 3 : 4), k + 7];
  const homeNotes = (k) => (opt('ending') === 'note' ? [k - 12, k] : triad(k));
  // one round: the pattern on key k from t0 at beat b. Returns its notes' times (for the drawing) and when it ends.
  // soft (Q38, the exercise page): notes in your bridge play at BRIDGE_VOL and are marked br for the cue
  const BRIDGE_VOL = 0.55;
  function round(k, t0, p, b, soft) {
    const ns = [];
    let t = t0;
    p.semi.forEach((s, i) => {
      if (s === null) {
        t += b;
        ns.push(null);
        return;
      }
      const last = i === p.semi.length - 1,
        len = last ? b * 2.2 : b * lenOf(p, i),
        q = quick(p, i),
        br = !!soft && inZone(k + s);
      note(k + s, t, last ? len : len * (q ? 1.1 : 0.92), bus, opt('sound'), (q ? 0.6 : 1) * (br ? BRIDGE_VOL : 1));
      ns.push({ t, d: len, i, br, v: (q ? 0.6 : 1) * (br ? BRIDGE_VOL : 1) });
      t += len;
    });
    if (opt('drone')) {
      const dg = AC.createGain();
      dg.gain.value = 0.5;
      dg.connect(bus);
      note(k - 12, t0, t - t0, dg, 'soft', 0.9); // the held note underneath: the key an octave down, in Soft tone
    }
    return { ns, end: t };
  }

  /* ===== Playing ===== */
  let timer = 0,
    sched = [],
    homeT = 0;
  const runs = []; // the last 40 rounds played ({k, n, spd, at}), for the tests
  function halt() {
    // stopped by another sound starting (NOW): quietly, no home ending
    end(false, true);
  }
  function play() {
    if (!cfg || !route().length) return;
    if (S.playing) return stop();
    if (!audio()) return toast('This browser can’t play sounds');
    stopPreview(true);
    NOW.start('pattern', cfg.key, halt);
    S.lastSnap = lastNow(); // Q38: the route holds still while Last time moves
    S.headX = null;
    S.playing = true;
    S.rampOff = 0;
    S.played = 0;
    if (S.round >= route().length) S.round = 0;
    newBus();
    AWAKE.set('pat', true);
    next(AC.currentTime + 0.08);
    listenStart(); // Q38, in the tap
    paintAll();
    tick();
  }
  function next(t0) {
    const r = route();
    if (!S.playing) return;
    if (S.round >= r.length) return end(true);
    if (opt('ramp') && S.played > 0) S.rampOff = Math.min(SPEEDS.length - 1 - baseIx(), S.rampOff + 1);
    S.played++;
    const p = pat(),
      b = beatOf(spdIx()),
      k = r[S.round];
    let st = t0;
    if (opt('cue')) {
      chord(triad(k, p), t0, b * 1.6, bus, 0.55); // the new key's chord, then the pattern two beats later
      st = t0 + b * 2;
    }
    const res = round(k, st, p, b, true);
    sched = res.ns;
    // Q38 what the voice is checked against this round: its top note, held cleanly
    S.rTop = k + hi(p);
    S.rKey = k;
    HOLD.on = false;
    HOLD.done = false;
    if (LS) LS.trail.length = 0;
    runs.push({ k, n: p.n, spd: SPEEDS[spdIx()], hold: S.hold, at: Date.now(), vols: res.ns.filter(Boolean).map((x) => x.v) });
    if (runs.length > 40) runs.shift();
    lastLit = -2;
    redraw();
    paint();
    const gap = b * 2;
    clearTimeout(timer);
    timer = setTimeout(
      () => {
        if (!S.hold) S.round++;
        next(res.end + gap);
      },
      Math.max(0, (res.end + gap - AC.currentTime - 0.15) * 1000)
    );
  }
  function stop() {
    end(false);
  }
  // done: the route finished (the home ending plays); quiet: stopped by another sound
  function end(done, quiet) {
    if (!S.playing) return;
    S.playing = false;
    S.rampOff = 0;
    clearTimeout(timer);
    cancelAnimationFrame(raf);
    sched = [];
    listenStop(); // Q38
    S.rTop = null;
    S.rKey = null;
    S.cue = false;
    AWAKE.set('pat', false);
    if (AC && bus) bus.gain.setTargetAtTime(0, AC.currentTime, 0.12);
    if (!quiet) NOW.ended('pattern');
    if (done) {
      const n = route().length;
      S.round = 0;
      home();
      toast('Done · ' + n + (n === 1 ? ' round' : ' rounds'));
    }
    redraw();
    paintAll();
  }
  // the home ending: a short pause, then the starting key, left to ring, as a teacher does at the piano
  function home() {
    if (opt('ending') === 'off' || !AC) return;
    const r = route();
    if (!r.length) return;
    newBus();
    const t = AC.currentTime + 0.3;
    chord(homeNotes(r[0]), t, 1.9, bus, 0.75);
    S.homeUntil = Date.now() + 2700;
    clearTimeout(homeT);
    homeT = setTimeout(() => {
      S.homeUntil = 0;
      paint();
    }, 2800);
  }
  // a short sample (a new sound, a starting note, an ending): through NOW, like everything that makes sound
  function sample(fn) {
    if (!audio()) return;
    if (S.playing) return;
    stopPreview(true);
    NOW.start('pattern', 'sample', () => bus && bus.gain.setTargetAtTime(0, AC.currentTime, 0.05));
    newBus();
    fn(AC.currentTime + 0.05);
  }

  /* ===== One note (Q37): the song ladder's note buttons =====
     tone(m, {repeat, onEnd}) plays one note in the player's sound, through NOW like everything that makes sound. With
     repeat it strikes again every 1.5 s until toneStop() or another sound starts; onEnd is called once it has stopped,
     however it stopped. */
  const TONE_EVERY = 1500,
    TONE_LEN = 1.1;
  let toneT = 0,
    toneNow = null; // {m, repeat, onEnd}
  function tone(m, o) {
    o = o || {};
    if (!isFinite(m) || !audio()) return false;
    toneStop();
    if (S.playing) end(false, true);
    stopPreview(true);
    NOW.start('pattern', 'tone', () => toneStop(true));
    toneNow = { m, repeat: !!o.repeat, onEnd: o.onEnd };
    const me = toneNow,
      strike = () => {
        if (toneNow !== me) return;
        newBus();
        note(m, AC.currentTime + 0.02, TONE_LEN, bus, opt('sound'), 1);
        me.strikes = (me.strikes || 0) + 1;
      };
    strike();
    if (me.repeat) toneT = setInterval(strike, TONE_EVERY);
    else toneT = setTimeout(() => toneNow === me && toneStop(), (TONE_LEN + 0.5) * 1000);
    return true;
  }
  // byNow: another sound started (NOW already moved on)
  function toneStop(byNow) {
    clearInterval(toneT);
    clearTimeout(toneT);
    toneT = 0;
    const t = toneNow;
    if (!t) return;
    toneNow = null;
    if (AC && bus) bus.gain.setTargetAtTime(0, AC.currentTime, 0.08);
    if (!byNow) NOW.ended('pattern', 'tone');
    if (t.onEnd)
      try {
        t.onEnd();
      } catch (e) {}
  }
  document.addEventListener('visibilitychange', () => document.hidden && toneStop());

  /* ===== Listening (Q38): the microphone, for Find your bridge and Listen while I sing =====
     Through the shared audio service (AUDIO.listen, its own context, which only ever hears the microphone) and the
     pitch listener (PITCH.live on one 2048 analyser, on the shared frame clock). The pattern's sound stays on this
     player's own context. Nothing is recorded. While the microphone is open the page's audio session is
     'play-and-record' (where Safari has navigator.audioSession), then back to 'playback'. */
  const session = (t) => {
    try {
      if (navigator.audioSession) navigator.audioSession.type = t;
    } catch (e) {}
  };
  const MIC_OPTS = { channelCount: 1, echoCancellation: false, noiseSuppression: false, autoGainControl: false };
  // fn(points, last) as PITCH.live gives them; onFail('blocked' | 'none'). Call it in a tap. Returns stop()
  function micOpen(fn, onFail) {
    const me = { off: false, stop: null },
      back = () => session(AC ? 'playback' : 'auto'),
      fail = (why) => {
        if (me.off) return;
        me.off = true;
        back();
        if (onFail) onFail(why);
      };
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !PITCH.has()) {
      setTimeout(() => fail('none'));
      return () => (me.off = true);
    }
    AUDIO.wake(); // in the tap: iOS only starts a context from one
    session('play-and-record');
    navigator.mediaDevices
      .getUserMedia({ audio: MIC_OPTS })
      .then((stream) => {
        const drop = () => stream.getTracks().forEach((t) => t.stop());
        if (me.off) return drop();
        const mic = AUDIO.listen(stream);
        if (!mic) {
          drop();
          return fail('none');
        }
        const off = PITCH.live(mic.analyser(2048), fn);
        me.stop = () => {
          off();
          mic.close();
          drop();
        };
      })
      .catch(() => fail('blocked'));
    return () => {
      if (me.off) return;
      me.off = true;
      if (me.stop) me.stop();
      me.stop = null;
      back();
    };
  }

  /* Listen while I sing: while the pattern plays, your voice as a dot and a 1 s trail on the drawing (painted by
     tick(), nothing looked up per frame), and Last time: the round's top held cleanly (HOLD) moves it up quietly */
  let LS = null; // {stop, trail: [{x, y, at}], last: {m, at}, n}
  const HOLD = { on: false, t0: 0, lastT: 0, done: false };
  const MIC_FAIL = {
    blocked: 'Microphone access was blocked. Allow it in Settings, then try again.',
    none: 'Listening isn’t supported in this browser',
  };
  function listenStart() {
    if (LS || !S.playing || !opt('listen')) return;
    const me = { trail: [], last: null, n: 0, stop: null };
    LS = me;
    me.stop = micOpen(
      (pts, p) => heard(me, p),
      (why) => {
        if (LS !== me) return;
        LS = null;
        toast(MIC_FAIL[why] || MIC_FAIL.none);
      }
    );
  }
  function listenStop() {
    const l = LS;
    LS = null;
    HOLD.on = false;
    if (l && l.stop) l.stop();
  }
  // a note's height on the drawing of the round now playing (as geom() places the pattern's notes)
  function yOfNote(m) {
    const p = pat(),
      l = lo(p),
      h = hi(p),
      s = m - (S.rKey == null ? keyNow() : S.rKey),
      y = h === l ? H / 2 - (s - l) * 8 : 96 - ((s - l) * 80) / (h - l);
    return Math.max(4, Math.min(H - 8, y));
  }
  function heard(me, p) {
    if (LS !== me || !S.playing) return;
    if (!p) {
      me.last = null;
      HOLD.on = false;
      return;
    }
    me.n++;
    me.last = { m: p.m, at: performance.now() };
    me.trail.push({ x: S.headX == null ? 14 : S.headX, y: yOfNote(p.m), at: me.last.at });
    while (me.trail.length && me.last.at - me.trail[0].at > 1000) me.trail.shift();
    // Last time: 250 ms or more within 1 semitone of the round's top, no gap, no jump
    if (S.rTop == null || !cfg) return;
    if (Math.abs(p.m - S.rTop) <= HOLD_WITHIN) {
      if (!HOLD.on || p.t - HOLD.lastT > 0.06) {
        HOLD.on = true;
        HOLD.t0 = p.t;
      }
      HOLD.lastT = p.t;
      if (!HOLD.done && p.t - HOLD.t0 >= HOLD_MIN) {
        HOLD.done = true;
        heldTop(S.rTop);
      }
    } else HOLD.on = false;
  }
  const HOLD_MIN = 0.25,
    HOLD_WITHIN = 1;
  // a round's top held cleanly: Last time moves up, quietly (no message, no celebration)
  function heldTop(m) {
    const cur = lastNow();
    if (cur && cur.m >= m) return;
    putEx(cfg.key, 'last', { m, at: Date.now() });
    paint();
  }

  /* ===== Find your bridge (Q38): the sheet VS-096 =====
     One slow slide on "ee", drawn live with jump markers (PITCH.jumps on the line as it comes in). The first jump
     suggests the zone: 2 semitones below its lower note to 1 above. From and To steppers, Use this bridge, Try again.
     With no jump, you set it by feel. Doors: the exercise page's bridge line and Settings › Your voice. */
  const FB_MAX = 20, // s: listening stops itself
    FB_HOP = 0.01;
  const FB = { phase: 'ready', why: '', s: null, n: 0, li: -1, pts: [], t0: 0, t: 0, jumps: [], jump: null, top: null, lo: 0, hi: 0, stop: null, me: null, el: null, drawn: 0, feel: false };
  const defZone = () => ({ lo: voice().hi - 5, hi: voice().hi - 2 });
  function fbStop() {
    const st = FB.stop;
    FB.stop = null;
    FB.me = null;
    if (st) st();
  }
  function fbReset() {
    fbStop();
    const b = bridge() || defZone();
    Object.assign(FB, { phase: 'ready', why: '', s: null, n: 0, li: -1, pts: [], t: 0, jumps: [], jump: null, top: null, el: null, feel: false, lo: b.lo, hi: b.hi });
  }
  function fbOpen() {
    if (S.playing) end(false);
    toneStop();
    stopPreview(true);
    fbReset();
    U.sheet = 'bridge';
    U.sd = {};
    rerender();
  }
  function fbStart() {
    fbStop();
    NOW.stop(); // one sound at a time: whatever plays stops, so the microphone hears only you
    const me = {},
      b = bridge() || defZone();
    Object.assign(FB, { phase: 'listening', why: '', s: new Float32Array(Math.round(FB_MAX / FB_HOP) + 60).fill(NaN), n: 0, li: -1, pts: [], t0: performance.now(), t: 0, jumps: [], jump: null, top: null, el: null, drawn: 0, feel: false, lo: b.lo, hi: b.hi, me });
    FB.stop = micOpen(
      (pts, p) => fbHeard(me, pts, p),
      (why) => {
        if (FB.me !== me) return;
        FB.stop = null;
        FB.me = null;
        FB.phase = 'blocked';
        FB.why = why;
        rerender();
      }
    );
    rerender();
  }
  function fbHeard(me, pts, p) {
    if (FB.me !== me || FB.phase !== 'listening') return;
    FB.pts = pts;
    if (p) {
      // the line at 10 ms steps, as PITCH.jumps reads it: readings come once a frame, so a short gap holds the reading
      // before it (never drawn in between, which would smooth a jump away)
      const i = Math.round(p.t / FB_HOP);
      if (i < FB.s.length) {
        if (FB.li >= 0 && i > FB.li + 1 && i - FB.li <= 6) FB.s.fill(FB.s[FB.li], FB.li + 1, i);
        FB.s[i] = p.m;
        FB.li = i;
        FB.n = Math.max(FB.n, i + 1);
      }
      FB.t = p.t;
    }
    const now = performance.now();
    if ((now - FB.t0) / 1000 >= FB_MAX) return fbDone();
    if (now - FB.drawn >= 100) {
      FB.drawn = now;
      fbFind();
      fbDraw();
    }
  }
  function fbFind() {
    FB.jumps = FB.n ? PITCH.jumps({ s: FB.s, n: FB.n, hop: FB_HOP, firstT: 0 }) : [];
  }
  function fbChart() {
    const v = voice(),
      ms = FB.pts.map((q) => q.m),
      lo = Math.floor(Math.min(v.lo - 2, ...ms)),
      hi = Math.ceil(Math.max(v.fal + 2, ...ms));
    return PITCH.svg([{ a: FB.pts, col: 'var(--accent)' }], {
      w: 340,
      h: 170,
      lo,
      hi,
      dur: Math.max(6, Math.ceil(FB.t + 0.5)),
      dots: FB.jumps.map((j) => ({ t: j.t, m: j.to })),
      label: 'Your slide' + (FB.jumps.length ? ', with ' + FB.jumps.length + (FB.jumps.length === 1 ? ' jump' : ' jumps') : ''),
    });
  }
  // in place, about ten times a second; the box is looked up again only once it's gone
  function fbDraw() {
    if (!FB.el || !FB.el.isConnected) FB.el = document.getElementById('bfLive');
    if (FB.el) FB.el.innerHTML = fbChart();
  }
  function fbDone() {
    if (FB.phase !== 'listening') return;
    fbStop();
    fbFind();
    const ms = FB.pts.map((q) => q.m).sort((a, b) => a - b);
    FB.top = ms.length ? Math.round(ms[Math.min(ms.length - 1, Math.floor(ms.length * 0.98))]) : null;
    FB.jump = FB.jumps[0] || null;
    if (FB.jump) {
      const low = Math.round(Math.min(FB.jump.from, FB.jump.to));
      FB.lo = low - 2;
      FB.hi = low + 1;
    }
    FB.phase = 'done';
    rerender();
  }
  const fbStepper = (k, l) =>
    '<div class="row pvrow"><span class="lbl">' +
    l +
    '</span><span class="pvstep"><button data-a="bfStep" data-v="' +
    k +
    '" data-k="-1" aria-label="' +
    l +
    ' lower">−</button><b id="bf_' +
    k +
    '">' +
    nameOf(FB[k]) +
    '</b><button data-a="bfStep" data-v="' +
    k +
    '" data-k="1" aria-label="' +
    l +
    ' higher">+</button></span></div>';
  function fbResult() {
    const j = FB.jump,
      heardAny = FB.pts.length > 0;
    let t = '';
    if (FB.phase === 'blocked') t = MIC_FAIL[FB.why] || MIC_FAIL.none;
    else if (FB.feel) t = 'Set it by feel: where does your voice start to feel thin or tight?';
    else if (!heardAny) t = 'Nothing was heard. Check the microphone and try again, or set it by feel.';
    else if (j)
      t =
        'Your voice jumped at ' +
        nameOf(Math.round(j.from)) +
        (j.to > j.from ? ', up to ' : ', down to ') +
        nameOf(Math.round(j.to)) +
        '. Your bridge is suggested around it.';
    else t = 'No jump this time: your voice stayed smooth. Set it by feel: where does it start to feel thin or tight?';
    return (
      '<p class="note bfres">' +
      t +
      '</p>' +
      (FB.top != null ? '<p class="note bftop">Highest note: ' + nameOf(FB.top) + '</p>' : '') +
      '<div class="grp setgap bfgrp">' +
      fbStepper('lo', 'From') +
      fbStepper('hi', 'To') +
      '</div>' +
      '<button class="cta" data-a="bfUse">Use this bridge</button>' +
      '<button class="ghost" data-a="bfStart">Try again</button>'
    );
  }
  function bridgeSheet() {
    let b = '';
    if (FB.phase === 'ready')
      b =
        '<p class="note">Slide slowly up on “ee”, from a low note to as high as is easy, like a siren. Take about five seconds. Where your voice jumps is your bridge.</p>' +
        '<p class="note bfhint">Nothing plays while it listens, and nothing is recorded.</p>' +
        '<button class="cta" data-a="bfStart">Start</button>' +
        '<button class="ghost" data-a="bfFeel">Set it by feel</button>';
    else if (FB.phase === 'listening')
      b =
        '<div class="bflive" id="bfLive">' +
        fbChart() +
        '</div><p class="note bfres">Listening… slide up on “ee”.</p><button class="cta" data-a="bfStop">Done</button>';
    else b = (FB.phase === 'done' && !FB.feel && FB.pts.length ? '<div class="bflive">' + fbChart() + '</div>' : '') + fbResult();
    return sheetWrap('Find your bridge', b);
  }

  /* ===== The Patterns page's window: previewing one pattern ===== */
  let pvNotes = [],
    pvT = 0,
    pvEnd = null;
  // k: the key note to play it in (Q39's Play on a suggested pattern), else the round shown; onEnd once it stops
  function preview(p, k, onEnd) {
    if (!audio()) return;
    if (S.playing) end(false);
    NOW.start('pattern', 'preview', () => stopPreview(true));
    newBus();
    pvEnd = onEnd || null;
    const res = round(k != null ? k : keyNow(), AC.currentTime + 0.06, p, beatOf(spdOf(p)));
    pvNotes = res.ns;
    S.preview = p.n;
    paintPage();
    tick();
    clearTimeout(pvT);
    pvT = setTimeout(
      () => {
        if (S.preview === p.n) {
          S.preview = null;
          NOW.ended('pattern');
          paintPage();
          previewEnded();
        }
      },
      (res.end - AC.currentTime) * 1000 + 250
    );
  }
  const spdOf = (p) => {
    const v = (D.prefs && D.prefs.pat && D.prefs.pat.spd ? D.prefs.pat.spd : {})[p.n];
    return v == null ? ONE : v;
  };
  function stopPreview(quiet) {
    if (S.preview == null) return;
    if (AC && bus) bus.gain.setTargetAtTime(0, AC.currentTime, 0.06);
    S.preview = null;
    clearTimeout(pvT);
    if (!quiet) NOW.ended('pattern');
    paintPage();
    previewEnded();
  }
  function previewEnded() {
    const f = pvEnd;
    pvEnd = null;
    if (f) f();
  }
  // Q39: a pattern played once in a given key (n: its number, k: the key note), through NOW like any preview
  function hear(n, k, onEnd) {
    const p = byN(n);
    if (!p || !isFinite(k)) return false;
    if (S.preview != null) stopPreview(true);
    preview(p, Math.round(k), onEnd);
    return S.preview === p.n;
  }
  /* Q39: the player opened from outside an exercise (Practise in <key>, from a song): o {id, name, n: the pattern, k:
     its starting note (MIDI), key: the key's name}. One round, Stay on this key on. Its pattern and starting note are
     kept in memory (cfg.gx), never in an exercise's saved choices */
  function guest(o) {
    if (!o || !byN(o.n) || !isFinite(o.k)) return false;
    use({
      key: 'song:' + o.id,
      guest: true,
      gx: {},
      name: o.name + ' · ' + o.key,
      col: 'var(--accent)',
      route: [Math.round(o.k)],
      def: +o.n,
      syl: '',
      vowels: false,
      fal: false,
    });
    S.round = 0;
    S.hold = true;
    S.group = null;
    return true;
  }

  /* ===== The drawing ===== */
  const W = 300,
    H = 118;
  // each note's place: held notes take more room, quick touches less; a breath (null) breaks the line
  function geom(p) {
    const vals = p.semi.filter((v) => v !== null),
      l = Math.min(...vals),
      h = Math.max(...vals),
      n = p.semi.length,
      at = [0];
    for (let i = 1; i < n; i++) at.push(at[i - 1] + lenOf(p, i - 1));
    const span = at[n - 1] || 1;
    return p.semi.map((s, i) =>
      s === null
        ? null
        : { x: 14 + (n === 1 ? 0 : (at[i] * (W - 28)) / span), y: h === l ? H / 2 : 96 - ((s - l) * 80) / (h - l), i }
    );
  }
  // pre: id prefix; k: the key shown (out-of-range notes labelled in orange), or null for none; col: the colour
  function svg(p, pre, k, col, label) {
    const pts = geom(p),
      segs = [];
    let cur = [];
    pts.forEach((q) => {
      if (q) cur.push(q.x.toFixed(1) + ',' + q.y.toFixed(1));
      else if (cur.length) {
        segs.push(cur);
        cur = [];
      }
    });
    if (cur.length) segs.push(cur);
    const mus = opt('notes') === 'notes';
    let h =
      '<svg class="pdraw" id="' +
      pre +
      'Draw" viewBox="0 0 ' +
      W +
      ' ' +
      H +
      '" role="img" aria-label="' +
      esc(label) +
      '">' +
      '<line x1="0" y1="100" x2="' +
      W +
      '" y2="100" class="pbase"/>' +
      (pre === 'pc' && k != null ? bandSVG(p, k) : '');
    segs.forEach((s) => (h += '<polyline points="' + s.join(' ') + '" class="pline"/>'));
    pts.forEach((q) => {
      if (!q) return;
      const n = k == null ? null : k + p.semi[q.i],
        bad = n != null && outOf(n),
        c = bad ? 'var(--warn)' : col,
        qk = quick(p, q.i);
      h += mus
        ? '<g class="pdot pnt" data-i="' +
          q.i +
          '" opacity=".35" style="transform-origin:' +
          q.x +
          'px ' +
          q.y +
          'px"><ellipse cx="' +
          q.x +
          '" cy="' +
          q.y +
          '" rx="' +
          (qk ? 4.4 : 6.6) +
          '" ry="' +
          (qk ? 3.2 : 4.8) +
          '" transform="rotate(-22 ' +
          q.x +
          ' ' +
          q.y +
          ')" fill="' +
          c +
          '"/><line x1="' +
          (q.x + (qk ? 4 : 6)) +
          '" y1="' +
          (q.y - 1.5) +
          '" x2="' +
          (q.x + (qk ? 4 : 6)) +
          '" y2="' +
          (q.y - (qk ? 18 : 26)) +
          '" stroke="' +
          c +
          '" stroke-width="1.8" stroke-linecap="round"/></g>'
        : '<circle class="pdot" data-i="' +
          q.i +
          '" cx="' +
          q.x.toFixed(1) +
          '" cy="' +
          q.y.toFixed(1) +
          '" r="' +
          (qk ? 3.6 : 6) +
          '" fill="' +
          c +
          '" opacity=".35"/>';
      if (bad)
        h +=
          '<text x="' +
          q.x.toFixed(1) +
          '" y="' +
          (q.y - 11).toFixed(1) +
          '" text-anchor="middle" class="pout">' +
          nameOf(n) +
          '</text>';
      // Q38 a note in your bridge is ringed
      if (pre === 'pc' && n != null && inZone(n))
        h +=
          '<circle class="pring" data-i="' +
          q.i +
          '" cx="' +
          q.x.toFixed(1) +
          '" cy="' +
          q.y.toFixed(1) +
          '" r="' +
          (qk ? 6.5 : 10.5) +
          '"/>';
    });
    // Q38 your voice while listening: a 1 s trail and a dot, painted by tick()
    if (pre === 'pc') h += '<polyline class="ptrail" points=""/><circle class="pvoice" r="5" cx="0" cy="0" style="display:none"/>';
    return (
      h +
      '<g class="prips"></g><g class="phead" style="display:none"><line x1="0" y1="2" x2="0" y2="' +
      (H - 6) +
      '"/><circle cx="0" cy="3" r="4"/></g></svg>'
    );
  }
  // Q38 the bridge band behind the drawing, for the round on key k: only where it meets the round's notes
  function bandSVG(p, k) {
    const b = bridge();
    if (!b) return '';
    const l = lo(p),
      h = hi(p),
      flat = h === l,
      u = flat ? 8 : 80 / (h - l),
      y = (s) => (flat ? H / 2 : 96) - (s - l) * u,
      zl = b.lo - k,
      zh = b.hi - k;
    if (zh < l || zl > h) return '';
    const t = Math.max(4, y(zh + 0.5)),
      bt = Math.min(104, y(zl - 0.5)),
      // the label goes to whichever end has no ringed note near it
      // (or just above the band when both ends have one)
      g = geom(p),
      ringAt = (f) => g.some((q) => q && inZone(k + p.semi[q.i]) && f(q.x)),
      near = ringAt((x) => x > W - 96),
      left = near && !ringAt((x) => x < 96),
      above = near && !left && t >= 16,
      ty = above ? t - 4 : t + 11;
    return (
      '<g class="pband"><rect x="0" y="' +
      t.toFixed(1) +
      '" width="' +
      W +
      '" height="' +
      (bt - t).toFixed(1) +
      '" rx="4"/><text x="' +
      (left ? 4 : W - 4) +
      '" y="' +
      ty.toFixed(1) +
      '" text-anchor="' +
      (left ? 'start' : 'end') +
      '">Bridge ' +
      zoneName(b) +
      '</text></g>'
    );
  }
  // the playhead moving through the notes, the current dot growing and lit, earlier dots staying lit, a ripple on each
  let raf = 0,
    lastLit = -2;
  function tick() {
    cancelAnimationFrame(raf);
    let el = null,
      p = null,
      els = null;
    const step = () => {
      const main = S.playing,
        live = main || S.preview != null;
      if (!live || !AC) return;
      const want = main ? 'pcDraw' : 'pwDraw',
        pp = main ? pat() : byN(S.preview);
      if (!el || !el.isConnected || el.id !== want || p !== pp) {
        el = document.getElementById(want);
        p = pp;
        lastLit = -2;
        els = el
          ? {
              head: el.querySelector('.phead'),
              rips: el.querySelector('.prips'),
              dots: [...el.querySelectorAll('.pdot')],
              voice: el.querySelector('.pvoice'),
              trail: el.querySelector('.ptrail'),
              cue: main ? document.getElementById('pcCue') : null,
              vOn: false,
            }
          : null;
      }
      if (el && els) {
        const ns = (main ? sched : pvNotes).filter(Boolean),
          t = AC.currentTime,
          pts = geom(p);
        let x = null,
          cur = -1;
        if (ns.length && t >= ns[0].t) {
          for (let j = 0; j < ns.length; j++) {
            const a = ns[j];
            if (t >= a.t && t < a.t + a.d) {
              cur = a.i;
              const b = ns[j + 1],
                pa = pts[a.i],
                pb = b ? pts[b.i] : null;
              x = pb ? pa.x + (pb.x - pa.x) * Math.min(1, (t - a.t) / a.d) : pa.x;
              break;
            }
          }
          if (cur < 0 && t >= ns[ns.length - 1].t) x = pts[ns[ns.length - 1].i].x;
        }
        els.head.style.display = x == null ? 'none' : '';
        if (x != null) els.head.setAttribute('transform', 'translate(' + x.toFixed(1) + ',0)');
        if (main && x != null) S.headX = x;
        if (main && els.voice) paintVoice(els);
        if (cur !== lastLit) {
          lastLit = cur;
          // Q38 the cue, while a note in your bridge plays
          if (main && els.cue) {
            const a = cur >= 0 ? ns.find((n) => n.i === cur) : null,
              on = !!(a && a.br && opt('bcue'));
            if (on) els.cue.innerHTML = cueHTML();
            els.cue.hidden = !on;
            S.cue = on;
          }
          els.dots.forEach((d) => {
            const i = +d.dataset.i,
              on = i === cur,
              q = quick(p, i);
            d.setAttribute('opacity', on ? '1' : i < cur ? '.75' : '.35');
            if (d.tagName === 'circle') d.setAttribute('r', on ? (q ? '5' : '8') : q ? '3.6' : '6');
            else d.style.transform = on ? 'scale(1.3)' : '';
          });
          if (cur >= 0 && MOTION.on() && cfg) {
            const q = pts[cur],
              c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            c.setAttribute('cx', q.x);
            c.setAttribute('cy', q.y);
            c.setAttribute('r', '8');
            c.setAttribute('class', 'prip');
            c.setAttribute('stroke', cfg.col);
            els.rips.appendChild(c);
            setTimeout(() => c.remove(), 700);
          }
        }
      }
      raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
  }

  // Q38 your voice on the drawing: the last second as a trail, and a dot while it's still sounding
  function paintVoice(els) {
    const l = LS;
    if (!l) {
      if (els.vOn) {
        els.voice.style.display = 'none';
        els.trail.setAttribute('points', '');
        els.vOn = false;
      }
      return;
    }
    const now = performance.now();
    let pts = '';
    for (let i = 0; i < l.trail.length; i++) {
      const q = l.trail[i];
      if (now - q.at <= 1000) pts += (pts ? ' ' : '') + q.x.toFixed(1) + ',' + q.y.toFixed(1);
    }
    els.trail.setAttribute('points', pts);
    const fresh = !!l.last && now - l.last.at < 200 && l.trail.length;
    els.voice.style.display = fresh ? '' : 'none';
    if (fresh) {
      const q = l.trail[l.trail.length - 1];
      els.voice.setAttribute('cx', q.x.toFixed(1));
      els.voice.setAttribute('cy', q.y.toFixed(1));
    }
    els.vOn = true;
  }
  // Q38 the cue's words: a hum (hmmm, ng, a trill, oo) gets "Thinner · quieter"; an open vowel its narrower one
  const NARROW = [
    [/ay|ey|eh/, 'eh', 'ih'],
    [/oh|oe|ow/, 'oh', 'uh'],
    [/ah|a$/, 'ah', 'uh'],
    [/ee|e$/, 'ee', 'ih'],
  ];
  const cueOf = (w) => {
    const x = NARROW.find(([re]) => re.test(String(w || '').toLowerCase()));
    return x ? { from: x[1], to: x[2] } : null;
  };
  function cueWord() {
    const v = vowelList();
    if (v.length) return v[S.round % v.length];
    const w = String((cfg && cfg.syl) || '')
      .split(/\s+/)
      .filter(Boolean);
    return w.length === 1 ? w[0] : '';
  }
  function cueHTML() {
    const c = cueOf(cueWord());
    return c ? '<s>' + c.from + '</s> ' + c.to + ' · quieter' : 'Thinner · quieter';
  }

  /* ===== What the card says ===== */
  const VOWEL_ALL = ['ee', 'eh', 'ah', 'oh', 'oo'];
  const SCALE = new Set([1, 5, 6, 7, 9, 12, 13]); // stepwise scale patterns
  // the vowel cue shows only where it means something: open-vowel exercises, on a scale pattern
  const vowelOn = () => !!(cfg && cfg.vowels) && opt('vowel') !== 'off' && SCALE.has(pat().n);
  const vowelList = () =>
    !vowelOn()
      ? []
      : opt('vowel') === 'all'
        ? VOWEL_ALL
        : String(cfg.syl || '')
            .split(/\s+/)
            .filter(Boolean);
  let lastVowel = '';
  function vowelHTML(anim) {
    const v = vowelList();
    if (!v.length) return '';
    const i = S.round % v.length,
      cur = v[i],
      nx = v[(i + 1) % v.length],
      key = S.round + ':' + cur,
      swap = anim && S.playing && key !== lastVowel;
    lastVowel = key;
    return (
      '<span class="pvl">Sing on</span><b' +
      (swap ? ' class="swap"' : '') +
      '><i>' +
      esc(cur) +
      '</i></b>' +
      (v.length > 1 ? '<span class="pvn">next <i>' + esc(nx) + '</i></span>' : '<span class="pvn">every round</span>')
    );
  }
  function statusHTML() {
    const r = route(),
      p = pat();
    if (!r.length) return '';
    const k = keyNow(),
      prev = S.round > 0 ? r[S.round - 1] : null,
      dir = prev == null ? '' : k > prev ? ' ↑' : k < prev ? ' ↓' : '';
    if (!S.playing && S.homeUntil > Date.now())
      return '<b>Home · ' + nameOf(r[0]) + '</b><span>Back where you started</span>';
    if (S.playing) {
      const bad = roundOut(k);
      return (
        '<b' +
        (bad ? ' class="pbad"' : '') +
        '>' +
        (bad ? '⚠ ' : '') +
        nameOf(k) +
        dir +
        ' · Round ' +
        (S.round + 1) +
        ' of ' +
        r.length +
        (S.hold ? ' · on repeat' : '') +
        '</b><span>' +
        p.name +
        '</span>'
      );
    }
    return (
      '<b>Starts on ' +
      nameOf(r[0]) +
      '</b><span>' +
      r.length +
      (r.length === 1 ? ' round' : ' rounds') +
      ' · ' +
      p.name +
      '</span>'
    );
  }
  const WARN =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17v.5"/></svg>';
  function rangeHTML() {
    const rc = rangeCheck();
    if (!rc) return { bad: false, h: '' };
    const r = route();
    let stopTxt = '';
    if (opt('stopTop') && rc.out.some((w) => w.kind === 'high')) {
      rc.out = rc.out.filter((w) => w.kind !== 'high');
      stopTxt =
        'Stops after round ' +
        r.length +
        ' of ' +
        full().length +
        ', before going above ' +
        yourT() +
        ' top (' +
        nameOf(top()) +
        ')';
    }
    if (rc.out.length)
      return {
        bad: true,
        h:
          WARN +
          '<span>' +
          rc.out.map((w) => warnText(w)).join('<br>') +
          (stopTxt ? '<br>' + stopTxt : '') +
          '. Tap to change your range.</span>',
      };
    const vt = voice().type === 'Custom' ? 'your range' : 'your ' + voice().type.toLowerCase() + ' range';
    return {
      bad: false,
      h:
        '<span>' +
        (stopTxt ||
          nameOf(rc.lo) + ' to ' + nameOf(rc.hi) + ' · within ' + vt + (useFal() ? ' (using falsetto)' : '')) +
        '</span>',
    };
  }
  // Q38 the bridge line: where your bridge is and which rounds cross it, a door to Find your bridge
  function bridgeHTML() {
    const b = bridge();
    if (!b) return '<span><b>Find your bridge</b></span><span class="pbgo">Find it</span>';
    const p = pat(),
      xs = [];
    route().forEach((k, i) => {
      if (p.semi.some((v) => v !== null && inZone(k + v))) xs.push(i + 1);
    });
    const where = !xs.length
      ? 'no round crosses it.'
      : xs.length === 1
        ? 'round ' + xs[0] + ' crosses it. Those notes play softer.'
        : 'rounds ' + xs[0] + '–' + xs[xs.length - 1] + ' cross it. Those notes play softer.';
    return '<span>Bridge ' + zoneName(b) + ' · ' + where + '</span><span class="pbgo">Change</span>';
  }
  // Q38 Last time on this exercise: a fact, never a score
  function lastHTML() {
    const lt = lastNow();
    if (lt)
      return (
        'Last time: ' +
        nameOf(lt.m) +
        ' · ' +
        relDay(new Date(lt.at)) +
        (opt('stopLast') ? ' · stops one round past it' : '')
      );
    return opt('stopLast') ? 'Last time: not yet. Listen while you sing to set it.' : '';
  }
  function listenHTML() {
    const on = !!opt('listen');
    return (
      '<span class="lbl">Listen while I sing' +
      (on ? '<small>Headphones in, so it only hears you</small>' : '') +
      '</span>' +
      switchHTML(on) +
      ''
    );
  }
  // update the card and dock in place (no redraw of the page while playing)
  function paint() {
    const st = document.getElementById('pcStat');
    if (st) st.innerHTML = statusHTML();
    const vw = document.getElementById('pcVowel');
    if (vw) {
      const h = vowelHTML(true);
      vw.innerHTML = h;
      vw.hidden = !h;
    }
    const rg = document.getElementById('pcRange');
    if (rg) {
      const r = rangeHTML();
      rg.innerHTML = r.h;
      rg.classList.toggle('bad', r.bad);
    }
    const br = document.getElementById('pcBridge');
    if (br) br.innerHTML = bridgeHTML();
    const ls = document.getElementById('pcLast');
    if (ls) {
      const h = lastHTML();
      ls.textContent = h;
      ls.hidden = !h;
    }
    const li = document.getElementById('pcListen');
    if (li) {
      li.innerHTML = listenHTML();
      li.setAttribute('aria-checked', !!opt('listen'));
    }
  }
  function paintAll() {
    paint();
    paintDock();
  }
  function redraw() {
    const d = document.getElementById('pcDraw');
    if (d && cfg)
      d.outerHTML = svg(pat(), 'pc', keyNow(), cfg.col, 'Pitch shape of ' + pat().name.replace(/&amp;/g, '&'));
  }

  /* ===== Markup: the card (on the page) and the dock ===== */
  function card() {
    if (!cfg || !route().length) return '';
    const r = rangeHTML(),
      v = vowelHTML(false);
    return (
      '<div class="pcard" id="pcCard" style="--pc:' +
      cfg.col +
      '">' +
      '<div class="pvowel" id="pcVowel"' +
      (v ? '' : ' hidden') +
      '>' +
      v +
      '</div>' +
      '<div class="pdw">' +
      svg(pat(), 'pc', keyNow(), cfg.col, 'Pitch shape of ' + pat().name.replace(/&amp;/g, '&')) +
      '<div class="pcue" id="pcCue" role="status" hidden></div></div>' +
      '<div class="pstat" id="pcStat" aria-live="polite">' +
      statusHTML() +
      '</div>' +
      '<button class="prange' +
      (r.bad ? ' bad' : '') +
      '" id="pcRange" data-a="patVoice" data-zk="set:voice" data-push aria-label="Your voice range. Open Your voice">' +
      r.h +
      '</button>' +
      '<button class="pbridge" id="pcBridge" data-a="patBridge" aria-label="' +
      (bridge() ? 'Your bridge, ' + zoneName(bridge()) + '. Change it' : 'Find your bridge') +
      '">' +
      bridgeHTML() +
      '</button>' +
      '<p class="plast" id="pcLast"' +
      (lastHTML() ? '' : ' hidden') +
      '>' +
      esc(lastHTML()) +
      '</p>' +
      '<button class="plisten" id="pcListen" data-a="patListen" role="switch" aria-checked="' +
      !!opt('listen') +
      '">' +
      listenHTML() +
      '</button>' +
      '</div>'
    );
  }
  const IC = {
    up: '<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 15l6-6 6 6"/></svg>',
    spk: '<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 10v4h4l5 4V6L8 10z"/><path d="M16 9.5c1.2 1.4 1.2 3.6 0 5"/></svg>',
    rep1: '<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="M17 2l3 3-3 3"/><path d="M4 11V9a4 4 0 0 1 4-4h12"/><path d="M7 22l-3-3 3-3"/><path d="M20 13v2a4 4 0 0 1-4 4H4"/><path d="M11.5 10.5l1.2-.8V14"/></svg>',
    ramp: '<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 18l6-6 4 4 6-8"/><path d="M15 8h5v5"/></svg>',
    play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l12-7.5z"/></svg>',
    stop: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="6" width="12" height="12" rx="2.5"/></svg>',
    star: (on) =>
      '<svg class="pstar' +
      (on ? ' on' : '') +
      '" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.5l2.6 5.3 5.9.9-4.25 4.1 1 5.85L12 16.9l-5.25 2.75 1-5.85L3.5 9.7l5.9-.9z"/></svg>',
    chk: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
    reset:
      '<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12a8 8 0 1 0 2.5-5.8"/><path d="M4 4v4h4"/></svg>',
    tort: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 16a7.5 6 0 0 1 15 0z"/><path d="M18.5 14.5c1.5 0 2.5-.8 2.5-2"/><path d="M6.5 16v2.5M15.5 16v2.5"/><path d="M8 11.5l3 4.5 3-4.5"/></svg>',
    hare: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19c0-4.5 3-7.5 7.5-7.5H15a4 4 0 0 1 4 4v.5h-3.5"/><path d="M14 11.5 12.5 3.5c2.2 1 3.4 3.4 3.3 6.6M16.8 12l1.4-6.5"/><path d="M4 19h7"/></svg>',
  };
  function spdPillHTML() {
    return spLabel(spdIx()) + (opt('ramp') ? IC.ramp : '');
  }
  function dock() {
    if (!cfg || !route().length) return '';
    const p = pat(),
      r = route();
    return (
      '<div class="pdock" role="group" aria-label="Pattern player">' +
      '<div class="ppills">' +
      '<button class="ppill ppat glass" data-a="patOpen" data-zk="pat" aria-label="Pattern: ' +
      p.name +
      '. Open Patterns"><span>' +
      p.name +
      '</span>' +
      IC.up +
      '</button>' +
      '<button class="ppill pspd glass' +
      (opt('ramp') ? ' ramping' : '') +
      '" id="pSpd" data-a="patSpd" data-own-gesture aria-label="Speed ' +
      spLabel(spdIx()) +
      '. Opens the speed slider">' +
      spdPillHTML() +
      '</button>' +
      '<button class="ppill psnd glass" id="pSnd" data-a="patSound" aria-haspopup="menu" aria-label="Sound: ' +
      soundOf(opt('sound')).name +
      '">' +
      IC.spk +
      '<span>' +
      soundOf(opt('sound')).name +
      '</span></button>' +
      '</div><div class="ptrans">' +
      '<div class="pstep glass"><button data-a="patShift" data-v="-1" aria-label="Start lower">−</button><span class="psv"><b id="pStart">' +
      nameOf(r[0]) +
      '</b><small>Starts on</small></span><button data-a="patShift" data-v="1" aria-label="Start higher">+</button></div>' +
      '<button class="prep glass' +
      (S.hold ? ' on' : '') +
      '" id="pRep" data-a="patHold" aria-pressed="' +
      S.hold +
      '" aria-label="Stay on this key">' +
      IC.rep1 +
      '</button>' +
      '<button class="pplay" id="pPlay" data-a="patPlay" aria-label="' +
      (S.playing ? 'Stop' : 'Play') +
      '">' +
      (S.playing ? IC.stop : IC.play) +
      '</button>' +
      '</div></div>'
    );
  }
  function paintDock() {
    const pl = document.getElementById('pPlay');
    if (pl) {
      pl.innerHTML = S.playing ? IC.stop : IC.play;
      pl.setAttribute('aria-label', S.playing ? 'Stop' : 'Play');
    }
    const rp = document.getElementById('pRep');
    if (rp) {
      rp.classList.toggle('on', S.hold);
      rp.setAttribute('aria-pressed', S.hold);
    }
    const sp = document.getElementById('pSpd');
    if (sp) {
      sp.innerHTML = spdPillHTML();
      sp.classList.toggle('ramping', !!opt('ramp'));
      sp.setAttribute('aria-label', 'Speed ' + spLabel(spdIx()) + '. Opens the speed slider');
    }
    const s0 = document.getElementById('pStart'),
      r = route();
    if (s0 && r.length) s0.textContent = nameOf(r[0]);
  }

  /* ===== The Patterns page (U.view 'pat') ===== */
  function tilesOf(list) {
    const cur = pat().n,
      def = cfg ? cfg.def : 0,
      fv = favs();
    return (
      '<div class="ptiles">' +
      list
        .map((p) => {
          const f = fv.includes(p.n),
            nm = p.name.replace(/&amp;/g, '&');
          return (
            '<div class="ptw"><button class="pt' +
            (p.n === cur ? ' on' : '') +
            (S.preview === p.n ? ' live' : '') +
            '" data-a="patPick" data-v="' +
            p.n +
            '" data-hold aria-label="' +
            p.n +
            ', ' +
            esc(nm) +
            (p.n === cur ? ', chosen' : '') +
            (p.n === def ? ', default' : '') +
            '" aria-description="' +
            esc(p.line.replace(/&amp;/g, '&')) +
            '">' +
            '<span class="ptop"><span class="pnum">' +
            p.n +
            '</span>' +
            (p.n === cur ? '<span class="pchk">' + IC.chk + '</span>' : '') +
            '</span>' +
            '<span class="pnm">' +
            p.name +
            '</span><span class="pst"><span class="psteps">' +
            p.steps +
            '</span><span class="pline" aria-hidden="true">' +
            p.line +
            '</span></span>' +
            (p.n === def ? '<span class="pdft">Default</span>' : '') +
            '<span class="pmini" aria-hidden="true">' +
            IC.play +
            '</span></button>' +
            '<button class="pfav' +
            (f ? ' on' : '') +
            '" data-a="patFav" data-v="' +
            p.n +
            '" aria-pressed="' +
            f +
            '" aria-label="' +
            (f ? 'Remove ' + esc(nm) + ' from Favourites' : 'Add ' + esc(nm) + ' to Favourites') +
            '">' +
            IC.star(f) +
            '</button></div>'
          );
        })
        .join('') +
      '</div>'
    );
  }
  function tilesHTML() {
    const g = S.group || pat().g;
    let h;
    if (g === 'f') {
      const fv = favs().map(byN).filter(Boolean);
      h = fv.length
        ? tilesOf(fv) + '<p class="note pgnote">' + GROUP_NOTE.f + '</p>'
        : '<div class="pempty">' +
          IC.star(false) +
          '<b>No favourites yet</b><span>Tap the star on any pattern to keep it here.</span></div>';
    } else if (g === 'r')
      h =
        SUBS.map(([k, l]) => '<div class="hdr psub">' + l + '</div>' + tilesOf(LIB.filter((p) => p.sub === k))).join(
          ''
        ) +
        '<p class="note pgnote">' +
        GROUP_NOTE.r +
        '</p>';
    else
      h =
        tilesOf(LIB.filter((p) => p.g === g)) +
        (GROUP_NOTE[g] ? '<p class="note pgnote">' + GROUP_NOTE[g] + '</p>' : '');
    return (
      h +
      '<button class="preset" data-a="patPick" data-v="' +
      (cfg ? cfg.def : 1) +
      '">' +
      IC.reset +
      'Back to default</button>'
    );
  }
  function winHTML() {
    const p = byN(S.preview) || pat(),
      live = S.preview === p.n;
    return (
      '<div class="pwin" id="pWin"><div class="pwh"><span class="pnum">' +
      p.n +
      '</span><b>' +
      p.name +
      '</b><span class="pst">' +
      p.steps +
      '</span>' +
      '<button class="pwplay' +
      (live ? ' live' : '') +
      '" data-a="patWin" data-v="' +
      p.n +
      '" aria-label="' +
      (live ? 'Stop' : 'Play ' + esc(p.name.replace(/&amp;/g, '&'))) +
      '">' +
      (live ? IC.stop : IC.play) +
      '</button></div>' +
      svg(p, 'pw', null, cfg ? cfg.col : 'var(--accent)', 'Pitch shape of ' + p.name.replace(/&amp;/g, '&')) +
      '</div>'
    );
  }
  function page() {
    if (!cfg) return '<h1>Patterns</h1>';
    const g = S.group || pat().g;
    return (
      '<div class="phd"><h1>Patterns</h1><span class="pfor">' +
      esc(cfg.name) +
      '</span></div>' +
      '<div class="pfix"><div class="seg pk-seg wide pgrp" role="tablist" aria-label="Pattern groups"><span class="pk-seg-ind" aria-hidden="true"></span>' +
      GROUPS.map(
        ([k, l]) =>
          '<button role="tab" data-a="patGroup" data-v="' +
          k +
          '" class="' +
          (k === 'f' ? 'pfseg ' : '') +
          (g === k ? 'on' : '') +
          '" aria-selected="' +
          (g === k) +
          '"' +
          (k === 'f' ? ' aria-label="Favourites">' + IC.star(g === 'f') : '>' + l) +
          '</button>'
      ).join('') +
      '</div>' +
      winHTML() +
      '</div>' +
      '<div id="pTiles">' +
      tilesHTML() +
      '</div>'
    );
  }
  function paintPage() {
    if (U.view !== 'pat') return;
    const w = document.getElementById('pWin');
    if (w) w.outerHTML = winHTML();
    const t = document.getElementById('pTiles');
    if (t) {
      const y = window.scrollY;
      t.innerHTML = tilesHTML();
      window.scrollTo(0, y);
    }
  }

  /* ===== The speed slider (like Control Centre's) ===== */
  let hud = null,
    hudT = 0,
    hudOn = false,
    y0 = 0,
    i0 = 0,
    pvTimers = [];
  // Q41 (D03) the speed is the parts kit's slider (its knob grows ×1.35 while held), under the −, speed and + bubble;
  // the vertical bar it replaced is kept in git at the tag vs-3.54-speedbar
  function hudEl() {
    if (hud) return hud;
    hud = document.createElement('div');
    hud.id = 'pHud';
    hud.setAttribute('data-own-gesture', '');
    hud.innerHTML =
      '<div class="phscrim" data-a="patHudClose"></div><div class="phwrap"><div class="phbub glass"><button data-a="patSpdStep" data-v="-1" aria-label="Slower">−</button><span id="pHudVal">1×</span><small>speed</small><button data-a="patSpdStep" data-v="1" aria-label="Faster">+</button>' +
      '<button class="phramp" id="pHudRamp" data-a="patRamp" aria-pressed="false" aria-label="Speed up each round">' +
      IC.ramp +
      '</button></div>' +
      '<div class="phcard glass"><span class="phtort" aria-hidden="true">' +
      IC.tort +
      '</span><div class="pk-slider" id="pHudBar" data-name="speed-slider" data-min="0" data-max="' +
      (SPEEDS.length - 1) +
      '" data-step="1" data-value="' +
      spdIx() +
      '" aria-label="Speed" tabindex="0"><div class="pk-slider-track"><div class="pk-slider-fill"></div></div><div class="pk-slider-thumb"></div></div><span class="phhare" id="pHudTop" aria-hidden="true">' +
      IC.hare +
      '</span><div class="phlabs" id="pHudLabs"></div></div></div>';
    document.body.appendChild(hud);
    const bar = hud.querySelector('#pHudBar');
    bar.addEventListener('pk:input', (e) => {
      setSpeed(Math.round(e.detail.value), true);
      clearTimeout(hudT);
    });
    bar.addEventListener('pk:change', () => later());
    return hud;
  }
  const pc = (i) => (i / (SPEEDS.length - 1)) * 100;
  function hudDraw() {
    if (!hudOn) return;
    const i = spdIx();
    hud.querySelector('#pHudVal').textContent = spLabel(i);
    const bar = hud.querySelector('#pHudBar');
    if (+bar.dataset.value !== i) Parts.setSlider(bar, i);
    bar.setAttribute('aria-valuemin', 0);
    bar.setAttribute('aria-valuemax', SPEEDS.length - 1);
    bar.setAttribute('aria-valuenow', i);
    bar.setAttribute('aria-valuetext', spLabel(i));
    hud.querySelector('#pHudLabs').innerHTML = [
      [0, '0.5×'],
      [ONE, '1×'],
      [SPEEDS.length - 1, '2×'],
    ]
      .map(([k, l]) => '<span style="left:' + pc(k) + '%">' + l + '</span>')
      .join('');
    hud.querySelector('#pHudTop').classList.toggle('in', i === SPEEDS.length - 1);
    const rb = hud.querySelector('#pHudRamp');
    rb.classList.toggle('on', !!opt('ramp'));
    rb.setAttribute('aria-pressed', !!opt('ramp'));
  }
  function openHud() {
    const pl = document.getElementById('pSpd');
    if (!pl) return;
    hudEl();
    const r = pl.getBoundingClientRect(),
      w = hud.querySelector('.phwrap');
    w.style.left = r.left + r.width / 2 + 'px';
    w.style.bottom = innerHeight - r.top + 12 + 'px';
    hudOn = true;
    hud.classList.add('on');
    hudDraw();
    clearTimeout(hudT);
  }
  function closeHud() {
    if (!hudOn) return;
    hudOn = false;
    clearTimeout(hudT);
    hud.classList.remove('on');
    if (S.playing) toast('Speed ' + spLabel(spdIx()) + ' · from the next round');
  }
  const later = () => {
    clearTimeout(hudT);
    hudT = setTimeout(closeHud, 2600);
  };
  // holding the speed pill opens the slider and a drag carries straight on, sideways, from the current speed; it snaps
  // to the 12 stops
  function begin(x) {
    y0 = x;
    i0 = spdIx();
    clearTimeout(hudT);
  }
  function move(x) {
    if (!hudOn) return;
    const bar = hud.querySelector('#pHudBar'),
      n = SPEEDS.length - 1,
      step = bar.getBoundingClientRect().width / n,
      raw = i0 + (x - y0) / step;
    setSpeed(Math.round(Math.max(0, Math.min(n, raw))), true);
    bar.classList.add('pk-held');
    clearTimeout(hudT);
  }
  function let_go() {
    if (!hud) return;
    hud.querySelector('#pHudBar').classList.remove('pk-held');
    later();
  }
  function setSpeed(i, quiet) {
    i = Math.max(0, Math.min(SPEEDS.length - 1, i));
    if (i === spdIx()) return;
    S.rampOff = 0;
    const p = P();
    p.spd = Object.assign({}, p.spd || {});
    if (i === ONE) delete p.spd[pat().n];
    else p.spd[pat().n] = i;
    save();
    hudDraw();
    paintDock();
    tempo();
    if (!quiet) toast('Speed ' + spLabel(i) + (S.playing ? ' · from the next round' : ''));
  }
  // live feedback: the drawing's dots light up in turn at the new tempo, without sound
  function tempo() {
    pvTimers.forEach(clearTimeout);
    pvTimers = [];
    if (S.playing) return;
    const dots = [...document.querySelectorAll('#pcDraw .pdot')],
      b = beatOf(spdIx()) * 1000;
    dots.forEach((d, k) =>
      pvTimers.push(
        setTimeout(() => {
          dots.forEach((x) => x.classList.remove('ptempo'));
          d.classList.add('ptempo');
        }, k * b)
      )
    );
    pvTimers.push(setTimeout(() => dots.forEach((x) => x.classList.remove('ptempo')), dots.length * b));
  }
  // holding the speed pill opens the slider straight away, so you can drag on; a tap opens it too
  let holdT = 0,
    held = false,
    heldAt = 0;
  document.addEventListener('pointerdown', (e) => {
    const pl = e.target.closest && e.target.closest('#pSpd');
    if (!pl) return;
    held = false;
    clearTimeout(holdT);
    const x = e.clientX;
    try {
      pl.setPointerCapture(e.pointerId);
    } catch (er) {}
    holdT = setTimeout(() => {
      held = true;
      heldAt = Date.now();
      openHud();
      begin(x);
    }, 330);
  });
  document.addEventListener('pointermove', (e) => {
    if (held && hudOn && e.target.closest && e.target.closest('#pSpd')) move(e.clientX);
  });
  const up = (e) => {
    if (!e.target.closest || !e.target.closest('#pSpd')) return;
    clearTimeout(holdT);
    if (held) {
      held = false;
      let_go();
    }
  };
  document.addEventListener('pointerup', up);
  document.addEventListener('pointercancel', up);

  /* ===== A small menu (the sound pill, Your voice's type): Q41 the parts kit's, growing out of its button ===== */
  let menuFn = null,
    pm = null;
  // items: [key, label, checked] (checked true/false: a ✓ item; undefined: a choice, ✓ on cur), or ['-', heading]
  function menu(anchor, title, items, cur, fn) {
    closeMenu();
    menuFn = fn;
    const o = (pm = KMENU.open({
      id: 'pmenu',
      anchor,
      kind: 'pull',
      name: title || 'Menu',
      onClose: (picked) => {
        if (pm !== o) return;
        pm = null;
        if (!picked) menuFn = null;
      },
      html:
        (title ? '<div class="pmh">' + esc(title) + '</div>' : '') +
        items
          .map(([k, l, on]) => {
            if (k === '-') return '<div class="pmh pmsep">' + esc(l) + '</div>';
            const c = on === undefined ? k === cur : !!on;
            return (
              '<button role="' +
              (on === undefined ? 'menuitemradio' : 'menuitemcheckbox') +
              '" aria-checked="' +
              c +
              '" data-a="patMenuPick" data-v="' +
              esc(k) +
              '">' +
              esc(l) +
              (c ? ICON.check : '') +
              '</button>'
            );
          })
          .join(''),
    }));
  }
  function closeMenu() {
    if (pm) pm.shut();
    pm = null;
    menuFn = null;
  }
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (pm) closeMenu();
      else if (hudOn) closeHud();
    }
  });

  /* ===== Settings pages: Your voice and Pattern player ===== */
  const sw = (a, on, l, sub) =>
    '<button class="row" data-a="' +
    a +
    '" role="switch" aria-checked="' +
    on +
    '"><span class="lbl">' +
    l +
    (sub ? '<small>' + sub + '</small>' : '') +
    '</span>' +
    switchHTML(on) +
    '</button>';
  const segH = (a, opts, cur, label) =>
    '<div class="seg pk-seg wide pset" role="group" aria-label="' +
    label +
    '"><span class="pk-seg-ind" aria-hidden="true"></span>' +
    opts
      .map(
        ([k, l]) =>
          '<button data-a="' +
          a +
          '" data-v="' +
          k +
          '" class="' +
          (k === cur ? 'on' : '') +
          '" aria-pressed="' +
          (k === cur) +
          '">' +
          l +
          '</button>'
      )
      .join('') +
    '</div>';
  function voicePage() {
    const v = voice();
    return (
      '<h1>Your voice</h1>' +
      '<div class="grp setgap"><button class="row" data-a="patVoiceType" aria-haspopup="menu"><span class="lbl">Voice type</span><span class="mut">' +
      esc(v.type) +
      ' ▾</span></button></div>' +
      '<div class="grp setgap">' +
      [
        ['lo', 'Lowest comfortable note'],
        ['hi', 'Highest comfortable note'],
        ['fal', 'Falsetto top'],
      ]
        .map(
          ([k, l]) =>
            '<div class="row pvrow"><span class="lbl">' +
            l +
            '</span><span class="pvstep"><button data-a="patNudge" data-v="' +
            k +
            '" data-k="-1" aria-label="' +
            l +
            ' lower">−</button><b id="pv_' +
            k +
            '">' +
            nameOf(v[k]) +
            '</b><button data-a="patNudge" data-v="' +
            k +
            '" data-k="1" aria-label="' +
            l +
            ' higher">+</button></span></div>'
        )
        .join('') +
      '</div><p class="foot">Changing a note makes your voice type Custom. Falsetto voice, Squeaky hinge, Upper to lower voice and the Flips patterns are checked against your falsetto top; everything else against your highest comfortable note.</p>' +
      '<div class="grp setgap">' +
      sw('patStopTop', !!opt('stopTop'), 'Stop at my top note') +
      sw('patStopLast', !!opt('stopLast'), 'Stop one past last time') +
      '</div>' +
      '<p class="foot">Stop at my top note: off, the exercise only warns you; on, it ends before any round goes above your top. Stop one past last time: it ends one round past the highest top you last held cleanly while listening. When both are on, the earlier stop wins.</p>' +
      '<div class="grp setgap"><button class="row" data-a="patBridge"><span class="lbl">Your bridge</span><span class="mut">' +
      (v.bridge ? zoneName(v.bridge) : 'Not set') +
      '</span>' +
      chev +
      '</button></div>' +
      '<p class="foot">Where your voice flips. On the exercise pages it’s shaded on the drawing, and its notes play softer.</p>'
    );
  }
  function playerPage() {
    return (
      '<h1>Pattern player</h1>' +
      '<div class="hdr">Sound</div><div class="grp" role="radiogroup" aria-label="Sound">' +
      SOUNDS.map(
        (s) =>
          '<button class="row" data-a="patSoundPick" data-v="' +
          s.id +
          '" role="radio" aria-checked="' +
          (opt('sound') === s.id) +
          '"><span class="lbl">' +
          s.name +
          '</span><span class="acc setchk" aria-hidden="true">' +
          (soundOf(opt('sound')).id === s.id ? ICON.check : '') +
          '</span></button>'
      ).join('') +
      '</div><div class="grp setgap">' +
      sw('patDrone', !!opt('drone'), 'Held note underneath', 'The key an octave down, under each round') +
      sw(
        'patCue',
        !!opt('cue'),
        'Chord before each round',
        'The new key’s chord, then the pattern, like a teacher setting up each round'
      ) +
      '</div>' +
      '<div class="hdr">Your bridge</div><div class="grp">' +
      sw('patBCue', !!opt('bcue'), 'Bridge cue', 'Thinner · quieter, while a note in your bridge plays') +
      sw('patListen', !!opt('listen'), 'Listen while I sing', 'Your voice as a dot on the drawing. Headphones in, so it only hears you') +
      '</div>' +
      '<div class="hdr">Ending</div><div class="psetbox">' +
      segH(
        'patEnding',
        [
          ['chord', 'Home chord'],
          ['note', 'Home note'],
          ['off', 'Off'],
        ],
        opt('ending'),
        'Ending'
      ) +
      '</div>' +
      '<p class="foot">After the last round it brings you back to the starting key, as a teacher does at the piano. Stop fades out gently either way.</p>' +
      '<div class="hdr">Vowel cue</div><div class="psetbox">' +
      segH(
        'patVowel',
        [
          ['ex', 'Syllables'],
          ['all', 'Mixed vowels'],
          ['off', 'Off'],
        ],
        opt('vowel'),
        'Vowel cue'
      ) +
      '</div>' +
      '<p class="foot">Shows what to sing each round on exercises sung on open vowels, with a scale pattern.</p>' +
      '<div class="hdr">Notes on the drawing</div><div class="psetbox">' +
      segH(
        'patNotes',
        [
          ['dots', 'Dots'],
          ['notes', 'Music notes'],
        ],
        opt('notes'),
        'Notes on the drawing'
      ) +
      '</div>'
    );
  }

  /* ===== Getting around ===== */
  // the page the player is on: an exercise's Summary (pushed, or in the iPad's split pane) or the Patterns page
  const onPage = () =>
    U.view === 'pat' ||
    (U.view === 'keyp' && !!cfg && !!cfg.guest) ||
    ((U.view === 'ex' || (!U.view && U.tab === 'exercises' && typeof split === 'function' && split())) &&
      U.exTab === 'summary' &&
      !!cfg &&
      cfg.key === U.exId);
  function open() {
    if (!cfg) return;
    S.group = pat().g;
    go(() => {
      U.patFrom = U.view;
      U.view = 'pat';
    });
  }
  function back() {
    stopPreview();
    go(() => {
      U.view = U.patFrom === 'ex' || U.patFrom === 'keyp' ? U.patFrom : null;
      U.patFrom = null;
    });
  }
  function pick(n) {
    if (!cfg) return;
    putEx(cfg.key, 'p', +n === cfg.def ? null : +n);
    S.round = Math.min(S.round, Math.max(0, route().length - 1));
    preview(byN(n));
  }
  function toggleFav(n) {
    n = +n;
    const f = favs().slice(),
      i = f.indexOf(n);
    if (i < 0) f.push(n);
    else f.splice(i, 1);
    put('fav', f);
    toast(i < 0 ? 'Added to Favourites' : 'Removed from Favourites');
    paintPage();
  }
  function shift(d) {
    if (!cfg) return;
    putEx(cfg.key, 'off', off() + d || null);
    const r = route(),
      rc = rangeCheck(),
      w = rc && (rc.out.find((x) => x.kind === (d > 0 ? 'high' : 'low')) || rc.out[0]);
    toast(
      (w ? '⚠ ' : '') +
        (d > 0 ? 'Higher' : 'Lower') +
        ' · starts on ' +
        nameOf(r[0]) +
        (w ? ' · ' + warnText(w, true) : '') +
        (S.playing ? ' · next round' : ''),
      2600,
      w ? 'long' : ''
    );
    if (!S.playing) {
      redraw();
      sample((t) => note(r[0], t, 0.5, bus, opt('sound'), 1));
    }
    paintAll();
  }
  function hold() {
    S.hold = !S.hold;
    toast(S.hold ? 'Staying on ' + nameOf(keyNow()) : 'Moving up again');
    paintAll();
  }
  function soundMenu(el) {
    menu(
      el,
      'Sound',
      SOUNDS.map((x) => [x.id, x.name]).concat([
        ['-', 'Under each round'],
        ['__drone', 'Held note underneath', !!opt('drone')],
      ]),
      soundOf(opt('sound')).id,
      (k) => {
        if (k === '__drone') {
          put('drone', !opt('drone'));
          toast('Held note underneath ' + (opt('drone') ? 'on' : 'off'));
          return;
        }
        put('sound', k);
        rerender();
        sampleSound();
      }
    );
  }
  function sampleSound() {
    const r = route(),
      k = r.length ? r[0] : 60;
    sample((t) => round(k, t, byN(2), 0.3));
  }
  // what the main Settings list shows for the two pages
  const vals = () => ({ voice: voice().type, player: soundOf(opt('sound')).name });

  // stop when the page isn't on screen any more, or the app goes to the background
  function after() {
    const on = onPage() && !!cfg && route().length > 0;
    const pd = document.querySelector('#dock .pdock');
    document.body.classList.toggle('patdock', on && U.view !== 'pat' && !U.sheet && !!pd);
    // iPad's split view: the dock sits under the exercise's pane, not across the list
    const din = document.getElementById('dock'),
      pane = pd && document.querySelector('#app .split .pane');
    if (pane) {
      const r = pane.getBoundingClientRect(),
        d = din.parentElement.getBoundingClientRect(),
        pl = parseFloat(getComputedStyle(din.parentElement).paddingLeft) || 0;
      din.style.maxWidth = Math.min(430, r.width) + 'px';
      din.style.margin = '0 0 0 ' + Math.max(0, r.left - d.left - pl + (r.width - Math.min(430, r.width)) / 2) + 'px';
    } else if (din.style.margin) {
      din.style.maxWidth = '';
      din.style.margin = '';
    }
    if (!onPage()) {
      if (S.playing) end(false);
      if (S.preview != null) stopPreview();
      closeHud();
      closeMenu();
    } else if (S.playing || S.preview != null) {
      tick();
      if (U.view === 'pat' && S.playing) end(false);
    }
    // Q38 Find your bridge lets go of the microphone once its sheet goes
    if (U.sheet !== 'bridge' && (FB.stop || FB.phase !== 'ready')) fbReset();
  }
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) return;
    if (keep) keep.pause(); // the silent-switch loop never plays in the background
    if (S.playing) end(false);
    if (S.preview != null) stopPreview();
    if (FB.phase === 'listening') fbDone();
  });

  /* ===== Actions ===== */
  Object.assign(SG_ACT, {
    patPlay: () => play(),
    patHold: () => hold(),
    patShift: (el, v) => shift(+v),
    patOpen: () => open(),
    patBack: () => back(),
    patSound: (el) => soundMenu(el),
    patSpd: () => {
      if (Date.now() - heldAt < 600) return; // the hold already opened it
      openHud();
      later();
    },
    patSpdStep: (el, v) => {
      setSpeed(spdIx() + +v, true);
      later();
    },
    patRamp: () => {
      put('ramp', !opt('ramp'));
      if (!opt('ramp')) S.rampOff = 0;
      toast(opt('ramp') ? 'Speeds up one step each round, up to 2×' : 'Steady speed');
      hudDraw();
      paintDock();
      later();
    },
    patHudClose: () => closeHud(),
    patMenuClose: () => closeMenu(),
    patMenuPick: (el, v) => {
      const f = menuFn;
      closeMenu();
      if (f) f(v);
    },
    patGroup: (el, v) => {
      segPick(el);
      S.group = v;
      el.closest('.seg')
        .querySelectorAll('.pfseg')
        .forEach((b) => (b.innerHTML = IC.star(v === 'f')));
      const t = document.getElementById('pTiles');
      if (t) t.innerHTML = tilesHTML();
    },
    patPick: (el, v) => {
      if (Date.now() - holdEnd < 450) return; // a press and hold shows what it trains; it never picks
      pick(v);
    },
    patWin: (el, v) => {
      if (S.preview === +v) stopPreview();
      else preview(byN(v));
    },
    patFav: (el, v) => toggleFav(v),
    patVoice: () => {
      if (S.playing) end(false);
      go(() => {
        U.setFrom = { tab: U.tab, view: U.view };
        U.view = 'set';
        U.setPg = 'voice';
      });
    },
    patVoiceType: (el) =>
      menu(
        el,
        'Voice type',
        Object.keys(VOICES)
          .map((t) => [t, t])
          .concat(voice().type === 'Custom' ? [['Custom', 'Custom']] : []),
        voice().type,
        (k) => {
          const v = VOICES[k];
          if (!v) return;
          put('voice', Object.assign({}, voice(), { type: k, lo: v[0], hi: v[1], fal: v[2] })); // the bridge stays
          rerender();
        }
      ),
    patNudge: (el, v, k) => {
      const o = Object.assign({}, voice());
      o[v] = Math.max(24, Math.min(108, o[v] + +k));
      o.type = 'Custom';
      put('voice', o);
      rerender();
    },
    patStopTop: () => {
      put('stopTop', !opt('stopTop'));
      S.round = 0;
      rerender();
    },
    // Q38
    patStopLast: () => {
      put('stopLast', !opt('stopLast'));
      S.round = 0;
      rerender();
    },
    patBCue: () => {
      put('bcue', !opt('bcue'));
      rerender();
    },
    patListen: () => {
      put('listen', !opt('listen'));
      if (!opt('listen')) listenStop();
      else listenStart(); // only while playing; in this tap
      if (U.view === 'set') rerender();
      else paint(); // nothing redrawn while playing
    },
    patBridge: () => fbOpen(),
    bfStart: () => fbStart(),
    bfStop: () => fbDone(),
    bfFeel: () => {
      fbStop();
      FB.phase = 'done';
      FB.feel = true;
      rerender();
    },
    bfStep: (el, v, k) => {
      if (v !== 'lo' && v !== 'hi') return;
      FB[v] = Math.max(24, Math.min(108, FB[v] + +k));
      if (FB.lo > FB.hi) {
        if (v === 'lo') FB.hi = FB.lo;
        else FB.lo = FB.hi;
      }
      ['lo', 'hi'].forEach((x) => {
        const b = document.getElementById('bf_' + x);
        if (b) b.textContent = nameOf(FB[x]);
      });
    },
    bfUse: () => {
      setBridge(FB.lo, FB.hi);
      fbReset();
      toast('Bridge set · ' + zoneName(bridge()));
      closeSheet();
    },
    patSoundPick: (el, v) => {
      put('sound', v);
      rerender();
      sampleSound();
    },
    patDrone: () => {
      put('drone', !opt('drone'));
      rerender();
    },
    patCue: () => {
      put('cue', !opt('cue'));
      rerender();
    },
    patEnding: (el, v) => {
      segPick(el);
      put('ending', v);
      if (v !== 'off') {
        const r = route(),
          k = r.length ? r[0] : 48;
        sample((t) => chord(homeNotes(k), t, 1.6, bus, 0.75));
      }
    },
    patVowel: (el, v) => {
      segPick(el);
      put('vowel', v);
    },
    patNotes: (el, v) => {
      segPick(el);
      put('notes', v);
    },
  });

  /* ===== Press and hold a pattern tile: what it trains fades in; letting go fades it back. A hold never picks ===== */
  let tileT = 0,
    tileEl = null,
    holdEnd = 0,
    tx = 0,
    ty = 0;
  document.addEventListener('pointerdown', (e) => {
    const t = e.target.closest && e.target.closest('.pt[data-hold]');
    if (!t) return;
    tileEl = t;
    tx = e.clientX;
    ty = e.clientY;
    clearTimeout(tileT);
    tileT = setTimeout(() => {
      if (tileEl === t) t.classList.add('held');
    }, 450);
  });
  document.addEventListener('pointermove', (e) => {
    if (tileEl && Math.hypot(e.clientX - tx, e.clientY - ty) > 10 && !tileEl.classList.contains('held')) {
      clearTimeout(tileT);
      tileEl = null;
    }
  });
  const tileUp = () => {
    clearTimeout(tileT);
    if (tileEl && tileEl.classList.contains('held')) {
      holdEnd = Date.now();
      const t = tileEl;
      setTimeout(() => t.classList.remove('held'), 60);
    }
    tileEl = null;
  };
  document.addEventListener('pointerup', tileUp);
  document.addEventListener('pointercancel', tileUp);
  document.addEventListener('contextmenu', (e) => {
    if (e.target.closest && e.target.closest('.pt[data-hold], #pSpd')) e.preventDefault();
  });

  return {
    LIB,
    GROUPS,
    SUBS,
    FAV_SEED,
    SPEEDS,
    VOICES,
    SOUNDS,
    byN,
    isMinor,
    notes,
    nameOf,
    clean,
    use,
    card,
    dock,
    page,
    voicePage,
    playerPage,
    vals,
    after,
    onPage,
    route,
    full,
    rangeCheck,
    pat,
    play,
    stop,
    preview,
    hear,
    hearStop: () => stopPreview(),
    guest,
    tone,
    toneStop,
    toneState: () => (toneNow ? { m: toneNow.m, repeat: toneNow.repeat, strikes: toneNow.strikes || 0 } : null),
    // Q38
    bridge,
    setBridge,
    bridgeSheet,
    cueOf,
    BRIDGE_VOL,
    fbState: () => ({
      phase: FB.phase,
      listening: !!FB.stop,
      lo: FB.lo,
      hi: FB.hi,
      jumps: FB.jumps.map((j) => ({ t: j.t, from: j.from, to: j.to })),
      top: FB.top,
      points: FB.pts.length,
    }),
    // for the tests
    state: () => ({
      playing: S.playing,
      round: S.round,
      hold: S.hold,
      preview: S.preview,
      speed: SPEEDS[spdIx()],
      base: SPEEDS[baseIx()],
      pattern: pat().n,
      route: route(),
      full: full(),
      top: top(),
      voice: voice(),
      favs: favs(),
      opts: Object.keys(DEF).reduce((o, k) => ((o[k] = opt(k)), o), {}),
      ctx: AC ? AC.state : null,
      hud: hudOn,
      runs: runs.slice(),
      key: cfg ? cfg.key : null,
      bridge: bridge(),
      last: lastNow(),
      listening: !!LS,
      heard: LS ? LS.n : 0,
      cue: !!S.cue,
      guest: !!(cfg && cfg.guest),
      gx: cfg && cfg.guest ? Object.assign({}, cfg.gx) : null,
    }),
    triad,
    homeNotes,
    geom,
  };
})();
