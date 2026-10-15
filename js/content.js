/* Vocal Sessions · content.js
   Everything about your practice that you might want to change: goals, the coach video, the exercises and their
   write-ups, the quick words, and the Toggl tags. The rest of the app reads these and never needs touching.

   Safe to change:  any text between quotes, goals in minutes, video timings, adding words to a list,
                    adding a new exercise to FOUND or ROT (with an id, name and focus, and ideally entries below).
   Never change:    an exercise's id ('slides', 'humming'…). Past sessions are saved under these ids,
                    so changing one would disconnect your history from that exercise.
   Text in write-ups can use <i>italics</i>, and must write & as &amp;.
   After a change, run  python tests/run.py content  to check everything still fits together.

   Plain script (not a module): loaded first, before the other files in js/. */

/* ===== Goals ===== */
// minutes: TARGET for the month, WEEK_TARGET for the week
const TARGET = 280,
  WEEK_TARGET = 70;

/* ===== Coach video ===== */
// VID: how long each exercise runs in the coach video, in seconds (all 3 levels), from its timestamps.
// Used to split a session's time when it was filled in at the end.
const VIDEO = 'https://youtu.be/rG-o10NggDI';
const VID = {
  slides: 435,
  humming: 355,
  lip: 380,
  straw: 355,
  falsetto: 315,
  upperlower: 120,
  rung: 520,
  hinge: 437,
  half: 493,
  vertical: 460,
  nasal: 390,
  flex: 420,
};

/* ===== Exercises ===== */
// focus is one of: 'cord-closure', 'register', 'resonance', 'agility', 'blend'. It sets the icon colour and a Toggl tag.
const FOUND = [
  { id: 'slides', name: 'Vocal slides', focus: 'agility' },
  { id: 'humming', name: 'Humming', focus: 'cord-closure' },
  { id: 'lip', name: 'Lip bubbling', focus: 'cord-closure' },
  { id: 'straw', name: 'Singing through a straw', focus: 'cord-closure' },
];
const ROT = [
  { id: 'falsetto', name: 'Falsetto voice', focus: 'register' },
  { id: 'upperlower', name: 'Upper to lower voice', focus: 'register' },
  { id: 'rung', name: 'Singing on the rung', focus: 'resonance' },
  { id: 'hinge', name: 'Squeaky hinge', focus: 'register' },
  { id: 'half', name: 'Half squeaky / half normal', focus: 'blend' },
  { id: 'vertical', name: 'Vertical mouth', focus: 'resonance' },
  { id: 'nasal', name: 'Nasal exercise', focus: 'resonance' },
  { id: 'flex', name: 'Vocal flexibility', focus: 'agility' },
];

/* ===== Quick words ===== */
// HOW_WORDS: "How did it go?"  TAKE_WORDS: notes on a recording  EX_WORDS: notes on each exercise (EX_WORDS_DEFAULT for your own)
const HOW_WORDS = [
  'Free',
  'Warm',
  'In control',
  'Clear tone',
  'Good placement',
  'Bit tight',
  'Breath ran short',
  'Strained',
  'Cracked on passaggio',
  'Voice tired',
];
const TAKE_WORDS = [
  'Nailed it',
  'Good tone',
  'Better than last time',
  'Flat on the high note',
  'Breathy',
  'Rushed the run',
  'Cracked',
];
const EX_WORDS = {
  slides: ['Smooth glide', 'Gaps in the middle', 'Light and easy', 'Pushed at the top'],
  humming: ['Buzz in the mask', 'Sound fell back', 'Relaxed lips', 'Felt forward'],
  lip: ['Even trill', 'Lips kept stopping', 'Jaw relaxed', 'Same effort top to bottom'],
  straw: ['Steady bubbles', 'Air kept stopping', 'Soothing', 'Easy climb'],
  falsetto: ['Light and free', 'Too breathy', 'Jaw stayed loose', 'Wobbly'],
  upperlower: ['No bump', 'Clunk into chest', 'Smooth way down', 'Lost volume'],
  rung: ['Jaw open', 'Through the passaggio', 'Got heavy', 'Forward ng'],
  hinge: ['Found the mix', 'Thinned out nicely', 'Squeak kept dropping', 'Effortless top notes'],
  half: ['Good blend', 'Too squeaky', 'Too heavy', 'Felt like real singing'],
  vertical: ['Tall vowel', 'Spread on high notes', 'Warm tone', 'Freer throat'],
  nasal: ['Low notes clear', 'Forward placement', 'Too nasal', 'Easy into the mix'],
  flex: ['Clean runs', 'Pitch slipped', 'Ready to speed up', 'Tripped on the run'],
};
const EX_WORDS_DEFAULT = ['Felt good', 'Tight today', 'Clear tone', 'Needed more warm-up'];

/* ===== Toggl tags ===== */
// added to the end of each line of Copy for Toggl; rotation exercises also get #<their focus>
const TOGGL = {
  foundation: '#foundation #cord-closure',
  rotation: '#rotation',
  application: '#application',
  song: '#song-practice',
};

