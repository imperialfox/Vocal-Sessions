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

// COACH_TIMES: where each exercise starts in the coach video on your phone (Settings › Coach video), from the
// YouTube video's timestamps. Write times as 'm:ss' or 'h:mm:ss'. To jump straight to levels too, give three times
// instead of one, Level 1 first: falsetto: ['19:30', '21:10', '23:05']. Exercises with three times get the
// L1 · L2 · L3 picker in the player; the rest start from the top of the exercise.
const COACH_TIMES = {
  slides: ['0:00'],
  humming: ['7:15'],
  lip: ['13:10'],
  falsetto: ['19:30'],
  upperlower: ['24:45'],
  straw: ['26:45'],
  rung: ['32:40'],
  hinge: ['41:20'],
  half: ['48:37'],
  vertical: ['56:50'],
  nasal: ['1:04:30'],
  flex: ['1:11:00'],
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
    what: 'A vocal slide is a smooth glide from a low note to a high note and back down, with no gaps between pitches. It starts on a lip trill or a buzzy <i>ng</i>, then moves onto the vowels <i>hee, hoo, hoe, hah</i> and <i>hay</i>, keeping the buzz on the roof of the mouth. Short slides come first, then medium ones, then your full range, bending forward on the top notes. Levels 2 and 3 add a small bounce on the high notes.',
    why: 'Slides warm up the muscles that change pitch, much like stretching before a workout. Moving through every note joins chest voice and head voice, so there’s less of a break as you go higher. Keeping the sound light teaches the voice to thin out as it rises. If the top notes feel strained, sing quieter rather than pushing.',
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
    what: 'Humming is singing short melodic patterns with your lips closed. Keep the lips only lightly touching and the sound quiet and relaxed. You should feel a buzz around your nose and cheekbones, an area singers call the “mask”.',
    why: 'Humming is the simplest way to find forward placement, where the sound sits at the front of the face rather than falling into the back of the throat. That forward buzz helps notes stay clear and in tune, and makes higher notes easier to reach. If you feel the buzz in your throat instead, hum more quietly.',
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
    what: 'Lip bubbling, also called a lip trill, is a motorboat <i>brrr</i> made by blowing air through loose lips. You sing patterns through your whole range while the lips keep fluttering. If your lips won’t flutter, press your cheeks in and forward with your fingertips.',
    why: 'The trill keeps your lips, face and jaw relaxed from the bottom of your range to the top. It also balances your breath: with too much air the neck tenses, and with too little the trill stops. The aim is to move through chest, mixed and head voice with the same effort throughout. If the trill cuts out on high notes, keep the air flowing steadily rather than pushing harder.',
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
    what: 'Falsetto is the light, breathy voice that sits apart from your chest voice. In this exercise you sing flowing, wave-like patterns in falsetto on <i>hoo</i> and <i>hee</i>, then <i>woh</i> or <i>wah</i>, at whatever volume feels comfortable. Keep your teeth at least half an inch (about 1 cm) apart so your jaw doesn’t clamp.',
    why: 'Regular practice makes falsetto comfortable and controllable, so it becomes a sound you choose rather than one you slip into. If it feels tight, check your jaw is still loose before changing anything else.',
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
    what: 'This exercise trains your voice from high to low. Patterns start high and come down on <i>woh</i> or <i>woo</i>, then <i>we</i>, then <i>wah</i> or <i>way</i>. Sing them slowly and quietly, in slow motion, so you pass from head voice down into chest voice without a bump. You can also do them on a lip trill or through a straw.',
    why: 'Most practice works the voice upwards, and this trains the way down. The goal is no audible change in tone as you cross between registers in either direction. If you hear a bump on the way down, slow the pattern further rather than forcing through it.',
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
    what: 'Straw singing is humming and singing patterns through a straw into a cup of water, which adds a little resistance. Start with a wide straw and only a little water.',
    why: 'It’s a semi-occluded vocal tract (SOVT) exercise. The partly blocked airway creates back-pressure that lets your vocal folds vibrate with less effort. The bubbles show you straight away if your air stops flowing, which builds steady breath support. It should feel soothing, never like work; if it doesn’t, use a wider straw or less water.',
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
    what: 'This exercise uses the word <i>rung</i> to shape your sound. Sing patterns on <i>rung</i> with your jaw dropped open vertically, as far as is comfortable, and the tip of your tongue resting behind your lower front teeth. Keep it light and moderately quiet.',
    why: 'The <i>ng</i> keeps the sound forward, while the open jaw breaks the habit of a clamped or spread mouth. Kept light, it’s one of the most reliable ways to blend the tricky middle, or mixed, voice. If it starts to feel heavy, sing quieter.',
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
    what: 'The squeaky hinge is a glide on a creaky sound, like an old door hinge, usually on <i>hmmm</i>. Imagine the sound in the centre of your head, and aim high even on the low note. As you go up, let the sound get thinner and narrower.',
    why: 'It’s one of the most direct ways to find your mixed voice. With good placement and support, it can feel easy right up to your top notes, and it can also soothe a hoarse voice. If your throat tightens as you rise, let the sound get smaller rather than louder.',
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
    what: 'This is the second part of the squeaky hinge. You keep some of the squeak while blending in your normal singing tone, first on <i>wah</i>, then <i>bow</i>, then <i>way</i> or <i>wah</i>, with your jaw dropped open.',
    why: 'It bridges the gap between an unusual exercise sound and your real singing voice. You keep the easy, forward placement of the squeak, with a tone you’d actually use on stage. If the squeak disappears completely, go back to more squeak and blend in your normal tone again gradually.',
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
    what: 'Vertical mouth exercises keep your mouth in a relaxed, tall oval rather than a wide smile. Sing patterns on <i>mum</i>, then <i>lum</i>, then <i>yum</i>, holding that shape throughout.',
    why: 'A spread, smiling mouth tightens the neck and makes high notes harder over time. The vertical shape gives a warmer tone and a freer throat, and many singers find it brings a new sense of freedom. Keep the oval relaxed; if your jaw starts to ache, it’s open too far.',
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
    what: 'This exercise uses a deliberately nasal sound to set your placement. Sing patterns on <i>may</i> and <i>me</i>, then <i>nay-yay</i>. The goal isn’t a nasal tone; it’s to lock in a forward placement.',
    why: 'It strengthens low notes, which become muffled and muddy when the sound drops into the back of the throat. It also gives you another smooth route into the mixed middle range. When you move on to a song, keep the forward feeling but let the nasal quality go.',
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
    what: 'Vocal flexibility exercises are scale patterns built on the pentatonic scale, sung on <i>woo</i>, then <i>woh</i> or <i>wah</i>, then <i>he</i>. Learn each pattern slowly and cleanly, then sing it a cappella, then speed it up.',
    why: 'The pentatonic scale is the template most R&amp;B and gospel runs are built on. Practising it builds agility and pitch accuracy at speed. Stay at each tempo until the notes come out clearly before going faster.',
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
