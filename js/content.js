/* Vocal Sessions · content.js
   Everything about your practice that you might want to change: goals, the coach video, the exercises and their
   write-ups and the quick words. The rest of the app reads these and never needs touching.

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
// VID: how long each exercise runs in the coach video, in seconds (all 3 levels), measured frame by frame (Q25: from
// its Level 1 to the next exercise's Level 1, so they add up to the video's 79:33). Used to split a session's time
// when it was filled in at the end.
const VIDEO = 'https://youtu.be/rG-o10NggDI';
const VID = {
  slides: 437.2,
  humming: 355.5,
  lip: 377.2,
  straw: 354.9,
  falsetto: 314.8,
  upperlower: 121.4,
  rung: 520.9,
  hinge: 435.9,
  half: 492.8,
  vertical: 459.6,
  nasal: 389.2,
  flex: 513.9,
};

// COACH_TIMES: where each level starts in the coach video on your phone (Settings › Coach video), Level 1 first.
// Q25: measured frame by frame from the video's green flash at each level's start (frame ÷ 24, to the hundredth of a
// second; the frames are in tools/coach-video/data/level_frames.json). Write times as 'm:ss.ff' or 'h:mm:ss.ff'
// ('m:ss' and 'h:mm:ss' still work). An exercise given one time instead of three has no L1 · L2 · L3 switch.
const COACH_TIMES = {
  slides: ['0:00.00', '2:02.96', '6:12.67'],
  humming: ['7:17.21', '9:35.50', '11:19.92'],
  lip: ['13:12.71', '15:39.75', '17:35.17'],
  falsetto: ['19:29.96', '21:11.17', '22:59.92'],
  upperlower: ['24:44.75', '25:34.92', '26:08.33'],
  straw: ['26:46.17', '28:34.17', '30:29.33'],
  rung: ['32:41.04', '35:55.25', '38:49.38'],
  hinge: ['41:21.96', '43:43.33', '45:55.62'],
  half: ['48:37.88', '51:59.54', '54:35.71'],
  vertical: ['56:50.62', '1:00:24.50', '1:02:34.96'],
  nasal: ['1:04:30.25', '1:06:08.62', '1:08:09.83'],
  flex: ['1:10:59.50', '1:13:37.54', '1:15:39.17'],
};

/* ===== Exercises ===== */
// focus is one of: 'cord-closure', 'register', 'resonance', 'agility', 'blend'. It sets the icon colour.
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
// Q19 the one-page session: EX_WORDS answer "How did it feel?" at level 3. At levels 1 and 2 the question is "What kept
// it at level N?": two reasons for the exercise (EX_WHY, EX_WHY_DEFAULT for your own exercises), then the shared ones.
// Picked words are saved as the exercise's note, the same as EX_WORDS
const EX_WHY = {
  slides: ['Cracked going up', 'Gaps in the middle'],
  humming: ['Lost the buzz', 'Lips felt tense'],
  lip: ['Lips kept stopping', 'Ran out of air'],
  straw: ['Air kept stopping', 'Too much pressure'],
  falsetto: ['Too breathy', 'Wobbly'],
  upperlower: ['Clunk into chest', 'Lost volume'],
  rung: ['Got heavy', 'Jaw kept closing'],
  hinge: ['Squeak kept dropping', 'Throat felt tight'],
  half: ['Too squeaky', 'Too heavy'],
  vertical: ['Spread on high notes', 'Jaw felt tight'],
  nasal: ['Too nasal', 'Low notes fuzzy'],
  flex: ['Pitch slipped', 'Tripped on the run'],
};
const EX_WHY_DEFAULT = ['Cracked at the top', 'Ran out of air'];
const EX_WHY_ALL = ['Still warming up', 'Voice felt tired', 'Short on time', 'Kept it easy today'];

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