/* ===== Exercise write-ups ===== */
// shown on each exercise's Summary tab: what it is, why it helps, and where it shows up in songs. n is the order in the coach video.
const DESC = {
  slides: {
    n: 1,
    what: 'Light, quiet glides from low to high and back on <i>hee, hoo, hoe, hah, hay</i>, keeping the buzz on the roof of your mouth. Short slides first, then medium, then your full range, bending forward on the top notes. Levels 2–3 add a bounce on the high notes.',
    why: 'It’s the vocal equivalent of stretching before a workout. Sliding through every pitch with no gaps starts blending chest and head voice, and keeping it light teaches the voice to thin out as it rises instead of pushing.',
    song: [
      [
        'Scoops and glides into notes',
        'R&amp;B singers constantly slide into a note rather than hitting it dead-on. Bruno Mars’s slides up into falsetto on <i>Leave the Door Open</i> are that siren in miniature.',
      ],
      [
        'Wide-range songs',
        'Do them before any song that runs from a low verse to a high chorus. Singers say slides right before a show make it feel like their range is opening.',
      ],
    ],
  },
  humming: {
    n: 2,
    what: 'Humming short melodic patterns with lips only lightly touching, quiet and relaxed, feeling a buzz around your nose and cheekbones (the “mask”).',
    why: 'It’s the easiest way to find forward placement: the sound sits up front rather than falling into the back of the throat. That forward buzz keeps notes clear, in tune and easier to reach higher.',
    song: [
      [
        'The first note',
        'Soft openings like the first verse of John Legend’s <i>All of Me</i> need that placement from note one, or the whole verse sounds muffled.',
      ],
      [
        'Quiet, close-to-the-mic moments',
        'Intimate R&amp;B verses (Daniel Caesar’s <i>Best Part</i>) are sung softly but still need to cut through. Humming trains “quiet but present”.',
      ],
    ],
  },
  lip: {
    n: 3,
    what: 'Blowing through loose lips to make a motorboat <i>brrr</i> while singing patterns through your whole range. If your lips won’t flutter, press your cheeks in and forward with your fingertips.',
    why: 'It keeps lips, face and jaw relaxed from bottom to top, and it balances breath: too much air and the neck tenses, too little and the trill stops. The aim is to pass through chest, mix and head voice with no change in effort.',
    song: [
      [
        'Running a whole song on a trill',
        'Try your hardest song on lip trills first, then sing the words. It keeps your breathing going through the tricky parts.',
      ],
      [
        'Pre-show nerves',
        'A go-to before going on stage for many singers. It also forces deeper breaths without you noticing.',
      ],
    ],
  },
  falsetto: {
    n: 4,
    what: 'Flowing, wave-like patterns in falsetto on <i>hoo</i>, <i>hee</i>, then <i>woh/wah</i>, at whatever volume feels comfortable. Teeth at least half an inch apart so the jaw doesn’t clamp.',
    why: 'Falsetto is the light, breathy voice that’s disconnected from chest voice. This makes it comfortable and controllable, so it becomes a colour you choose rather than something you fall into.',
    song: [
      [
        'Whole songs in falsetto',
        'Curtis Mayfield’s <i>Superfly</i> is sung almost entirely in falsetto. MJ’s <i>Don’t Stop ’Til You Get Enough</i> is the same idea at dance tempo.',
      ],
      [
        'Soft R&amp;B texture',
        'Daniel Caesar’s <i>Get You</i> lives in a light, airy upper voice. That relaxed falsetto is what this builds.',
      ],
      [
        'Hooks and ad-libs',
        'Bruno Mars uses falsetto for the sweet, high moments in <i>Leave the Door Open</i> and <i>Versace on the Floor</i>.',
      ],
    ],
  },
  upperlower: {
    n: 5,
    what: 'Patterns that start high and descend on <i>woh</i> / <i>woo</i>, <i>we</i>, then <i>wah/way</i>, sung slowly and quietly, in “slow motion”, so you pass from head voice down into chest with no bump. Can also be done on lip trills or through a straw.',
    why: 'Most people practise going up; this trains the way down. The goal is no audible change in tone as you cross between registers in either direction.',
    song: [
      [
        'Coming down from a peak',
        'After a high falsetto ad-lib, R&amp;B singers often slide straight back into the chest-voice melody. A clunk there sounds like two different singers.',
      ],
      [
        'Songs that sit between voices',
        'Melodies that keep crossing between head and chest sound disjointed until the registers blend.',
      ],
    ],
  },
  straw: {
    n: 6,
    what: 'Humming and singing patterns through a straw into water, which adds slight resistance. Start with a wide straw and little water; it should feel soothing, never like work.',
    why: 'It’s a semi-occluded (SOVT) exercise: the partial blockage creates back-pressure that lets your vocal folds vibrate with less effort. The bubbles show you instantly if your air stops flowing, which builds steady breath support.',
    song: [
      [
        'Mapping a hard song safely',
        'Sing the chorus of <i>When I Was Your Man</i> through the straw to learn the climb without straining, then sing it normally.',
      ],
      [
        'Recovery after a long day',
        'Voice therapists use straw work for rehab. Use it when your voice feels tired from talking at work before you sing anything.',
      ],
    ],
  },
  rung: {
    n: 7,
    what: 'Singing patterns on the word <i>rung</i>, jaw dropped open vertically as far as is comfortable, tongue tip resting behind the lower front teeth. Light and moderately quiet, never heavy.',
    why: 'The <i>ng</i> keeps the sound forward while the open jaw breaks the habit of a clamped or spread mouth. Kept light, it’s one of the best blenders for the tricky middle (mixed) voice.',
    song: [
      [
        'Tenor choruses in the passaggio',
        'A lot of Bruno Mars’s choruses sit right in the tenor middle zone, where voices crack or get shouty. <i>Rung</i> trains you to sail through it with an open jaw.',
      ],
      [
        'Big ballad climbs',
        'OPM power ballads like Side A’s <i>Forevermore</i> climb into a high chorus. The open, relaxed jaw stops the top notes getting pinched.',
      ],
    ],
  },
  hinge: {
    n: 8,
    what: 'Gliding on a creaky, squeaky-hinge sound (often on <i>hmmm</i>), imagining the sound in the centre of your head. Aim high even on the low note, and let the sound get thinner and narrower as you go up.',
    why: 'One of the best exercises for finding the mixed voice. With good placement and support it feels effortless right up to your top notes, and it can even soothe a hoarse voice.',
    song: [
      ['Songs with a big range', 'When a song spans low verses to a high chorus, the squeaky door bridges that gap.'],
      [
        'High mix instead of falsetto',
        'When an R&amp;B chorus needs power up high (think <i>When I Was Your Man</i>), you want a strong mix, not a flip into breathy falsetto. This is where that mix starts.',
      ],
    ],
  },
  half: {
    n: 9,
    what: 'Part two of the squeaky door. You keep some of the squeak while blending in your normal singing tone, on <i>wah</i>, then <i>bow</i>, then <i>way/wah</i>, with the jaw dropped open.',
    why: 'It’s the bridge from an odd exercise sound to your real singing voice. You keep the easy, forward placement of the squeak but with a tone you’d actually use on stage.',
    song: [
      [
        'Practising the hard line',
        'Sing whichever chorus line you keep cracking on half squeaky, half normal, then switch to full voice.',
      ],
      [
        'Keeping a climax easy',
        'When a song builds to its last big chorus, this blend lets you add power without the throat taking over.',
      ],
    ],
  },
  vertical: {
    n: 10,
    what: 'Patterns on <i>mum</i>, then <i>lum</i>, then <i>yum</i>, keeping the mouth in a relaxed vertical oval rather than a wide smile.',
    why: 'A spread, smiley mouth tightens the neck and makes high notes harder over time. The vertical shape gives a warmer tone and a freer throat; many singers find it brings a new sense of freedom.',
    song: [
      [
        'Emotional high notes',
        'The peak lines of a heartbreak ballad like <i>When I Was Your Man</i> are where singers grimace and spread. A vertical mouth keeps the tone warm instead of thin.',
      ],
      [
        'Smiling vs singing',
        'Even on a happy last note, keeping the mouth tall in your mix keeps the tone full. The vertical <i>yum</i> is a favourite warm-up for exactly that.',
      ],
    ],
  },
  nasal: {
    n: 11,
    what: 'Deliberately nasal patterns on <i>may</i>, <i>me</i>, then <i>nay-yay</i>. The goal isn’t a nasal tone; it’s to lock in a forward placement.',
    why: 'It strengthens low notes, which go muffled and muddy when the sound drops into the back of the throat. It also gives you another smooth route into the mixed middle range.',
    song: [
      [
        'Low verses that need to carry',
        '<i>Mee</i> and <i>may</i> bring muffled low notes forward, so a soft, low verse (like those in Daniel Caesar’s <i>Best Part</i>) stays clear instead of disappearing.',
      ],
      [
        'Bright, forward R&amp;B and pop tone',
        'Healthy “twang” comes from this placement. It’s why upbeat Bruno Mars tracks like <i>24K Magic</i> sound bright and cut through a busy mix.',
      ],
    ],
  },
  flex: {
    n: 12,
    what: 'Scale patterns built on the pentatonic scale, on <i>woo</i>, <i>woh/wah</i>, then <i>he</i>. Learn them slowly and cleanly, then sing them a cappella, then speed them up.',
    why: 'The pentatonic scale is the template most R&amp;B and gospel runs are built on. Drilling it builds agility and pitch accuracy at speed, but only if each tempo is clean before you go faster.',
    song: [
      [
        'Runs and riffs',
        'The melismas in R&amp;B ballads (Boyz II Men, Luther Vandross) are largely pentatonic shapes strung together.',
      ],
      [
        'Riffs that mean something',
        'A riff should “say” something even without words. Once the shapes are automatic, you can focus on the feeling rather than the notes.',
      ],
      [
        'Your ad-libs',
        'The final choruses of songs like <i>Leave the Door Open</i> are where runs go over the backing vocals.',
      ],
    ],
  },
};
