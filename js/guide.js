/* Vocal Sessions · guide.js (Q04 · Marks: Practice Guide)
   Explains each mark where it's used, so you never have to leave the song to remember what a mark means.
   - GUIDE: every word of the guide, keyed by MK_DEF type, so a wording change is one edit here. Written in original
     words (approved 22 Oct 2026), never course text. tests/test_guide.py fails if a mark in MK_DEF has no text.
   - MKG: the guide's pages (U.view = 'guide', U.gPg = 'home' | 'how' | a mark's type), Key for this song (the sgKey
     sheet), the peek card (hold a mark button in the marks sheet) and the doors into them.
   Examples are drawn with MARKS.line() on a small section built from the sample words, so they look exactly like marks
   on a song. Nothing here is saved: the song's marks are only read.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

/* ===== Guide: the words =====
   Each mark: peek (the peek card's line and the guide rows' subtitle), what, how, when, ex (the example: w its words,
   m its marks as [type, option, first word, last word, text], it an Intention line above), vs (Don't confuse with:
   to the other mark's type, or none; t the difference), tech (the technical name, when there is one). */
const GUIDE = {
  lead: 'Every mark, what it means and how to sing it. Marks sit in four layers that follow the order you learn a song.',
  noteSub: 'Study reminders: trouble spots, the original, your version, questions',
  howSub: 'The four passes, and habits that help',
  marks: {
    pitch: {
      peek: 'Which way the next note goes, or check the first note.',
      what: 'An arrow for which way the note goes, or a reminder to find the first pitch of a phrase.',
      how: 'Hear the higher note in your head before you get there and keep the vowel tall. On falling notes keep your energy so they don’t go flat. For a starting note, hum it quietly first.',
      when: 'You keep going the wrong way, landing slightly off, or losing the key after a break.',
      ex: { w: 'calls me back again', m: [['pitch', 'Up', 2]] },
      vs: { to: 'slide', t: 'Pitch says where the note goes. Slide says how you travel there.' },
    },
    slide: {
      tech: 'portamento',
      peek: 'Glide into, off or between notes.',
      what: 'Gliding smoothly through the pitches. A scoop starts just below and slides up, a fall-off drops away at the end, and slide between joins two notes.',
      how: 'Keep it short and on purpose, usually well under a second. Keep the air flowing through the glide and land exactly on the target.',
      when: 'The original does it, or you’re finding a note’s pocket with your slide-in method. Shrink the slide each time until you land straight on.',
      ex: { w: 'along the water', m: [['slide', 'Scoop up', 2]] },
      vs: { to: 'ornament', t: 'A slide is one smooth glide. An ornament has separate quick notes.' },
    },
    hold: {
      peek: 'How long the note lasts.',
      what: 'A line running past the word to show how far the note sustains.',
      how: 'Keep the vowel steady and the air moving to the end of the line, then release on time.',
      when: 'You cut notes short, or breathe too early at the end of a line.',
      ex: { w: 'that never stay', m: [['hold', '', 2]] },
      vs: { to: 'stress', t: 'Stress is an underline under the word only. Hold runs past it.' },
    },
    ornament: {
      peek: 'Quick extra notes that decorate the melody.',
      what: 'Run: several notes on one syllable. Riff: a short stylish pattern. Turn: a quick circle around a note. Flip: a light jump up and back. Grace note: one tiny note just before the main one.',
      how: 'Learn it slowly on “ah”, note by note, then speed up. Lock in the first and last notes before the middle. Many pop runs sit on the pentatonic scale.',
      when: 'The original decorates a note, or you add your own. Pair your own with a My version note.',
      ex: { w: 'that never stay', m: [['ornament', 'Run', 2]] },
      vs: { to: 'slide', t: 'Ornaments have distinct notes you could sing one by one. Slides don’t.' },
    },
    rhythm: {
      peek: 'Where the words sit against the beat.',
      what: 'Pushed: slightly early, for urgency. Laid back: slightly late without slowing down. Off the beat: the stress lands between beats (syncopation).',
      how: 'Feel the pulse first by tapping or nodding, then place the words against it. The tempo never changes.',
      when: 'A line sounds stiff next to the original, or you keep rushing.',
      ex: { w: 'counting lights', m: [['rhythm', 'Pushed', 1]] },
      vs: { to: '', t: 'Song Clock timing records when a line happens. Rhythm says how it feels against the beat.' },
    },
    phrase: {
      peek: 'One musical sentence, sung as one gesture.',
      what: 'A bracket over the words that make one musical thought.',
      how: 'Keep the air moving and the notes joined from the first word to the last, like saying one sentence without stopping.',
      when: 'On every song while you learn it, especially where a phrase crosses a line break.',
      ex: { w: 'Walking slow along the water', m: [['phrase', '', 0, 4]] },
      vs: { to: '', t: 'A lyric line is how the words are laid out and timed. A phrase is how the music breathes.' },
    },
    chain: {
      peek: 'No reset between two phrases.',
      what: 'A link meaning you don’t breathe or start fresh between two phrases. The second carries on from the first.',
      how: 'Take a breath before the chain that’s big enough for both, and keep your energy up through the join.',
      when: 'One thought runs across two phrases, or the original goes straight through. A missing breath mark is undecided; a chain is a decision.',
      ex: {
        w: 'Hold on, hold on till the morning breaks',
        m: [
          ['phrase', '', 0, 3],
          ['chain', '', 3],
          ['phrase', '', 4, 7],
        ],
      },
      vs: { to: 'carry', t: 'Chain joins two phrases. Carry joins two words.' },
    },
    peak: {
      peek: 'The word the phrase leans towards.',
      what: 'A small tick over the point of greatest energy. It’s often the highest note, but not always.',
      how: 'Build towards it and ease off after it. One peak per phrase; two cancel each other out.',
      when: 'A phrase sounds flat, or every word gets the same weight.',
      ex: { w: 'Walking slow along the water', m: [['peak', '', 4]] },
      vs: { to: 'stress', t: 'Stress marks meaning. Peak marks the top of the musical arc.' },
    },
    breath: {
      peek: 'Where you breathe, and what kind.',
      what: 'Full: a planned, low breath where there’s time. Quick: a fast catch breath. Sneak: a tiny hidden top-up.',
      how: 'Breathe for the phrase that’s coming and start singing straight after. Holding the breath first locks up your upper body.',
      when: 'You run out, gasp, or breathe in the middle of a word.',
      ex: { w: 'counting lights that never stay', m: [['breath', 'Full', 4]] },
      vs: { to: 'shape', t: 'Shape’s ending is how the note finishes. Breath is taking in air afterwards.' },
    },
    shape: {
      peek: 'How the volume moves, and how the phrase ends.',
      what: 'Swell gets louder, Fade gets softer, Arc grows to the peak then eases. Endings: cut is a clean stop, release lets go on the air, fade dies away.',
      how: 'Change volume with breath energy, not by squeezing your throat. For a cut, place the final consonant right on the beat.',
      when: 'Everything comes out at one volume, or your line endings are untidy.',
      ex: { w: 'every corner calls me back again', m: [['shape', 'Swell', 0, 5]] },
      vs: { to: 'peak', t: 'Peak is one word. Shape covers the whole phrase.' },
    },
    vowel: {
      peek: 'The shape of the vowel on a note.',
      what: 'Tall: more height inside, lips slightly round. Open: relaxed, dropped jaw. Modified: shifts towards a more open neighbour on high notes. Hold first vowel: for two-part vowels like “time” (ah + ee). Sing as: type the sound you want.',
      how: 'Shape the vowel before the note starts and keep it steady through the note.',
      when: 'Long or high notes, words that sound pinched, and any diphthong you hold.',
      ex: { w: 'counting lights', m: [['vowel', 'Hold first vowel', 1, 1, 'ah→ee']] },
      vs: { to: 'say', t: 'Vowel shapes the tone of a note. Say gets the word itself right.' },
    },
    carry: {
      peek: 'Move a final consonant onto the next word.',
      what: 'Keeps the vowel long and the line joined (legato). “back again” becomes “ba‿kagain”.',
      how: 'Hold the vowel for the note’s full length, then land the consonant at the start of the next word. l, m, n and v can carry the tone straight through.',
      when: 'A line sounds choppy, or you rush to final consonants and clip the vowels.',
      ex: { w: 'calls me back again', m: [['carry', '', 2]] },
      vs: { to: 'chain', t: 'Carry joins two words. Chain joins two phrases.' },
    },
    onset: {
      peek: 'How a word begins.',
      what: 'Soft: air and sound start together, your everyday default. Breathy: a little air comes first. Hard: a crisp start, like “apple”.',
      how: 'For soft, imagine gently fogging a mirror. For hard, close briefly and release lightly, never a cough.',
      when: 'An entry sounds blurry or harsh, or the style calls for a particular start.',
      ex: { w: 'every corner', m: [['onset', 'Hard', 0]] },
      vs: { to: 'colour', t: 'Onset is only the first moment of a sound. Breathy colour lasts the whole line.' },
    },
    stress: {
      peek: 'The word that carries the meaning.',
      what: 'An underline under the most important word in the line.',
      how: 'Give it a little more weight, length or a clearer consonant. It doesn’t need to be louder. Little words like “the” rarely get it.',
      when: 'A line sounds like a list of equal words, or the meaning gets lost.',
      ex: { w: 'calls me back again', m: [['stress', '', 2, 2]] },
      vs: { to: 'peak', t: 'Stress is about meaning. Peak is the top of the musical arc.' },
    },
    say: {
      peek: 'How to pronounce a word.',
      what: 'A note for unfamiliar words, other languages, accents or style choices like “gonna”.',
      how: 'Write the sound the way you’d read it, split into syllables: “mor-nin”, “ma-hal”.',
      when: 'You keep stumbling on a word, or you’re singing in a language you use less often.',
      ex: { w: 'till the morning', m: [['say', '', 2, 2, 'mor-nin']] },
      vs: { to: 'vowel', t: 'Say gets the word right. Vowel shapes the tone of one note.' },
    },
    register: {
      peek: 'Which part of your voice to use.',
      what: 'Chest: your speaking voice, full and grounded. Head: your upper register, sung with real connection. Mix: a blend around your break. Falsetto: light and airy. Flip here: where you change on purpose.',
      how: 'Start preparing a few notes before your break, not on it. Don’t drag chest voice higher than it wants to go, and keep vowels slightly narrower near the break.',
      when: 'Your voice cracks or strains on a line, or the original clearly changes quality.',
      ex: {
        w: 'calls me back again',
        m: [
          ['register', 'Flip here', 2],
          ['register', 'Head', 3],
        ],
      },
      vs: {
        to: 'colour',
        t: 'Register is which part of the voice. Colour is the quality on top. Register’s Flip here also differs from the Flip ornament, which is a decoration.',
      },
    },
    colour: {
      peek: 'The tone quality of a line.',
      what: 'Light and Full set the weight. Belt is a confident call carried high. Cry is soft and sob-like. Twang is bright and ringing. Breathy lets air into the tone.',
      how: 'Find each through speech: belt is calling across a street, cry is a sympathetic “aww”, twang is a teasing “nyah nyah”.',
      when: 'The original changes tone between sections, or your sound stays the same all the way through.',
      ex: {
        w: 'Hold on, hold on',
        m: [
          ['register', 'Mix', 0],
          ['colour', 'Belt', 0],
        ],
      },
      vs: { to: 'register', t: 'Colour is the quality on top. Register is which part of the voice.' },
    },
    vibrato: {
      peek: 'Let the note shimmer, or keep it straight.',
      what: 'Vibrato is the natural, gentle wobble of a relaxed, supported note. Straight tone has none.',
      how: 'A common pop pattern is to start straight and let vibrato bloom near the end. Keep the throat open, and never fake vibrato with your jaw.',
      when: 'Held notes and the ends of phrases.',
      ex: { w: 'till the morning breaks', m: [['vibrato', 'Start vibrato', 3]] },
      vs: { to: 'ornament', t: 'A turn is notes you choose. Vibrato is a natural movement of one note.' },
    },
    mic: {
      peek: 'Change your distance from the mic.',
      what: 'Pull back on big, high notes so they don’t blast. Come close on soft lines for warmth (the proximity effect).',
      how: 'Keep singing into the mic as you move. When recording on your phone, move back a little on big notes.',
      when: 'You perform with a mic, or your recordings clip on loud notes.',
      ex: { w: 'till the morning breaks', m: [['mic', 'Pull back', 3]] },
      vs: { to: 'shape', t: 'Shape changes how loud you sing. Mic changes how loud you’re heard.' },
    },
    intention: {
      peek: 'What you mean in this section.',
      what: 'One short line above a section: who you’re singing to and what you want them to feel.',
      how: 'Think it before the section starts and let it change your breath and phrasing.',
      when: 'Last, once the song is secure, or whenever a performance feels empty. Feeling cues like this are strong memory landmarks.',
      ex: { it: 'to someone who isn’t coming back', w: 'every corner calls me back again', m: [] },
      vs: { to: 'note', t: 'Intention is a performance choice. Notes are study reminders.' },
    },
    note: {
      peek: 'A study reminder that shows on every layer.',
      what: 'Trouble spot, Original does…, My version, or Question. Notes use a bookmark, never the orange timing flag.',
      how: 'Keep it short. Delete a trouble spot once it’s fixed. Nothing is scored.',
      when: 'Anything you want to come back to.',
      ex: { w: 'calls me back again', m: [['note', 'Trouble spot', 3]] },
      vs: { to: 'intention', t: 'Notes are study reminders. Intention is a performance choice.' },
    },
  },
  how: {
    title: 'How to mark a song',
    lead: 'Work in four passes, one layer at a time. Each layer builds on the one before.',
    passes: [
      [
        'Notes',
        'Sing the melody on “nah” or “loo”, no words. Listen for jumps, slides, held notes, runs and lines that sit ahead of or behind the beat. Bookmark any note that needs your slide-in method.',
      ],
      [
        'Phrasing',
        'Still on “nah”. Decide your breaths first, then bracket each phrase, chain the ones with no reset, pick one peak each and add Shape.',
      ],
      [
        'Words',
        'Add the lyrics and check the notes are still right. Mark vowels on long or high notes, diphthongs, carried consonants, onsets and the key words.',
      ],
      ['Delivery', 'Register changes first, then colour, vibrato and mic. Write one intention line per section last.'],
    ],
    habitsTitle: 'Habits that make marks work',
    habits: [
      ['Hear it twice, then mark.', 'Your first guess is often wrong.'],
      ['Test every mark by singing it.', 'If it doesn’t change how you sing, delete it.'],
      ['Loop back.', 'If a line falls apart with words, sing it on “nah” again.'],
      // shown since Q05's suggested breaths exist (3.28): a gap of CK_SB after a placed line
      [
        'Let timing help.',
        'Where your timing leaves a gap after a line, a faint suggested breath appears on the Phrasing layer while you’re marking. Tap it to keep it.',
      ],
      ['Feeling and structure help memory most.', 'Give every section at least one Intention, Phrase or Shape.'],
    ],
  },
  key: {
    title: 'Key for this song',
    lead: 'Only the marks this song uses. Tap one to learn it.',
    empty: 'No marks yet. Add marks with the pencil.',
  },
};