/* ===== Exercise pages (Q32) =====
   What each built-in exercise page shows, beside its write-up (DESC) and the coach video.
   - how: the "How to do it" steps. where: [the glow spot on the head drawing, "Where you feel it"]. Spots: palate, mask,
     nose, lips, head, centre.
   - syl: what you sing (the vowel cue uses these). def: the default pattern (its number in the pattern library, patterns.js).
     vowels: sung on open vowels, so the vowel cue shows (with scale patterns only). fal: the high notes are in falsetto, so
     the range check uses your falsetto top.
   - L: each level: [what you do, the starting notes of each round, a shift in semitones]. The notes are the coach video's,
     copied from tools/coach-video/data/audio_timeline.json (not re-analysed); the shift moves a level whose pattern starts
     above its key (Humming 2 on the third, Half squeaky 1 on the fifth, Upper to lower at the top) onto key notes. No
     notes: no "Hear it" (Vocal slides). Squeaky hinge's notes were never saved, so its route is made up (C3 down to A2,
     then up to G3).
   - facts: each level's three facts, [icon, label, value], from the coach video (Q24). Icons are FACT_ICON in config.js. */
const EX_PAGE = {
  slides: {
    syl: 'hee hoo hoe hah hay',
    where: [
      'palate',
      'On the roof of your mouth, the hard palate, all the way up and down the slide. It’s easiest to find on <i>ee</i>.',
    ],
    how: [
      'Hold one steady note on <i>hee</i>, with no vibrato, and feel it on the roof of your mouth.',
      'Slide from low to high and back on <i>hee</i>, then on <i>hoo</i>, <i>hoe</i>, <i>hah</i> and <i>hay</i>, with the tip of your tongue resting behind your lower front teeth.',
      'Keep it light and quiet, and let the sound get thinner as it rises.',
      'Roll your head gently side to side and wiggle your jaw to stay loose.',
      'On the longest slides, bend forward from the waist as you reach the top, as if you’re falling forward.',
    ],
    L: [
      ['One long note on hee, then short slides.', null],
      ['Medium slides on hee, hoo, hah, hay.', null],
      ['Full range slides.', null],
    ],
    facts: [
      [
        ['arrow', 'Placement', 'Forward'],
        ['wave', 'Vibrato', 'None'],
        ['volume', 'Keep it', 'Light and quiet'],
      ],
      [
        ['head', 'Head', 'Tilt slightly, roll side to side'],
        ['jaw', 'Jaw', 'Wiggle it'],
        ['up', 'Going higher', 'Light and thin'],
      ],
      [
        ['up', 'High notes', 'Bend forward at the waist and bounce'],
        ['repeat', 'Bounce', 'Whole body, 3 times'],
        ['next', 'Each time', 'Release a little higher'],
      ],
    ],
  },
  humming: {
    syl: 'hmmm',
    def: 1,
    where: [
      'mask',
      'A buzz at the front of your face, around your nose and cheekbones (the “mask”), with light vibration on the roof of your mouth.',
    ],
    how: [
      'Close your lips so they only just touch. Don’t press them together.',
      'Hum <i>hmmm</i> quietly, keeping your jaw and tongue loose inside.',
      'Follow the pattern, staying relaxed rather than chasing volume.',
      'If the buzz drops into your throat, hum more quietly until it comes forward again.',
    ],
    L: [
      ['Hum on hmmm.', 'C3 B2 A♯2 A2 G♯2 A2 A♯2 B2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3 A3'],
      ['Hum through a melodic pattern.', 'E3 D♯3 D3 C♯3 C3 E3 F3 F♯3 G3 G♯3 A3 A♯3 B3 C4 C♯4', -4],
      ['Hum a longer, more complex pattern.', 'C3 B2 A♯2 B2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3 A3 A♯3'],
    ],
    facts: [
      [
        ['mouth', 'Lips', 'Loosely touching, not pressed'],
        ['wave', 'Keep it', 'Quiet and relaxed'],
        ['target', 'Feel it', 'Roof of mouth, mask'],
      ],
      [
        ['target', 'Feel the buzz', 'Nose and cheekbones'],
        ['arrow', 'Placement', 'Forward'],
        ['wave', 'Keep it', 'Relaxed'],
      ],
      [
        ['arrow', 'Placement', 'Forward'],
        ['target', 'Feel it', 'Roof of mouth, mask'],
        ['wave', 'Keep it', 'Loose. Don’t chase volume'],
      ],
    ],
  },
  lip: {
    syl: 'brrr',
    def: 1,
    where: [
      'lips',
      'A tickle in your lips and across the front of your face. Your neck and jaw should feel nothing at all.',
    ],
    how: [
      'Blow air through loose, closed lips so they flutter: <i>brrr</i>.',
      'If they won’t flutter, press your fingertips into your cheeks, pushing them in, up and forward.',
      'Keep the air steady but not forced. Too much air tightens your neck.',
      'Sigh into the high notes and let them go, rather than bracing for them.',
    ],
    L: [
      ['Motorboat your lips across your range.', 'C3 B2 A♯2 A2 A♯2 B2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3 A3 A♯3 B3 C4'],
      ['Lip bubble through a scale pattern.', 'C3 B2 A♯2 A2 G♯2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3 A3'],
      ['Full range lip bubbles.', 'C3 B2 A♯2 A2 G♯2 A2 A♯2 B2 C3 C♯3 D3 D♯3 E3 F3 F♯3'],
    ],
    facts: [
      [
        ['up', 'High notes', 'Sigh into them'],
        ['stop', 'Don’t', 'Push'],
        ['hand', 'Lips stop?', 'Press cheeks in and forward'],
      ],
      [
        ['link', 'Keep smooth', 'Chest, mix and head'],
        ['up', 'High notes', 'Don’t tense up for them'],
        ['wave', 'Stay', 'Energised but relaxed'],
      ],
      [
        ['link', 'Pass through', 'Chest, mixed and head voice, smoothly'],
        ['stop', 'Larynx', 'Never grab at it'],
        ['wave', 'Whole range', 'Effortless'],
      ],
    ],
  },
  straw: {
    syl: 'hmmm',
    def: 1,
    where: [
      'lips',
      'Gentle pressure at your lips and a steady push from your belly. Your throat should feel soothed, not worked.',
    ],
    how: [
      'Start with a wide straw in a bottle or cup with a little water.',
      'Breathe in and blow steady bubbles, letting your belly muscles do the work.',
      'Now hum through the straw while the bubbles keep going.',
      'Add the pattern to the hum, keeping the bubbles flowing all the way through.',
      'If it feels like hard work, switch to a wider straw or use less water.',
    ],
    L: [
      ['Blow bubbles through a straw into water.', 'C3 B2 A♯2 A2 G♯2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3 A3'],
      ['Hum a melodic pattern through the straw.', 'C3 B2 A♯2 A2 A♯2 B2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3 A3 A♯3 B3 C4'],
      ['Sing a longer pattern through the straw.', 'C♯3 C3 B2 A♯2 A2 A♯2 B2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3 A3 A♯3'],
    ],
    facts: [
      [
        ['breath', 'Breath', 'Abdominals support it'],
        ['straw', 'Straw', 'Start with a wide one'],
        ['wave', 'Feel', 'Effortless and soothing'],
      ],
      [
        ['breath', 'Air', 'Keep it flowing forward'],
        ['spark', 'Water resistance', 'Builds breath-support muscle memory'],
      ],
      [
        ['straw', 'As you progress', 'Try smaller straws'],
        ['next', 'Afterwards', 'A whole song through the straw'],
      ],
    ],
  },
  falsetto: {
    syl: 'hoo hee hoh',
    def: 2,
    vowels: true,
    fal: true,
    where: ['head', 'High and light in your head, breathy and free. Nothing should grip in your throat.'],
    how: [
      'Tilt your head down slightly and sing <i>hoo</i> lightly in your upper voice.',
      'Keep your teeth about half an inch apart and your jaw loose. Two fingers between your teeth can help.',
      'Let the pattern roll like waves, rolling your head gently side to side.',
      'Sing at whatever volume feels comfortable. Don’t try to control it yet.',
      'Keep the tip of your tongue behind your lower front teeth.',
    ],
    L: [
      ['Sing on hoo, rolling like waves.', 'D♯4 E4 F4 F♯4 G4 F♯4 F4 E4 D♯4 D4 C♯4'],
      ['Sing hee in falsetto through a scale.', 'F4 F♯4 G4 G♯4 A4 A♯4 B4 G4 F♯4 F4 E4 D♯4 D4'],
      ['Alternate hoh and wah/woh in falsetto, wider intervals.', 'D♯4 E4 F4 F♯4 F4 E4 D♯4 D4 C♯4 C4'],
    ],
    facts: [
      [
        ['mouth', 'Teeth', 'Half an inch apart'],
        ['volume', 'Volume', 'Comfortable. Don’t control it yet'],
        ['wave', 'Keep it', 'Loose'],
      ],
      [
        ['jaw', 'Jaw', 'Open'],
        ['wave', 'Stay', 'Relaxed'],
        ['volume', 'Once comfortable', 'Practise soft to loud'],
      ],
      [
        ['target', 'Feel', 'Free and disconnected'],
        ['stop', 'Don’t', 'Force a chest connection'],
      ],
    ],
  },
  upperlower: {
    syl: 'woh woo wee wah',
    def: 6,
    vowels: true,
    fal: true,
    where: [
      'head',
      'It starts light and high in your head and settles lower as you come down, with no bump on the way.',
    ],
    how: [
      'Start high, in your upper voice, on <i>woh</i>.',
      'Come down slowly, as if in slow motion, joining every note to the next.',
      'Keep the volume low and your lips and tongue relaxed.',
      'Listen for the place where your voice changes gear, and keep the tone the same through it.',
      'For a change, do it on a lip trill or through a straw instead of a vowel.',
    ],
    L: [
      ['Descend from upper to lower voice on woh.', 'G♯4 G4 F♯4 F4 E4 D♯4 D4', -7],
      ['Sing we-we-we descending.', 'A♯4 A4 G♯4 G4', -7],
      ['Alternate wah and way descending.', 'A♯4 A4 G♯4 G4', -7],
    ],
    facts: [
      [
        ['speed', 'Speed', 'Slow motion, legato'],
        ['volume', 'Volume', 'Low'],
        ['mouth', 'Keep', 'Lips and tongue relaxed, open'],
      ],
      [
        ['link', 'Transition', 'Smooth, no noticeable break'],
        ['straw', 'Instead of a vowel', 'Lip bubbles or a straw'],
      ],
      [
        ['link', 'Registers', 'Blend seamlessly'],
        ['note', 'Tone', 'No change from one register to the next'],
      ],
    ],
  },
  rung: {
    syl: 'runnng',
    def: 3,
    where: [
      'nose',
      'The <i>ng</i> buzzing up behind your nose and at the front of your face, with your jaw hanging open and loose.',
    ],
    how: [
      'Sing <i>rung</i>, like the rung of a ladder, holding the <i>ng</i>: <i>runnng</i>.',
      'Drop your jaw open vertically as far as is comfortable. A mirror helps.',
      'Keep the tip of your tongue behind your lower front teeth.',
      'Keep it light and fairly quiet, even through the middle of your range.',
    ],
    L: [
      [
        'Sing runnng to blend registers through the mix.',
        'C♯3 C3 B2 A♯2 A2 A♯2 B2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3 A3 A♯3 B3 C4 C♯4 D4',
      ],
      ['Runnng through a longer scale.', 'C3 B2 A♯2 B2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3 A3 A♯3 B3 C4'],
      ['Runnng through a wide-range pattern.', 'C♯3 C3 B2 A♯2 B2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3'],
    ],
    facts: [
      [
        ['jaw', 'Jaw', 'Drop open vertically'],
        ['mouth', 'Tongue', 'Tip behind lower front teeth'],
        ['volume', 'Volume', 'Light, moderately quiet'],
      ],
      [
        ['jaw', 'Jaw', 'Dropping freely throughout'],
        ['spark', 'Builds', 'Open-jaw muscle memory'],
        ['stop', 'Breaks', 'The habit of singing tight'],
      ],
      [
        ['jaw', 'Jaw', 'Open'],
        ['mouth', 'Tongue', 'Relaxed'],
        ['note', 'Free jaw', 'Free tone'],
      ],
    ],
  },
  hinge: {
    syl: 'hmmm',
    def: 4,
    fal: true,
    where: ['centre', 'Right in the centre of your head. Done right, it feels effortless, even on your top notes.'],
    how: [
      'Hum <i>hmmm</i> and make the sound of a squeaky door hinge.',
      'Imagine the sound being made right in the centre of your head, not at the back of your throat.',
      'Aim high even on the low notes, so you’re already in place when the high notes come.',
      'Think thinner and narrower as you go up, and sing quieter rather than pushing.',
      'If it tightens, raise your arms and drop them on the high notes, like a sigh.',
    ],
    L: [
      ['Make a squeaky door hinge sound.', 'C3 B2 A♯2 A2 A♯2 B2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3'],
      ['Squeaky hinge through a scale, with glissandos.', 'C3 B2 A♯2 A2 A♯2 B2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3'],
      ['Extended squeaky hinge pattern.', 'C3 B2 A♯2 A2 A♯2 B2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3'],
    ],
    facts: [
      [
        ['target', 'Focus', 'Centre of your head'],
        ['up', 'Going higher', 'Thinner and lighter'],
        ['wave', 'Effort', 'None at all'],
      ],
      [
        ['wave', 'Stay', 'Loose'],
        ['breath', 'Strain', 'None, when placement and breath are right'],
      ],
      [
        ['up', 'Highest range', 'Let the voice in freely'],
        ['spark', 'For some', 'A way into the whistle register'],
      ],
    ],
  },
  half: {
    syl: 'wah bow way',
    def: 2,
    vowels: true,
    where: ['mask', 'The hinge’s focus at the front of your face, carried into your normal singing voice.'],
    how: [
      'Start with the squeaky hinge sound to find the placement.',
      'Sing <i>wah</i> with your jaw dropped fully open, mixing the squeak with your normal tone.',
      'Keep the hinge’s forward buzz as your normal tone comes in.',
      'If the squeak disappears completely, go back to more squeak and blend in again gradually.',
    ],
    L: [
      [
        'Sing wah, bridging from squeaky to natural.',
        'G3 F♯3 F3 E3 D♯3 E3 F3 F♯3 G3 G♯3 A3 A♯3 B3 C4 C♯4 D4 D♯4 E4 F4',
        -7,
      ],
      ['Sing bow-bow with squeaky hinge glissandos.', 'D♯3 D3 C♯3 C3 B2 D♯3 E3 F3 F♯3 G3 G♯3 A3 A♯3 B3 C4 C♯4 D4 D♯4'],
      ['Sing way, half squeaky, half normal.', 'C♯3 C3 B2 A♯2 A2 G♯2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3'],
    ],
    facts: [
      [
        ['target', 'Placement', 'Squeaky hinge'],
        ['note', 'Tone', 'Normal singing'],
        ['jaw', 'Jaw', 'Fully open'],
      ],
      [
        ['arrow', 'Placement', 'Keep it forward'],
        ['link', 'Bridges', 'Squeaky hinge to your normal voice'],
      ],
      [
        ['wave', 'Feel', 'Flowing 6/8'],
        ['link', 'Carry', 'Hinge placement into real singing'],
      ],
    ],
  },
  vertical: {
    syl: 'mum lum yum',
    def: 2,
    vowels: true,
    where: [
      'palate',
      'Space at the back of your mouth and an open throat. The tone feels warmer, and your neck stays loose.',
    ],
    how: [
      'Shape your mouth into a relaxed, slightly vertical oval, not a wide smile.',
      'Sing <i>mum-mum</i>, keeping that oval on every note.',
      'Check in a mirror that the corners of your mouth aren’t spreading.',
      'If your jaw starts to ache, it’s open too far. Ease off a little.',
    ],
    L: [
      [
        'Sing mum-mum with a slightly vertical mouth.',
        'C3 B2 A♯2 A2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3 A3 A♯3 B3 C4 C♯4 D4',
      ],
      ['Sing lum-lum through a scale.', 'C3 B2 A♯2 A2 G♯2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3 A3'],
      ['Sing yum-yum through a 6/8 pattern.', 'C♯3 C3 B2 A♯2 A2 G♯2 C3 C♯3 D3 D♯3 E3 F3 F♯3'],
    ],
    facts: [
      [
        ['stop', 'Avoid', 'Spreading it wide'],
        ['head', 'Spread mouth', 'Tenses the neck'],
        ['note', 'Vertical feels', 'Warmer and freer'],
      ],
      [
        ['jaw', 'Mouth', 'Vertical throughout'],
        ['stop', 'Breaks', 'Smiling while singing'],
      ],
      [
        ['jaw', 'Mouth', 'Vertical'],
        ['ear', 'Listen for', 'Freedom and warmth in the tone'],
      ],
    ],
  },
  nasal: {
    syl: 'may me nay',
    def: 1,
    vowels: true,
    where: ['nose', 'Forward, in and around your nose and the front of your face, never at the back of your throat.'],
    how: [
      'Sing <i>may-may-may</i>, placing the sound right at the front, almost in your nose.',
      'Keep your head forward and your face relaxed.',
      'Don’t worry that it sounds nasal. That’s what the exercise is for.',
      'On the low notes, keep the sound just as far forward so they stay clear.',
    ],
    L: [
      ['Sing may-may-may.', 'C3 B2 A♯2 A2 A♯2 B2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3 A3'],
      ['Sing me-me-me through a scale.', 'C3 B2 A♯2 A2 G♯2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3 A3'],
      ['Sing nay-yay-yay through a 6/8 pattern.', 'B2 A♯2 A2 G♯2 G2 G♯2 A2 A♯2 B2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3'],
    ],
    facts: [
      [
        ['arrow', 'Placement', 'Forward, nasal'],
        ['stop', 'Not', 'Back of throat'],
        ['ear', 'Sounds nasal?', 'Fine. It’s healthily forward'],
      ],
      [
        ['arrow', 'Keep it', 'Bright and forward'],
        ['spark', 'Low notes', 'Gain clarity and strength'],
      ],
      [
        ['arrow', 'Placement', 'Forward, nasal'],
        ['link', 'Also', 'A route into your mixed middle range'],
      ],
    ],
  },
  flex: {
    syl: 'woo wah he',
    def: 5,
    vowels: true,
    where: ['mask', 'Forward and light at the front of your face, so each note of the run stays distinct.'],
    how: [
      'Learn the pattern slowly on <i>woo</i>, making sure every note is clean and in tune.',
      'Keep each note light and separate, so they don’t blur together.',
      'Speed up only once it’s accurate, and stay at each speed until it is.',
      'Once you know it well, try it without the notes playing.',
    ],
    L: [
      ['Sing woo through a pentatonic scale.', 'C3 B2 A♯2 A2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3 A3 A♯3 B3 C4 C♯4'],
      ['Alternate woo and wah through a longer pattern.', 'C3 B2 A♯2 A2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3'],
      ['Sing he through a fast 12/8 pattern.', 'D3 C♯3 C3 B2 C3 C♯3 D3 D♯3 E3 F3 F♯3 G3 G♯3'],
    ],
    facts: [
      [
        ['speed', 'Speed', 'Slow first, then build'],
        ['spark', 'Builds', 'Runs, riffs and improvisation'],
      ],
      [
        ['speed', 'Order', 'Accuracy, then speed'],
        ['next', 'Once you know it', 'Try it a cappella'],
      ],
      [
        ['spark', 'Builds', 'Agility and riffs'],
        ['speed', 'Once notes are clean', 'Go faster than the recording'],
      ],
    ],
  },
};