/* ===== Guide: pages, Key for this song, the peek card ===== */
const MKG = (() => {
  const HOLD = 480; // ms: holding a mark button this long opens its peek card
  const PAGES = () => ['home', 'how'].concat(Object.keys(MK_DEF));
  const valid = (pg) => PAGES().includes(pg);
  const keyOf = (pg) => (pg === 'home' ? 'mk:guide' : 'mk:' + pg);
  // the guide's own icon (Settings' tile, the grid's row): an open book
  const BOOK =
    '<svg viewBox="0 0 24 24"><path d="M12 6.6c-2.1-1.6-4.9-2.2-8.2-1.8v12.9c3.3-.4 6.1.2 8.2 1.8 2.1-1.6 4.9-2.2 8.2-1.8V4.8c-3.3-.4-6.1.2-8.2 1.8z"/><path d="M12 6.6v12.9"/></svg>';
  // How to mark a song: steps, one per pass
  const STEPS = '<svg viewBox="0 0 24 24"><path d="M4 19h4.5v-4.5H13V10h4.5V5.5H20"/></svg>';

  /* ----- where Back goes: the place the guide was opened from, and the guide pages before this one ----- */
  let ret = null,
    hist = [];
  function here() {
    return {
      tab: U.tab,
      view: U.view,
      songId: U.songId,
      sEdit: U.sEdit,
      sel: SG.sel ? Object.assign({}, SG.sel) : null,
      mk: MK.open ? Object.assign({}, MK.open) : null,
    };
  }
  function open(pg) {
    if (!valid(pg)) return;
    hidePeek();
    if (U.view === 'guide') {
      if (U.gPg === pg) return;
      hist.push(U.gPg);
      if (hist.length > 12) hist.shift();
    } else {
      ret = here();
      hist = [];
    }
    go(() => {
      U.view = 'guide';
      U.gPg = pg;
      U.sheet = null;
      U.sd = {};
    });
  }
  // code with no card to push from (a sheet's row, the peek card, the capsule): push the page anyway
  function push(pg) {
    if (!valid(pg)) return;
    ZOOM.armPush(keyOf(pg));
    open(pg);
  }
  function back() {
    if (U.view !== 'guide') return;
    if (hist.length) {
      const pg = hist.pop();
      return go(() => {
        U.gPg = pg;
      });
    }
    const r = ret || { tab: U.tab, view: null };
    ret = null;
    // a song page (the song's own page on iPhone, the Songs pane on iPad and Mac) is found again the way the song's
    // other pages find it, so a turn of the iPad on the way still lands on the song
    const song = r.songId && songById(r.songId) && (r.view === 'lyr' || (r.tab === 'songs' && !r.view));
    go(() => {
      if (song) {
        const p = ckReturnPlace();
        U.tab = p.tab;
        U.view = p.view;
        U.songId = r.songId;
        // the Marks side: the selection and its marks sheet as they were
        if (r.sEdit === 'annotate') {
          U.sEdit = 'annotate';
          SG.sel = r.sel;
          MK.open = r.mk;
          MK.err = '';
        }
      } else {
        U.tab = r.tab;
        U.view = r.view && r.view !== 'guide' ? r.view : null;
      }
      U.gPg = null;
    });
  }

  /* ----- drawing a mark's example with the real renderer ----- */
  function exSec(t) {
    const g = GUIDE.marks[t].ex;
    return {
      lines: [g.w.split(' ')],
      marks: (g.m || []).map((x, i) => ({
        id: 'gx' + i,
        L: MK_DEF[x[0]].L,
        type: x[0],
        opt: x[1] || '',
        line: 0,
        w0: x[2],
        w1: x[3] == null ? x[2] : x[3],
        text: x[4] || '',
      })),
    };
  }
  const word = (wi, w, d) => {
    const lab = MARKS.labRow(d);
    return (
      '<span class="w' +
      (lab ? ' hv' : '') +
      (d.cls.length ? ' ' + d.cls.join(' ') : '') +
      '">' +
      (lab ? lab + '<span class="wt">' + esc(w) + '</span>' : esc(w)) +
      '</span>'
    );
  };
  function example(t) {
    const g = GUIDE.marks[t].ex,
      sec = exSec(t),
      r = MARKS.line(sec, 0, () => true, word);
    return (
      '<div class="gdex">' +
      (g.it ? '<p class="mint">' + esc(g.it) + '</p>' : '') +
      '<p class="sgl' +
      (r.labelled ? ' hasv' : '') +
      '">' +
      r.html +
      '</p>' +
      r.notes
        .map((m) => '<p class="sgnote">' + MKI.bookmark + '<span><b>' + esc(m.opt) + '</b> ' + esc(m.text) + '</span></p>')
        .join('') +
      '</div>'
    );
  }

  /* ----- the pages ----- */
  const glyph = (t) => '<span class="gdg" aria-hidden="true">' + mkGlyph(t) + '</span>';
  const layerOf = (t) => (MK_DEF[t].L === 'note' ? 'Every layer' : mkLayerNum(MK_DEF[t].L) + ' · ' + mkLayerName(MK_DEF[t].L));
  // a row that opens a guide page; from the app's own pages it's a card (push on iPhone, zoom on iPad and Mac)
  function pageRow(pg, ic, name, sub, card) {
    return (
      '<button class="row gdrow" data-a="gdOpen" data-v="' +
      pg +
      '"' +
      (card ? ' data-zk="' + keyOf(pg) + '" data-push' : '') +
      '>' +
      ic +
      '<span class="lbl">' +
      esc(name) +
      (sub ? '<small>' + esc(sub) + '</small>' : '') +
      '</span>' +
      chev +
      '</button>'
    );
  }
  function home() {
    return (
      '<h1>Marks guide</h1><p class="gdlead">' +
      esc(GUIDE.lead) +
      '</p>' +
      '<div class="grp tiled">' +
      pageRow('how', '<span class="gdg gdhow" aria-hidden="true">' + STEPS + '</span>', GUIDE.how.title, GUIDE.howSub, true) +
      '</div>' +
      MK_LAYERS.map(
        (x, i) =>
          '<div class="hdr">' +
          (i + 1) +
          ' · ' +
          x[1] +
          '</div><div class="grp tiled">' +
          MK_BY[x[0]].map((t) => pageRow(t, glyph(t), MK_DEF[t].n, GUIDE.marks[t].peek, true)).join('') +
          '</div>'
      ).join('') +
      '<div class="hdr">Every layer</div><div class="grp tiled">' +
      pageRow('note', glyph('note'), MK_DEF.note.n, GUIDE.noteSub, true) +
      '</div>' +
      // kept from the Marks key this page replaces
      '<div class="grp tiled setgap"><div class="row"><span class="gdg gdmut" aria-hidden="true">' +
      SGI.link +
      '</span><span class="lbl">Linked<small>A section shared with its repeats, and their marks</small></span></div></div>' +
      '<p class="foot">Only one layer shows at a time. Add or change marks with the pencil.</p>'
    );
  }
  function chips(t) {
    const d = MK_DEF[t],
      o = d.opts.length ? d.opts : [mkTakesText(t, '') ? 'Your own words' : 'One tap'];
    return (
      '<div class="gdopts" aria-label="Options">' + o.map((x) => '<span class="gdchip">' + esc(x) + '</span>').join('') + '</div>'
    );
  }
  function mark(t) {
    const d = MK_DEF[t],
      g = GUIDE.marks[t],
      vs = g.vs,
      sec = (h, body) => '<div class="hdr exh">' + h + '</div><div class="grp">' + body + '</div>',
      prose = (s) => '<div class="prose">' + esc(s) + '</div>';
    return (
      '<span class="tile big gdbig" aria-hidden="true">' +
      mkGlyph(t) +
      '</span><h1>' +
      esc(d.n) +
      '</h1><div class="ex-h"><span class="badge">' +
      layerOf(t) +
      '</span>' +
      (g.tech ? '<span class="badge">' + esc(g.tech) + '</span>' : '') +
      '</div>' +
      chips(t) +
      sec('What it is', prose(g.what)) +
      sec('How to sing it', prose(g.how)) +
      sec('When to mark it', prose(g.when)) +
      sec('Example', example(t)) +
      sec(
        'Don’t confuse with',
        vs.to && MK_DEF[vs.to]
          ? pageRow(vs.to, glyph(vs.to), MK_DEF[vs.to].n, vs.t, true)
          : prose(vs.t)
      )
    );
  }
  function how() {
    const H = GUIDE.how;
    return (
      '<h1>' +
      esc(H.title) +
      '</h1><p class="gdlead">' +
      esc(H.lead) +
      '</p>' +
      '<div class="grp"><div class="prose"><ol class="gdpass">' +
      H.passes.map((p) => '<li><b>' + esc(p[0]) + '.</b> ' + esc(p[1]) + '</li>').join('') +
      '</ol></div></div>' +
      '<div class="hdr exh">' +
      esc(H.habitsTitle) +
      '</div><div class="grp"><div class="prose gdhabits">' +
      H.habits.map((p) => '<p><b>' + esc(p[0]) + '</b> ' + esc(p[1]) + '</p>').join('') +
      '</div></div>'
    );
  }
  function page() {
    const pg = U.gPg;
    if (pg === 'how') return how();
    if (MK_DEF[pg]) return mark(pg);
    return home();
  }
  const title = () => (U.gPg === 'how' ? GUIDE.how.title : MK_DEF[U.gPg] ? MK_DEF[U.gPg].n : 'Marks guide');

  /* ----- Key for this song: only the marks the song uses, by layer, then its Notes ----- */
  function used(sg) {
    const by = {},
      notes = [],
      seen = new Set();
    if (!hasLyrics(sg)) return { by, notes };
    sg.order.forEach((x) => {
      const sec = sg.sections[x.sid];
      if (!sec || seen.has(x.sid)) return; // a linked repeat shares its section's marks: counted once
      seen.add(x.sid);
      MARKS.live(sec.marks).forEach((m) => {
        if (m.type === 'note') return notes.push({ m, sec });
        const u = by[m.type] || (by[m.type] = { n: 0, opts: new Set() });
        u.n++;
        if (m.opt) u.opts.add(m.opt);
      });
    });
    return { by, notes };
  }
  function keySheet() {
    const sg = songById(U.songId),
      K = GUIDE.key,
      u = used(sg),
      row = (t, name, sub) =>
        '<button class="row gdrow" data-a="gdKeyRow" data-v="' +
        t +
        '">' +
        glyph(t) +
        '<span class="lbl">' +
        esc(name) +
        (sub ? '<small>' + esc(sub) + '</small>' : '') +
        '</span>' +
        chev +
        '</button>';
    let h = '';
    MK_LAYERS.forEach((x, i) => {
      const ts = MK_BY[x[0]].filter((t) => u.by[t]);
      if (!ts.length) return;
      h +=
        '<div class="hdr">' +
        (i + 1) +
        ' · ' +
        x[1] +
        '</div><div class="grp tiled">' +
        ts
          .map((t) => {
            const o = MK_DEF[t].opts.filter((x) => u.by[t].opts.has(x));
            return row(t, MK_DEF[t].n, (o.length ? o.join(', ') + ' · ' : '') + u.by[t].n + ' in song');
          })
          .join('') +
        '</div>';
    });
    if (u.notes.length)
      h +=
        '<div class="hdr">Notes</div><div class="grp tiled">' +
        u.notes
          .map(({ m, sec }) =>
            row('note', m.opt || 'Note', m.text || (m.line >= 0 && sec.lines[m.line] ? 'On “' + mkWords(sec, m) + '”' : ''))
          )
          .join('') +
        '</div>';
    if (!h)
      return sheetWrap(
        K.title,
        '<p class="note gdempty">' +
          esc(K.empty) +
          '</p><div class="grp tiled">' +
          '<button class="row gdrow" data-a="gdKeyRow" data-v="home"><span class="gdg gdbook" aria-hidden="true">' +
          BOOK +
          '</span><span class="lbl">Marks guide</span>' +
          chev +
          '</button></div>'
      );
    return sheetWrap(K.title, '<p class="note gdklead">' + esc(K.lead) + '</p>' + h);
  }

  /* ----- the peek card: hold a mark button in the marks sheet ----- */
  let hold = null, // a press on a mark button, waiting to become a hold
    eat = 0, // until when the next click is eaten: the one that follows a hold, or a tap that only closed the card
    shown = null; // the type the card is showing
  function peekHTML(t) {
    const d = MK_DEF[t],
      g = GUIDE.marks[t];
    return (
      '<div class="mkpeek glass" id="mkpeek" role="dialog" aria-label="' +
      esc(d.n) +
      '" data-v="' +
      t +
      '"><div class="pkhd"><span class="mkt" aria-hidden="true">' +
      mkGlyph(t) +
      '</span><span class="pkt"><b>' +
      esc(d.n) +
      '</b><small>' +
      esc(d.opts.length ? d.opts.join(' · ') : mkTakesText(t, '') ? 'Your own words' : 'One tap') +
      '</small></span></div><p class="pkln">' +
      esc(g.peek) +
      '</p>' +
      example(t) +
      '<div class="pkbtns"><button class="sgpill" data-a="gdPeekClose">Close</button><button class="sgpill blue" data-a="gdPeekMore" data-v="' +
      t +
      '">Learn more</button></div></div>'
    );
  }
  function placePeek(c) {
    const sh = $('mksheet'),
      vw = document.documentElement.clientWidth,
      w = Math.min(340, vw - 16);
    c.style.width = w + 'px';
    const r = sh ? sh.getBoundingClientRect() : { left: 0, width: vw, top: innerHeight };
    const left = Math.max(8, Math.min(vw - 8 - w, r.left + r.width / 2 - w / 2));
    c.style.left = Math.round(left) + 'px';
    const sat = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--sat')) || 0,
      top = Math.max(8 + sat, r.top - 8 - c.offsetHeight);
    c.style.top = Math.round(top) + 'px';
  }
  function showPeek(t) {
    if (!MK_DEF[t] || !$('mksheet')) return;
    hidePeek();
    const tmp = document.createElement('div');
    tmp.innerHTML = peekHTML(t);
    const c = tmp.firstElementChild;
    document.body.appendChild(c);
    shown = t;
    placePeek(c);
    MOTION.animate(
      c,
      [
        { opacity: 0, transform: 'scale(.9)' },
        { opacity: 1, transform: 'none' },
      ],
      { spring: 'ripple', fade: true }
    );
  }
  function hidePeek() {
    const c = $('mkpeek');
    if (c) c.remove();
    shown = null;
  }
  // the hold: on a mark button in the marks sheet, still for HOLD ms; moving the finger cancels it
  document.addEventListener(
    'pointerdown',
    (e) => {
      const c = $('mkpeek');
      eat = 0; // a new press: only its own click can be eaten
      if (c && !c.contains(e.target)) {
        // a tap outside the card only closes it
        hidePeek();
        eat = Date.now() + 1500;
      }
      const b = e.target.closest && e.target.closest('#mksheet .mkb');
      if (!b || (e.button && e.pointerType === 'mouse')) return;
      clearTimeout(hold && hold.t);
      hold = {
        x: e.clientX,
        y: e.clientY,
        t: setTimeout(() => {
          if (!hold || !b.isConnected) return;
          hold.done = true;
          eat = Date.now() + 10000; // until the finger lifts
          showPeek(b.dataset.v);
        }, HOLD),
      };
    },
    true
  );
  document.addEventListener(
    'pointermove',
    (e) => {
      if (hold && !hold.done && Math.hypot(e.clientX - hold.x, e.clientY - hold.y) > 10) {
        clearTimeout(hold.t);
        hold = null;
      }
    },
    true
  );
  ['pointerup', 'pointercancel'].forEach((ty) =>
    document.addEventListener(
      ty,
      () => {
        if (!hold) return;
        clearTimeout(hold.t);
        if (hold.done) eat = Date.now() + 600;
        hold = null;
      },
      true
    )
  );
  // a hold never also taps the button (and the long press's own menu never shows). On window, so it runs before the
  // song page's own capture handler on document (which selects words)
  window.addEventListener(
    'click',
    (e) => {
      if (Date.now() < eat) {
        eat = 0;
        e.stopPropagation();
        e.preventDefault();
      }
    },
    true
  );
  document.addEventListener('contextmenu', (e) => {
    if (e.target.closest && e.target.closest('#mksheet .mkb')) e.preventDefault();
  });
  // a scroll (the page or the sheet) or leaving the app closes the card
  document.addEventListener(
    'scroll',
    (e) => {
      if (shown && !(e.target && e.target.id === 'mkpeek')) hidePeek();
    },
    true
  );
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) hidePeek();
  });
  window.addEventListener('resize', () => hidePeek());
  // after every redraw: the card goes when its marks sheet (or its button) has gone
  function after() {
    if (shown && !document.querySelector('#mksheet .mkb[data-v="' + shown + '"]')) hidePeek();
    else if (shown) placePeek($('mkpeek'));
  }

  Object.assign(SG_ACT, {
    gdOpen: (el, v) => (el.hasAttribute('data-zk') ? open(v) : push(v)),
    gdBack: () => back(),
    gdKey: () => {
      U.sheet = 'sgKey';
      U.sd = {};
      rerender();
    },
    gdKeyRow: (el, v) => push(v),
    gdPeekClose: () => hidePeek(),
    gdPeekMore: (el, v) => push(v),
  });

  return {
    page,
    title,
    keySheet,
    after,
    open,
    push,
    back,
    showPeek,
    hidePeek,
    BOOK,
    HOLD,
    // tests
    state: () => ({ ret: ret && Object.assign({}, ret), hist: hist.slice(), peek: shown }),
    used: (sg) => {
      const u = used(sg);
      return {
        by: Object.fromEntries(Object.entries(u.by).map(([k, v]) => [k, { n: v.n, opts: [...v.opts] }])),
        notes: u.notes.map((x) => x.m.id),
      };
    },
    exSec,
  };
})();
