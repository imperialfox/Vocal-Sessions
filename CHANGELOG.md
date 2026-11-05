# Changelog

All notable changes to Vocal Sessions. The app's **Changelog** page (Settings › Changelog) is built from this file, so every entry here appears there.

Version numbers follow **major.minor.patch**:
- **Major:** a redesign
- **Minor:** new features
- **Patch:** small fixes

---

## 3.68 · 5 Nov 2026
*The app's hand-written values take their names (Q54)*
<!-- area: look -->

From the UI consistency audit of 3.62. The motion, corners, shadows and colours still written by hand now use the app's and the kit's named values, and the value check also guards the code, so later features keep one feel. Nothing moves on screen: every part of the main screens sits exactly where it did.

**Motion**
- Rows that move (song rows, take rows, check rows, a swiped row) settle on the gentle spring, as the rest of the app does, instead of their own small bounce.
- The pattern player's dots and vowel change pop on the ripple spring; its steps settle on the segmented control's curve; the speed bubble moves on the gentle spring.
- Pull to refresh spins at the kit's pace (one turn a second) and springs back on the gentle spring.
- The session clock's fades are the kit's glass appearing (250 ms) and leaving (350 ms).
- With Reduce Motion, the session clock, the launch screen, the marks sheet, the vowel change and the session's sections fade on the kit's 100 ms, like everything else since 3.65.
- Recall's hidden words, the pointer hint, the sideways scroll fade and the pattern player's dimming fade on the app's one named fade (200 ms).
- How did it go?'s note box opens on the kit's appearing time. Closing the takes uses the kit's close time.
- The Changelog's cards and timeline settle on the gentle spring. Its "now" dot pulses three times, then rests.
- A missing step in the session nudges for the same length as the other nudge (1.2 s).
- The card zoom's and the launch's own timings keep their lengths, now named in one place.

**Look**
- Corners within 2 pt of a named size take it (cards 20, large blocks 26, inner boxes 14, small tiles and highlights 10). The floating window keeps its 22 pt capsule.
- A row or pattern step lifted by a finger has the kit's lifted shadow; the pointer hint has its floating shadow.
- White on a coloured fill is the app's on-accent colour; the session clock's knob is the kit's knob colour. Video stays black and white.

**Behind the scenes**
- The value check now also checks shadows and colours, and in the code every hand-set time and easing. Each value left has a one-line reason.
- Three unused animations are gone.

Screens: VS-001, VS-002, VS-003, VS-004, VS-005, VS-006, VS-007, VS-008, VS-009, VS-010, VS-011, VS-012, VS-013, VS-014, VS-015, VS-016, VS-017, VS-018, VS-019, VS-020, VS-021, VS-022, VS-023, VS-024, VS-025, VS-026, VS-027, VS-028, VS-029, VS-030, VS-031, VS-032, VS-033, VS-034, VS-035, VS-036, VS-037, VS-038, VS-039, VS-040, VS-041, VS-042, VS-043, VS-044, VS-045, VS-046, VS-047, VS-048, VS-049, VS-050, VS-051, VS-052, VS-053, VS-054, VS-055, VS-056, VS-057, VS-058, VS-059, VS-060, VS-061, VS-062, VS-063, VS-064, VS-065, VS-066, VS-067, VS-068, VS-069, VS-070, VS-071, VS-072, VS-073, VS-074, VS-075, VS-076, VS-077, VS-078, VS-079, VS-080, VS-081, VS-082, VS-083, VS-084, VS-085, VS-086, VS-087, VS-088, VS-089, VS-090, VS-091, VS-092, VS-093, VS-094, VS-095, VS-096, VS-097, VS-098, VS-099, VS-100, VS-101, VS-102, VS-103, VS-104, VS-105, VS-106, VS-107, VS-108

## 3.67 · 5 Nov 2026
*Every button presses the kit's way (Q53)*
<!-- area: look -->

From the UI consistency audit of 3.62. Every button now presses through the parts kit, so buttons feel the same everywhere, and new buttons get the right press without extra work. Nothing looks different at rest.

**Glass buttons**
- Circles and capsules on glass still grow as you press them and light up under the icon, now through the kit's own press.

**Solid buttons**
- Solid buttons (Start session, the calendar, the track's play pad, the coach video's buttons, the ladder's notes and others) shrink as you press them and come back on the same soft spring as the glass ones. Before, they came back with a slower bounce of their own.
- A tile in Song Clock's controls shrinks as one, label and all.

**Buttons on a bar**
- The track's transport, the floating window's buttons and the pattern player's steps only light up, as before.

**Chips**
- The word chips (How did it go?, the session's cues, Add exercise's focus) are the kit's chips: the colour fades in as you pick one, and they no longer shrink. "+ Your own" still shrinks, since it opens something.

**Note steppers**
- Settings › Your voice and Find your bridge show the note, then the kit's − | + stepper beside it, as on iOS. Each half lights up when pressed. The notes move exactly as before.

Rows still highlight when pressed, as since 3.55.

Screens: VS-001, VS-002, VS-003, VS-004, VS-005, VS-006, VS-007, VS-008, VS-009, VS-010, VS-011, VS-012, VS-013, VS-014, VS-015, VS-016, VS-017, VS-018, VS-019, VS-020, VS-021, VS-022, VS-023, VS-024, VS-025, VS-026, VS-027, VS-028, VS-029, VS-030, VS-031, VS-032, VS-033, VS-034, VS-035, VS-036, VS-037, VS-038, VS-039, VS-040, VS-041, VS-042, VS-043, VS-044, VS-045, VS-046, VS-047, VS-048, VS-049, VS-050, VS-051, VS-052, VS-053, VS-054, VS-055, VS-056, VS-057, VS-058, VS-059, VS-060, VS-061, VS-062, VS-063, VS-064, VS-065, VS-066, VS-067, VS-068, VS-069, VS-070, VS-071, VS-072, VS-073, VS-074, VS-075, VS-076, VS-077, VS-078, VS-079, VS-080, VS-081, VS-082, VS-083, VS-084, VS-085, VS-086, VS-087, VS-088, VS-089, VS-090, VS-091, VS-092, VS-093, VS-094, VS-095, VS-096, VS-097, VS-098, VS-099, VS-100, VS-101, VS-102, VS-103, VS-104, VS-105, VS-106, VS-107, VS-108

## 3.66 · 5 Nov 2026
*Sheet music from UG's own PDF download (Q57)*
<!-- area: songs -->

The app now reads the PDF that UG's Download PDF gives you, as well as the Safari print. No printing step, and the words come with it exactly.

**Adding sheet music**
- Choose the PDF from UG's Download PDF the same way as a print: from the song's Sheet music row, or Add sheet music on New song.
- The app works out which kind of PDF it is from its first two pages. Safari prints read exactly as before.
- A PDF it can't read says so: "This doesn't look like sheet music the app can read yet."

**What comes with it**
- The notes, rests and bars, read from the music itself rather than from pictures of it.
- The words, saved on their notes. They'll show on the Sheet music page in a later milestone.
- The title and artist from the top of page 1 fill New song's empty fields.
- The tempo printed at the top is offered. On Sheet music read it starts in the Tempo field, and New song shows "tempo N from the print". Nothing is set until you save.
- A print with no tab reads from its notation alone.

**To check**
- Tempo changes in a print are listed with their bars. Playback uses the first tempo.
- A print with more than one part reads the staff with the words, and says the vocal line was guessed.
- A guitar part (mostly chords) is turned away, as before.
- The same PDF on another song is found by the file itself, or by its title and artist, since these PDFs have no UG link.

**Sheet view**
- For these PDFs, each line is drawn from the PDF itself at your screen's sharpness, so it's crisp on iPhone and iPad.

Screens: VS-051, VS-099, VS-100, VS-101, VS-108

## 3.65 · 5 Nov 2026
*Sheets, pages and Reduce Motion move the kit's way (Q52)*
<!-- area: look -->

From the UI consistency audit of 3.62. Three moves now follow the parts kit, so the app has one feel everywhere and nothing settles after it should have stopped.

**The page behind a sheet**
- When a sheet opens, the page behind shrinks back on the same spring as the sheet, with no bounce at the end.
- When the sheet closes, the page comes back on the sheet's own leaving timing, so the two move as one.

**Opening a page from a list**
- When a page slides in from the right, the page underneath moves a third of the way left and dims a little less, as iOS does.

**Reduce Motion**
- Fades that replace movement are quicker: 100 ms, the kit's length, in place of 200 ms. Sheets fade in and out in 100 ms again (the app was stretching them).
- The green flash when a session step is done keeps a visible length (650 ms), since it's telling you something.

Every page below can sit behind a sheet or slide in; every sheet's Reduce Motion fade changed too.

Screens: VS-001, VS-002, VS-003, VS-004, VS-005, VS-006, VS-007, VS-008, VS-009, VS-010, VS-011, VS-012, VS-013, VS-014, VS-015, VS-016, VS-017, VS-018, VS-019, VS-020, VS-021, VS-022, VS-023, VS-024, VS-025, VS-026, VS-027, VS-028, VS-029, VS-030, VS-097, VS-108

## 3.64 · 5 Nov 2026
*One search bar for Songs and Search (Q51)*
<!-- area: songs -->

From the UI consistency audit of 3.62. Searching inside Songs now uses the same search bar as Search, so there's one search bar that looks and moves one way.

**Searching your songs on iPhone**
- Tap the search field under the Songs title. The search bar opens at the bottom in the tab bar's place, with the same spring as Search, and the keyboard comes up.
- What you type filters the Songs list as before. It stays a Songs search, not a search of the whole app.
- The bar rides just above the keyboard, and the list gets room at the bottom so the last song isn't hidden behind it.
- ✕ closes the search: the whole list and the tab bar come back.

**Gone**
- The old Songs search bar, with its tab bar shrunk to a Songs circle and its Cancel button. ✕ does that job now.

On iPad and Mac the field stays at the top of the Songs list, as before.

Screens: VS-008

## 3.63 · 5 Nov 2026
*Every door moves the same way (Q50)*
<!-- area: fixes -->

From the UI consistency audit of 3.62. One rule for every door: a row slides its page in from the right, a card zooms, and Back takes you back to where you were.

**Doors that now slide in**
- The gear on Today slides Settings in, and Back slides it away. It used to appear and disappear in one frame.
- Today's suggested rotation opens its exercise the same way the Exercises list does.
- Show all sessions and Show all song practice on Progress slide in, as Show all songs does on Today.
- Song practice on a song page slides in, and Back now returns to the song. It used to go to Today.

**Back to the right place**
- Add coach video on Exercises opens Coach video and stays on the Exercises tab, so Back returns to Exercises. It used to jump to Settings.

On iPad and Mac these doors zoom as before.

Screens: VS-001, VS-006, VS-007, VS-009, VS-012, VS-013, VS-014, VS-018, VS-022

## 3.62 · 5 Nov 2026
*Quicker screens and one Cancel (Q49)*
<!-- area: fixes -->

From a check of what made screens slow, and a long run of random taps.

**Quicker**
- Every screen draws with less work: the top bar no longer measures its buttons each time a screen draws, only when they change size. That was a quarter to a third of the work of every draw.
- With the floating window showing, it's placed once just after a screen draws, instead of during it.
- Dates are written out with one reusable format each, instead of a new one every time (Progress and Today draw the most dates). They read exactly as before.
- A screen at the top of its page no longer scrolls back to the top after it redraws (it's already there).
- Together, drawing a screen takes about a third less work.

**One Cancel**
- Already on another song and A different song? (after adding sheet music) showed two Cancel buttons. Now there's one, and it drops the print you just added as the old one did.

**Menus**
- An open menu (a sound, a sort, a song's) closes when you turn the phone, as iOS's do. It stayed where it was placed for the old width, so it could end up off the screen, and the next tap anywhere was lost closing it.

Screens: VS-101, VS-102, VS-003, VS-004, VS-008, VS-009, VS-014, VS-016

## 3.61 · 5 Nov 2026
*Every button has a name (Q48)*
<!-- area: fixes -->

Nothing changes on screen. Behind the scenes, every button and control in the app now has a permanent name, so notes, tests and the Visual App Atlas can point at it (`VS-009 › song-row`) and still find it after a redesign moves it.

**Names**
- About 280 new names, and the existing ones used wherever their button shows: every button, field, link, row and option, named by what it does or holds, never by where it sits or what it says.
- Most are named by their action, so a button gets the same name on every screen it shows on. Back, Close, Done, Cancel and the parts kit's own buttons get one standard name each.
- The Songs list's search button is now `song-search-field` (it was `search-field`, the name kept as an old name), since the app's own search field shows there too.
- Settings › Delete everything: its confirm name pointed at the backup button beside it as well. It now points only at Delete everything.

**Checks**
- A new test fails if any button in the code has no name, if a name is the wrong shape or found by its position, or if one name points at two different buttons on a screen.
- The Atlas taps by name, only while the right screen or sheet is showing, and finds the parts kit's sheets again, which it lost at 3.55.
- `reference/elements.md` lists every name, written from the register.

Screens: none

## 3.60 · 5 Nov 2026
*Sheet music you can hear: dots, the print and a guide (Q47)*
<!-- area: songs -->

A song's sheet music now has its own page. See the notes as dots or the print's own lines, hear the vocal line played back, loop a few bars and slow them down.

**The Sheet music page**
- Tap the Sheet music row on a song's page to open it. The circle at the top has the score's settings (octave, tempo, key, what to check, replace the print).
- **Dots** shows each note as a dot at its pitch, a couple of bars a line on an iPhone and four on an iPad. Bars and + or − change how many bars a line. Bars with something to check are shaded. Notes the reader muted are hollow, and unsure ones are dashed.
- **Sheet** shows the lines of your own print, with the bar being sung outlined as it plays. The print is cut into lines again each time you open it, so nothing extra is stored. With no print on this device the dots still play.

**The guide**
- Play sounds the vocal line in the pattern player's sound (the recorded piano unless you've chosen another). Muted notes stay silent.
- Tap a bar to play from there. Tap a dot to hear its note, or to jump there while it plays.
- The note button gives you your starting note: the next note from where the playhead is.
- Speed − and + step from 0.5× to 2×, the same steps as the pattern player. It's kept on this device.
- Loop repeats the bars of the line you're on. Change lets you tap the first and last bar of the loop. Tap Loop again to turn it off; the bars are kept for next time. The track player's own loop isn't changed.
- It stops when you leave the page, lock the phone or play something else, and carries on from the same place.

**Also**
- New prints remember which line each bar is on, so the sheet view finds its lines straight away.

Screens: VS-108, VS-009, VS-099

## 3.59.1 · 5 Nov 2026
*A fix for 3.59's top bar (Q45)*
<!-- area: fixes -->

- A title in the top bar with no buttons beside it, such as the recording label, gets the bar's whole width again, so it isn't cut short on a small iPhone.

Screens: VS-009

## 3.59 · 5 Nov 2026
*The top bar, Today's title and search from the parts kit (Q45)*
<!-- area: look -->

The top bar, Today's title and search now follow the parts kit, so the bar's buttons are never blurred, Today's header has Apple's spacing, and on the iPhone search lives at the bottom.

**Top bar**
- The soft fade at the top of a scrolled page is now part of the top bar, behind its buttons, so the gear and the other buttons stay sharp, with a sheet open or not.
- It's the page colour fading out, with no blur. It fades in once you scroll a little, as before, and shrinks with the page under a sheet.
- The buttons stay exactly where they were.

**Today**
- The date sits on its own line above "Today", in regular weight, and "Today" sits a little lower than the other tabs' titles, as in Apple's apps.
- The chevron is grey and closer to the word. The date, the word and the chevron still open the calendar.

**Search on the iPhone**
- The search circle opens the search field at the bottom, in the tab bar's place, and the tab bar shrinks away. ✕ closes it and takes you back to the tab you were on.
- The field rides just above the keyboard, so you can see what you type. The results get room at the bottom, so the last one scrolls clear of the field.
- The field and Cancel at the top of Search are gone: the results and recent searches fill the page. iPad and Mac keep their field at the top.

**Also**
- Parts kit 1.2.0.

Screens: VS-001, VS-002, VS-003, VS-004, VS-005, VS-006, VS-007, VS-008, VS-009, VS-010, VS-011, VS-012, VS-013, VS-014, VS-015, VS-016, VS-017, VS-018, VS-019, VS-020, VS-021, VS-022, VS-023, VS-024, VS-025, VS-026, VS-027, VS-028, VS-029, VS-030, VS-097

## 3.58 · 4 Nov 2026
*Smoother page changes, with no jump at the end (Q44)*
<!-- area: look -->

Opening a page from a card, a row or Back now starts moving sooner and lands without a jump. Every spring and timing is as it was.

**No more drop at the end**
- On an iPhone, every zoom, push and Back ended with the whole page dropping 6 pt. The picture of the page that moves during the change now sits exactly where the real page is, so nothing moves when it's swapped in. The same goes for swipe back and Reduce Motion's fade.
- The exercise page's title row sits level with every other page's title, 4 pt higher than before.

**A quicker start**
- Opening an exercise starts moving about one frame sooner (about 30 ms after the tap in the test browser, down from about 45 ms).
- Tapping a tab, or a button in a sheet, no longer copies the screen first, since nothing zooms from there.

**Resting**
- Today's background shapes hold still while a sheet is open, a page change plays, the page scrolls or they're out of view, then carry on from where they were. At rest on Today they drift as before.
- The glow on the exercise page pulses three times, then rests. It stops at once when you start the pattern player.
- The page behind a sheet no longer animates its (invisible) corners as it shrinks.

Screens: VS-001, VS-002, VS-003, VS-004, VS-006, VS-007, VS-008, VS-009, VS-010, VS-011, VS-012, VS-013, VS-014, VS-018, VS-019, VS-020, VS-021, VS-022, VS-023, VS-024, VS-025, VS-026, VS-027, VS-028, VS-029, VS-030, VS-097

## 3.57 · 4 Nov 2026
*A recorded piano, a smoother Soft tone and no more pops (Q43)*
<!-- area: practice -->

The pattern player's notes are more pleasant to sing against, and they never click, pop or distort.

**Piano**
- Piano-ish is now Piano: a real recorded piano, warm and in stereo, instead of notes made in code. It's the default sound. If you chose Soft tone or Electric piano before, you keep it.
- Each note is held for as long as it's sung, then fades gently. The click at the end of every Piano-ish note is gone.
- The recordings download the first time the player makes a sound (about 1.4 MB, once) and are kept for offline. Until they've arrived, the piano plays Soft tone.

**Soft tone**
- Rounder and warmer: a gentler start and end, and a slight vibrato on notes longer than half a second. The held note underneath uses it too.

**Chords**
- The player's output has room for the chord before each round, so it no longer distorts. Piano and Soft tone have a small room echo.

Everywhere the player plays a note gets the new sounds: the exercise pages, the Patterns page, the song ladder's notes, Practise in a key and the Sound choice in Settings › Pattern player.

The piano notes are from Liam Lee's piano samples, under the MIT licence (credited in the README).

Screens: VS-014, VS-018, VS-024

## 3.56 · 4 Nov 2026
*Sheet music from your Ultimate Guitar prints (Q42)*
<!-- area: songs -->

A song can now take your own Ultimate Guitar print and keep its vocal line as sheet music: every note, bar and rest, read on this device. Print the Vocals part from UG in Safari, in the notation plus tab view, and save it as a PDF.

**Adding a print**
- On a song's page, Practice has a new Sheet music row: tap Add sheet music and choose the PDF. New song's Add media takes a print too, and fills in the title and artist from it.
- The print is read in the background, line by line, with Cancel, so the app carries on while it reads. Nothing is saved until you tap Save sheet music.
- Before saving you see the key signature, the bars, the range and where the song sits against your voice, the octave (Lower, As written or Higher, set from Your voice) and the tempo (type the number from the top of the print, or move it by 1).
- After saving, the key sheet opens on the print's key. Nothing changes until you tap Use.

**What it reads**
- Notes and their lengths, dots, ties across bar lines, triplets, rests, rests of several bars (checked against the bar numbers on the print), pickup bars and bars that change the time.
- Bend labels, grace notes and slides don't confuse it. Harmony keeps the top note.
- Notes it can't trust are muted and listed: a tab number it couldn't read, a note far outside the song's range, a sudden one-note jump. Where the tab and the notes disagree, it plays the tab and marks it.
- Tap the Sheet music row to see what to check: bars that don't add up, repeats (the order may be wrong), bar numbers that don't match the print.

**It checks what comes in**
- A file that isn't a PDF, a locked or damaged one, a print from somewhere else, the wrong view, a guitar part, or a print it can barely read is turned away with a message saying what to do. A very big or long PDF asks first.
- A print with a different title asks whether it's this song, a new song, or neither. A print already on another song offers to open that song. A second print asks before it replaces the first, and the old one is kept for 30 days.
- Add sheet music waits while you're recording.

**Kept safe**
- Sheet music is in your backups, with its own check code, so older versions still open new backups. The PDF itself stays on this device, like tracks.
- Settings › Storage shows the sheet music, with Remove prints, keep scores to free space, and Sheets with no song after a reset.
- The reader works offline after the first print.

Screens: VS-009, VS-020, VS-051, VS-098, VS-099, VS-100, VS-101, VS-102, VS-103, VS-104, VS-105, VS-106, VS-107

## 3.55 · 4 Nov 2026
*Menus, sheets and controls from the parts kit (Q41)*
<!-- area: look -->

Menus, sheets, alerts, toasts, switches, segmented controls, the speed slider and the tab bar now come from the parts kit, so they behave like the iPhone's own and every later change to their look is one setting.

**Pop-ups**
- "Are you sure?" questions (deleting a take, a session or a song, removing the track, resetting, discarding) are now iPhone alerts in the middle of the screen: Cancel and a red action.
- A take's menu, a comment's menu and a marker's menu are now action sheets that rise from the bottom.
- Toasts drop in from the top and stay 3 seconds.
- Every menu shares one style, with rounder corners. Holding a song row or a lyric line lifts it after a moment and opens its menu at 0.7 seconds. The page dims a little behind it, with no blur.
- Sheets have the screen's own rounder corners. Flick one down to close it, or pull it down from its content when that's at the top.
- New song opens halfway up on Add media and grows to full height once you pick a file or choose Manually. The Marks key for a song opens full screen.

**Controls and bars**
- Switches slide, and you can drag or flick them.
- Segmented controls (Practise, Recall and Perform, ranges, levels and the rest) have equal segments. The knob springs across, swells into glass while you press it, and can be dragged.
- The pattern player's speed is a slider now, under the − and + bubble. Holding the speed pill and sliding sideways still changes it in one go.
- The tab bar never folds away when you scroll, and the search circle sits a little closer to it.
- When a top bar button changes its icon, the old icon blurs out and the new one blurs in.
- Search fields stretch a little when you drag them.
- Rows highlight while you press them instead of shrinking.

<!-- area: fixes -->
**Behind the scenes**
- The parts kit (version 1.1.0) is part of the app, unchanged, and it runs the app's motion: its springs, slow motion and Reduce Motion. Settings › Accessibility works as before.
- Every design decision is one line in the kit's settings for this app, and a test checks the app differs from the kit only where a decision says so.
- A list of everything the kit replaced is kept for the reference sheets that come next.

Screens: VS-001, VS-004, VS-006, VS-007, VS-008, VS-009, VS-010, VS-013, VS-014, VS-015, VS-016, VS-017, VS-018, VS-019, VS-021, VS-023, VS-024, VS-025, VS-026, VS-027, VS-031, VS-032, VS-033, VS-034, VS-035, VS-036, VS-037, VS-038, VS-039, VS-040, VS-041, VS-042, VS-043, VS-044, VS-045, VS-046, VS-047, VS-048, VS-049, VS-050, VS-051, VS-052, VS-053, VS-054, VS-055, VS-056, VS-057, VS-058, VS-059, VS-060, VS-061, VS-062, VS-063, VS-064, VS-065, VS-066, VS-067, VS-068, VS-069, VS-070, VS-071, VS-072, VS-073, VS-074, VS-075, VS-076, VS-077, VS-078, VS-079, VS-080, VS-081, VS-082, VS-083, VS-084, VS-085, VS-086, VS-087, VS-088, VS-089, VS-090, VS-091, VS-092, VS-096, VS-097, VS-098

## 3.54 · 4 Nov 2026
*Song key and scale lanes: sing a song in its key (Q39)*
<!-- area: practice -->

The app now finds a song's key from your takes, shows the key's notes behind your pitch lines, and suggests patterns from the pattern player in that key that reach the note you're working on.

**The song key**
- Under the ladder's lines, the app listens to every take of the song for its key. When two keys fit about as well, it asks ("Which key is this song in?" with both and Other…). Otherwise it suggests one ("This sounds like F major") with Use. You only choose once for each song.
- Not enough singing yet? It says so, and you can choose the key yourself.
- Choose or change it on a new sheet: Major or Minor, then 12 notes spelled for the key (D♭, E♭, A♭, B♭ in major; C♯ and G♯ in minor). Open it from Lines or the new **Key** row on the song's page.
- The key is saved with the song and goes in your backups.

**Scale lanes**
- Once a song has a key, its notes show as faint lanes behind your pitch lines, on Lines and live while you record. The home note is blue, and every note is spelled for the key (B♭4 in F major, not A♯4).
- A **Scale lanes** chip on Lines switches them off on this phone. They show where the notes are; nothing is marked right or wrong.

**Practise in the key**
- The note to work on: where the words part from your trill, or else the line's top note ("sits on A4, the 3rd of F major").
- Up to three patterns from the library that play in the song's key and reach that note, riffs first. Each shows its range and what it trains, with Play.
- Tap one to open the pattern player on that note, staying on the key. Your exercises' own choices aren't changed.
- The ladder's note buttons now match the song's key too.

Screens: VS-004, VS-009, VS-097, VS-098

## 3.53 · 4 Nov 2026
*Bridge-aware patterns: find your bridge and get guided through it (Q38)*
<!-- area: practice -->

The pattern player now knows where your voice flips, and guides you through it, thinner and quieter, instead of letting you push.

**Find your bridge**
- A new sheet listens to one slow slide on "ee", draws it as you sing and marks where your voice jumps.
- It suggests your bridge from the first jump: two notes below to one above. Change it with From and To, then **Use this bridge**. **Try again** listens again.
- No jump, or you'd rather not sing it? Set it by feel. It also shows the highest note you reached.
- Open it from the exercise page's bridge line or from **Settings › Your voice › Your bridge**. Your bridge is saved with Your voice and goes in your backups.

**On the exercise page**
- The bridge is shaded on the drawing, and its notes are ringed in orange.
- A line under the drawing says which rounds cross it ("Bridge E4–G4 · rounds 11–14 cross it"), with Change.
- Those reference notes play softer, at about half volume.
- While one plays, a cue says **Thinner · quieter** on a hum, or the narrower vowel and quieter on a vowel (ah → uh, ee → ih). Switch it off in Settings › Pattern player › Bridge cue.

**Listen while I sing**
- Off to start. With it on, the microphone shows your voice as a dot and a short trail on the drawing while the pattern plays. Put headphones in, so it only hears you. Nothing is recorded.
- When you hold a round's top note cleanly, **Last time** moves up quietly ("Last time: F4 · today"). Without listening it never changes.
- **Stop one past last time** (Settings › Your voice, next to Stop at my top note) ends the exercise one round past it. With both on, the earlier stop wins.
- No scores and no right or wrong anywhere.

Screens: VS-014, VS-023, VS-024, VS-096

## 3.52 · 4 Nov 2026
*The song ladder: sing a section four ways (Q37)*
<!-- area: practice -->

Application can now sing a section as a ladder: a lip trill, a hum, the vowels, then the words, with your pitch lines showing where the words drift from the trill. It's a way to carry what the exercises teach straight into the song.

**The ladder**
- The song card has a **Straight / Ladder** switch. Each song remembers which one you chose.
- Four rungs, one take each: **Lip trill**, **Hum**, **Vowels only** and **Words**. Each has its own short instruction and its own view of the words: faded for the trill and hum, the vowel letters picked out for Vowels only, the words for Words. **Skip this rung** moves on.
- While a rung records, its pitch line draws live under the meter.
- The rungs you've sung fold into one row ("2 of 4 sung · Trill · Hum"). Tap it to see each one with a small line and play. Only the rung you're on stays open; the rest are one "Up next" line.
- Sing over the track and the headphones question work as before.

**Lines and notes**
- From two rungs, **Lines** shows their pitch lines on top of each other, lined up at the first note, each switched on or off with its chip.
- It names where the words part from the trill: by line when the song is timed, otherwise by time. **Hear both** plays the trill there, then the words. If they stay together, it says so.
- Once all four are sung, **Notes of the line** gives a button for each note you held in the trill. Tap one to hear it. With **Repeat** on, it keeps playing until you tap it again.
- No scores, percentages or red and green anywhere: lines, not grades.

**Your takes**
- Ladder takes are ordinary takes of the section, named "Ladder · Lip trill" and so on, with Star, Compare, notes and backups as before. **Done** folds the card to "Song · Section · Ladder · N takes".
- Pitch lines are worked out on your phone when they're needed and never saved or backed up.

<!-- area: fixes -->
**Behind the scenes**
- A shared pitch listener reads a voice the same way everywhere, from a take or live from the microphone, ready for bridge-aware patterns and key finding next. It uses pitchy (MIT), kept as a fixed copy in the app so it works offline.
- The pattern player can play a single note, for the note buttons.

Screens: VS-004

## 3.51 · 3 Nov 2026
*One set of corners, presses and motion (Q40)*
<!-- area: look -->

The app now has one named set of corner sizes, button presses and motion timings, and a check that stops new one-off values creeping in, so it keeps feeling like one app as it grows.

**What you'll notice**
- The pattern player's speed bar and its pull-up menu (sound, voice type) use the same glass as the pills beside them, a little lighter than before.
- Solid buttons all press the same amount now: the Song Clock pill and the tiles in Song controls, a song row's play button, the track player's pads, the pattern player's play, repeat and pills, and the session's nudge. Some pressed a little deeper or shallower before.

<!-- area: fixes -->
**Behind the scenes**
- Every corner, press, curve and fade timing that already matched the new set now uses its name. Nothing else changes how it looks.
- The values that don't match yet stay as they are, on a list in the tests that can only get shorter. They move onto the set as their parts move onto the parts kit.
- A new test fails if a new one-off corner, press, curve or timing is added anywhere, in the stylesheet or the code.

Screens: VS-002, VS-008, VS-009, VS-010, VS-014, VS-016, VS-050

## 3.50 · 3 Nov 2026
*Every screen has its own ID (Q36)*
<!-- area: look -->

Every screen, page and sheet now has a permanent ID, like VS-001 for Today, so a note or a request can point at exactly the right screen in a few characters. The ID stays the same when a screen is renamed, moved or redesigned.

**Screen IDs**
- 95 screens, pages, sheets and overlays are numbered VS-001 to VS-095, by area: Today, the session, Progress, Songs, Exercises, Search, Settings, then sheets and the parts drawn over everything (the session clock, the floating window, the launch screen and the peek card).
- The main buttons, rows and cards on each screen have names too, such as VS-001 › start-session-button, so a note still points at the right button after a redesign moves it.
- Five main journeys have their own IDs: F-01 Focused session, F-02 Song practice, F-03 Add a song, F-04 Time a song and F-05 Back up and restore.
- New screens get the next number. A number is never reused, and a screen that's removed keeps its number, marked retired.

**Show screen IDs**
- A new switch in Settings › Appearance shows the current screen's ID in a small grey label in the top corner, just below the bar. With a sheet open it shows both, such as VS-009 · VS-050.
- It's off unless you switch it on, on this device only, and never in backups. Taps go straight through the label.
- With it on, each version in the Changelog shows which screens it changed.

<!-- area: fixes -->
**Behind the scenes**
- The list of everything the app saves now says which version each item arrived in and whether backups carry it, and lists the settings it was missing.
- The tests check every screen the app can show has an ID, every named part is still there, and the list of saved data matches the code.

Screens: VS-025, VS-027

## 3.49 · 2 Nov 2026
*Glass that looks and presses like iOS 27 (Q33)*
<!-- area: look -->

The app's glass now uses numbers measured against a real iPhone on iOS 27.

**Pressing**
- Glass buttons grow when you press them, as on the iPhone, instead of shrinking: 17 pt bigger along their longest side (a round button by about 39%, the search circle by about 27%), with a soft white light under the icon. They settle back with one small dip.
- The session clock pill and the clock's play pill react to a press now too.
- Buttons that sit on a glass bar (the tabs, the track player's play, back and loop, the floating window's play) no longer shrink. They light up and the bar stays still.
- Start session, list rows and other solid buttons press as before.
- With Reduce Motion on, buttons don't grow; the light still fades in and out.

**The glass**
- Light mode: a lighter blur that lets more of what's behind show through, a slightly brighter tint, a barely-there shadow and a fine edge lit from the top.
- Dark mode: a thin white layer with gentler colour, lit from the bottom edge, and no shadow.
- Sheets stay near-solid for reading. They take only the new edge and shadow, and dark mode's gentler colour.

**Reduce transparency**
- A new switch in Settings › Accessibility makes the glass more solid, so what's on it is easier to read. It's for this iPhone only and never in backups. Safari can't see the iPhone's own setting, so the switch is how to turn it on.

## 3.48 · 2 Nov 2026
*Every exercise page explains the exercise and plays it (Q32)*
<!-- area: practice -->

Each exercise's page now teaches it and gets you singing straight away, with no video or other app. The app plays the pattern itself, with piano-like notes it makes (no recordings), from a library of 60 practice patterns.

**The page**
- A drawing of the pattern with a red playhead, three facts for the level with the coach video's icons, a fix tip, **How to do it**, **Where you feel it** (a glow on a head drawing), the level dots on the level you last logged, a shorter Why it helps with More, then the coach video and In a song as before.
- Vocal slides has a picture of short, medium and full-range slides instead, since the coach video has no notes for it.

**Hear it**
- Play starts on the coach's notes for the level and moves up a key each round. Before each round the new key's chord plays (minor for minor patterns), a low note holds underneath, and after the last round it goes back to the starting key. Stop fades out gently.
- The dock has the pattern, its speed, the sound (Soft tone, Piano-ish or Electric piano), the starting note, **Stay on this key** and Play.
- The speed pill opens a slider like Control Centre's, from 0.5× to 2×. **Speed up each round** goes one step faster every round, up to 2×. Each pattern keeps its own speed.
- It plays with the silent switch on and keeps the screen awake while it plays.

**Patterns**
- Tap the pattern to open the Patterns page: Warm-ups, Agility, Riffs and runs, Flips (full voice into falsetto) and ★ Favourites, started with riffs in Bruno Mars's style. A window at the top plays each pattern like the exercise page does.
- Tap a pattern to choose it and hear it. Press and hold to see what it trains. Each exercise remembers its pattern and starting note, with Back to default.

**Your voice**
- The card says when a pattern goes above or below your range, and **Settings › Your voice** sets it (tenor to start). Falsetto exercises and Flips check against your falsetto top. **Stop at my top note** ends before going above it.
- **Settings › Pattern player** has the sound, the held note, the chord before each round, the ending, the vowel cue and dots or music notes on the drawing.
- Your choices go into backups. Nothing else about your data changes.

## 3.47 · 2 Nov 2026
*No more rating the song at the end of a session (Q29)*
<!-- area: practice -->

Application ends at your take. The app no longer asks you to score the song.

- "Rate the song" (Pitch · Tone · Ease) is gone from Application, and from a session's edit sheet.
- A session's sheet no longer shows scores from before. They're still kept in your data and backups, so nothing is lost.
- Song practice's "How did it go?" words and Star on takes are unchanged.

## 3.46 · 2 Nov 2026
*Copy for Toggl is gone (Q28)*
<!-- area: practice -->

The app stands on its own now, so the leftover Copy for Toggl has been taken out.

- A session's sheet and a song practice's sheet no longer have the Copy for Toggl button, and song practice's "Toggl tag #song-practice" line is gone. Everything else on them is unchanged.
- Nothing about Toggl was ever saved, so your sessions and backups are exactly as they were.

## 3.45 · 2 Nov 2026
*Every tab label in full with the iPhone on its side (Q27)*
<!-- area: look -->

With the iPhone on its side, the tab bar shows every tab's name in full beside the search circle. "Exercises" used to read "Exerc".

- When the bar is short of room, the space either side of each tab tightens so every icon and name fits. The names stay the same size.
- With room to spare, the tabs look exactly as they did. Upright, iPad and Mac are unchanged.

## 3.44 · 2 Nov 2026
*The floating window: picture in picture, tuck it away, one look (Q26)*
<!-- area: practice -->

The coach video's window works like Apple's picture in picture, any floating window can be tucked away at the side, and every kind now looks and behaves the same.

**Coach video, picture in picture**
- The window is just the video now; the bar under it is gone.
- Tap it to show its controls over the dimmed video: ✕, open the player, −10 · play · +10, and L1 L2 L3 (as in the player: a tap jumps to that level's start, and the lit level starts again). They fade after about 3 seconds; tap again to hide them sooner.
- Three sizes: small, medium and the full width. Pinch, or double-tap for the next. The last size is kept on this device.

**Tuck it away**
- Drag or throw any floating window off the left or right edge. It slides away and leaves a small tab with an arrow.
- Sound and timers carry on; a blue dot on the tab shows something is playing.
- Tap the tab, or pull it out, to bring the window back.

**One look**
- The top line says what it is (the section, song or step) and the time is below it. "Playing ·" and "Paused ·" are gone: the play/pause button shows that.
- The session's step name is in the normal text colour, after a dot in the step's colour, so it's easy to read.
- The red window while you record over the track is a deeper red, easier to read, and says "Track under your take".
- One thin progress line along the bottom edge for every kind (the song track has one now), and the same rounded shape for every capsule.
- In dark mode the session ring's empty track shows more clearly.
- A long name loses its end, never its start.

**Behaviour**
- In a bottom corner, every page leaves room at its end so the last line scrolls clear of the window.
- The window presses down slightly when tapped, and lifts while you drag it.
- Swapping from one kind to another cross-fades while it changes size in the same corner. With Reduce Motion, it fades in and out.
- Every ✕ and play button is easier to hit (44 pt), and the coach video's ✕ no longer jumps to the wrong corner.
- VoiceOver reads a steady name (e.g. "Focused session, Rotation"), and the time only when you ask, not every second.

## 3.43 · 2 Nov 2026
*Coach video: every tap lands on the exact start of a level (Q25)*
<!-- area: practice -->

The coach video's chapters are now the 36 level starts measured frame by frame, so a tap never lands in the end of the exercise before.

**Jumps**
- Every exercise has L1 · L2 · L3 in the player. A tap jumps to that level's first frame; tapping the lit level starts it again.
- At a level's end it plays on into the next one. With Loop on, it repeats that level, right to the next level's start.

**Level 1 first**
- Opening an exercise always starts at the top of Level 1: a session step, Play with coach on an exercise page (it now reads "From Level 1") and the exercise list in the player.
- Pausing and coming back carries on where you were. Only opening an exercise again goes back to Level 1.
- The video's level switch never changes the level you log.

**Lengths**
- Each exercise's length in the coach video is now its measured length. Your past session totals don't change; only the step split of sessions filled in at the end shifts slightly, mostly for Vocal flexibility.

## 3.42 · 1 Nov 2026
*Session clock: a ring you can read at a glance (Q22)*
<!-- area: practice -->

The timer pill opens a ring in the one-page session's colours, with small fixes that take the stress out of timing.

**The ring**
- One ring, three slices: Foundation, Rotation and Application, each as long as your usual time for that step (from your last 10 sessions; set times until there are 3).
- The step you're on fills its slice as time passes, with a small tick and "Usual move-on ~N min" where you usually move on.
- No pressure: a logged step fills its whole slice even if it was short, and going past your usual time changes nothing. Steps you haven't reached show your usual time ("~14 min").
- Tap the big number to show the step's time first, with the total below. It's remembered on this phone.
- Song practice has one slice all the way round.

**Pause and finish**
- Paused, the ring slowly breathes, the numbers go grey and the main button says Resume. With Reduce Motion it just dims.
- The clock's main button does what the pinned button does. Finish from the clock and the ring closes into the Session saved line ("41 min · Sunday · weekly goal reached"), with Done below.

<!-- area: look -->
**Open and close**
- The clock grows out of the timer pill and shrinks back into it.
- Swipe it sideways anywhere, either way, to close it: it follows your finger and closes past about a fifth of its width or on a flick, otherwise it springs back. ✕ still closes it, and the time slider keeps its own gesture.
- The floating window shows the same ring, small, beside "Rotation · 4:16", with its pause button.
- Steady digits: every clock number keeps its width as it ticks.

**Less to worry about**
- The screen stays on while a session runs ("Screen stays on" at the start and on Resume), and can sleep when paused or finished. If the phone won't allow it, nothing else changes.
- After more than 10 minutes away, it asks "You were away N min": Take it out, or Keep it, I was singing. It never decides for you.
- Undo for about 5 seconds after each Log.
- Tap a finished step's time to fix it: hold and slide, see what was logged, then Save time. Progress's split uses the fixed time.
- Close the app mid-session and it carries on when you come back ("Session picked up").

## 3.41 · 1 Nov 2026
*Session saved: a calm finish that becomes Today (Q21)*
<!-- area: practice -->

Finishing a session lands on a calm "Session saved" screen that belongs to Today, then becomes Today with one tap.

**Session saved**
- This week's arch, with only today's minutes drawing in on top of the week so far. The numbers are your real ones, and nothing counts up.
- "41 min · Sunday", plus "weekly goal reached" once you've reached it.
- The week's circles, with today's turning green, and "N-week streak continues" when you have a streak.
- Done sits just below, in the middle of the screen.

<!-- area: look -->
**Done becomes Today**
- The arch, the circles and the streak line move into their places on Today, Done becomes Start session, and the rest of Today rises in around them.
- With Reduce Motion it fades instead, and so does a screen it can't line up exactly (iPad, landscape, or no streak yet).

<!-- area: practice -->
**Kept as it was**
- Song practice keeps its own finish: How did it go?, then its summary.
- Copy for Toggl is on the session's own sheet, from the calendar or All sessions.

## 3.40 · 1 Nov 2026
*Application: carry on, sing, compare and keep your best take (Q20)*
<!-- area: practice -->

Application, the session's last step, is quicker: pick up where you left off, sing, compare, keep the best take and move on.

**Carry on**
- A card picks up the song and section you last sang. Change section shows Whole song and each section of the song; a song with no sections is always Whole song.
- Other songs sit underneath, sorted by Recently practised or A–Z.
- "Practised, not recorded" logs a song you practised without a take, for days in the car.
- With nothing sung yet, the pinned button reads Skip and finish.

**Singing**
- Sing over the track (remembered on this phone): with the song's track on the phone, Sing plays it from just before the section and records over it. It asks first, with headphones as the default and the speaker only after you say so, as agreed for recording over the track. <!-- area: recordings -->
- While it records, the card becomes the recording (the section, the time, its words and Stop), the rest of the page steps back and keeps still, and the floating window turns into a red window for the track. <!-- area: recordings -->

**Takes**
- Each take shows its waveform, its length and a star to mark your keeper. <!-- area: recordings -->
- Compare switches between this take and the one before in one tap, from the same moment, one at a time. <!-- area: recordings -->
- ↻ Again sings the same section again. Done flashes green and the song folds to one line; tap it to change anything.
- Song practice has the same take rows, with Compare and ↻ Again. A take's Save or share and Delete are on its notes sheet (tap its name), and swiping left still deletes. <!-- area: recordings -->
- Every take is kept, as before.

**Finishing**
- Finishing a session no longer asks How did it go? It's saved straight away (the long-session check stays). Past answers still show, and you can still add them from a session's edit sheet. Song practice still asks.

## 3.39 · 1 Nov 2026
*A session on one page, with rings for each exercise (Q19)*
<!-- area: practice -->

Foundation, Rotation and Application now follow each other on one page, so a session feels like one piece from start to finish.

**One page**
- A finished step folds to a one-line summary and the next slides up into its place, with the step after it showing faded underneath. Tap a summary to change anything, then Done.
- You can't jump ahead: the next step is only a preview, and pulling past the bottom springs back, like pull to refresh, saying what's still needed.
- One button stays pinned at the bottom with the same labels as before (Log foundation, Log 2 exercises, Finish session) and a hint above it. Each step's end is recorded exactly as before, so Progress's time split is unchanged.
- It says Foundation everywhere in the session.
- Back now leaves the session (it keeps running) from any step.

**Levels**
- Each exercise is a row with a ring. Tap the row to go up a level: Foundation goes 1, 2, 3, then Skip; Rotation goes 1, 2, 3, then off.
- Level 3 sweeps the card blue, then a green flash, and asks How did it feel?
- Levels 1 and 2 ask What kept it at level 1 (or 2)? after a moment, with reasons for that exercise, Still warming up, Voice felt tired, Short on time, Kept it easy today and + Your own.
- Words you pick are saved as that exercise's note, as before, and the row folds to one line so the next exercise gets a nudge.

**Rotation**
- The suggested exercise sits on top, then More exercises, sorted by Longest ago, Most recent or A–Z, each saying when you last did it.
- With nothing picked, the button says Skip rotation, and Just Foundation today? Finish here ends the session there.

**Coach video**
- In Foundation and Rotation the coach video sits in the floating window, ready at the step's exercise. Application has a Coach ▸ pill instead. Drag either to any corner; ✕ tucks the video into the pill.
- Application itself is unchanged for now.

**Behind the scenes**
- A session saved part-way through by an earlier version opens where it was left.

## 3.38 · 1 Nov 2026
*Undo that stays with its own song, and a tidy-up behind the scenes (Q17)*
<!-- area: fixes -->

Nothing else looks different: this clears out code and styles nothing used any more.

**Fixes**
- Fixed: Undo on a timing change could put back a different song's timing if that song had been changed since. Each song now has its own Undo, so a toast's Undo only ever changes the song it was shown for.
- Fixed: if a track's waveform had gone missing and you opened another song's track while it was being read again, the first track could take over the player. The track you went to now stays, and the first one's waveform is still saved for next time.

**Behind the scenes**
- Removed leftovers from Sync by sections and play-along without a track (both retired in 3.28): code that no longer did anything, and out-of-date notes.
- Timing no longer saves an unused setting (`real`). Timing saved by older versions still opens as before.
- Removed ten styles nothing on screen used any more.

## 3.37.1 · 1 Nov 2026
*The microphone's sound engine rests properly after a refused recording (Q16)*
<!-- area: fixes -->

- Fixed: if the microphone was refused just as you tapped Record, the app's sound engine could stay switched on with nothing to listen to. It now rests once it has woken, as it does after every take.

## 3.37 · 1 Nov 2026
*Record over your song's track, and Loop that plays each level to its end (Q16)*
<!-- area: recordings -->

**Recording over the track**
- The song's track can now keep playing while you record a take. Tap Record while it plays and the app asks first: **Record with headphones** or **Record through the speaker**. Through the speaker, the track may be heard in the take.
- Said headphones, the next takes go straight in while the track keeps playing. The app asks again once the track pauses, when headphones come out or other audio devices change, and after you leave the app. The speaker asks every time.
- Stopping the take leaves the track playing, and the lock screen still controls it. Anything else that plays (a take, the coach video, play-along) still stops everything, the track and the recording included, and the take is saved.
- With the track paused, Record starts straight away, as before.

<!-- area: practice -->
**Coach video**
- Loop now plays each level right to its end before going back to its start. It used to jump back up to a quarter of a second early, cutting off the end of the level.

<!-- area: fixes -->
**Notes for whoever works on the app**
- One shared audio service (`AUDIO`, js/audio.js) for everything that listens to the microphone: the mono mix, the level meter and, later, the voice analysers. It never plays the track, takes or the coach video.
- One frame clock (`AUDIO.frame`) for anything drawn from the microphone. The level meter now uses it and no longer looks up its bars every 90 ms.
- The coach video's Loop uses the same precise timer as the track's loop.

## 3.36 · 1 Nov 2026
*Room for register details in your marks and timing (Q15)*
<!-- area: songs -->

Nothing looks different: marks and timing look and behave the same. This gets the app ready for register work, so a future version can add details without older versions losing them.

**Marks**
- A mark this version doesn't know yet (a new kind of mark, a new option such as a new register, or a new layer) is kept when a backup from a newer version is restored, instead of being thrown away. It stays hidden: it isn't drawn, counted, listed in Key for this song or shown while playing along, and adding a mark never replaces it. It still follows its words when you edit the lyrics.
- Extra details on a mark now stay with it when you change it on the same words or move it from the top of its section to a word.

**Timing, markers and the loop**
- Extra details on a song's timing, its sections' timing and each timed line are kept when you re-time a line, nudge, move a section, trim or clear the length, instead of being dropped at the next change.
- Markers and the loop keep theirs too, including when you set a new loop start or end.

**Backups**
- A backup made by the next version restores here with nothing lost, and a backup made afterwards carries it all back out unchanged. A new check proves it with a made-up backup from the next version.

<!-- area: fixes -->
**Notes for whoever works on the app**
- New optional fields go in one place on each record, `ext` (for example a mark's `ext`, or a timed line's third item). See Rules that keep old data working in MAINTAINING.md.
- Data step 4 turned out to have nothing to do (the marks are already moved across as data loads); it's now noted in the code and left as a safety net.

## 3.35.1 · 1 Nov 2026
*Hold-menu checks wait like a finger would (Q18)*
<!-- area: fixes -->

Nothing in the app changes.

- Fixed: the checks that hold a take, a comment or a marker and then tap the menu sometimes tapped too soon. The app rightly ignores a tap in the first moment after letting go of a hold, so on GitHub's quicker computer that tap was sometimes ignored and the check went red. They now wait as long as a finger would.

## 3.35 · 1 Nov 2026
*Steadier checks behind the scenes (Q18)*
<!-- area: fixes -->

Nothing in the app changes. This makes the automatic checks give the same answer on GitHub as on the computer that builds the app, so a new version no longer shows a red cross for no real reason.

**Checks that now wait properly**
- Quick flicks (swiping back, and throwing the floating window into a corner) are now sent at a fixed speed, so a busy computer can't make them look like slow drags.
- The calendar checks now work on the first day of a month, and just after midnight on it.
- A few checks now wait for the thing they're checking (a saved take, the Rename field) instead of waiting a fixed time.

**Notes for whoever works on the app**
- How to run the checks the same way GitHub does, and a list of known check problems and why they happen.

## 3.34 · 31 Oct 2026
*Smoother play-along and waveform on older iPhones (Q14)*
<!-- area: songs -->

Nothing looks different: the app just does much less work on every frame.

**Play-along**
- The song's timing is worked out once, not 60 times a second, and the lyric lines are found once when the view is built.
- When the song moves to the next line, only the lines that change are touched, and the screen is measured before anything is written, so there's no stutter on the line change.
- Blur ahead now goes only on the lines you can see (and a screen's worth either side), so a long song no longer blurs dozens of hidden lines.
- Tapping a line, or fixing one with a hold (punch-in), no longer rebuilds the whole lyric view or redraws the page behind it: the line changes in place.

**The track player**
- The waveform, loop, markers and section starts are drawn once and slid along as the track plays; only the red playhead is drawn each frame. They're drawn again when you zoom, change the loop or markers, switch light and dark, or rotate.
- The line lane under the waveform works the same way.
- In Song view, only the row the playhead is in is redrawn while playing.
- Buttons and labels are only updated when they actually change.

## 3.33 · 31 Oct 2026
*Today's glow reaches the top of the screen (Q23)*
<!-- area: look -->

**Behind the status bar**
- The app now runs right up behind the clock and battery, so Today's colours reach the top of the screen instead of stopping at a grey strip.
- The top buttons, toasts, sheets, pages and pop-ups all stay clear of the clock.

## 3.32 · 31 Oct 2026
*Every mark explained right where you use it (Q04)*
<!-- area: songs -->

**Hold a mark for a quick reminder**
- On the Marks side, hold any mark button for about half a second: a small card pops up with the mark's name, what it's for, its options and an example drawn just as it looks on a song.
- Letting go never adds the mark. A plain tap still adds it as before.
- Close, a tap anywhere else or a scroll puts the card away. **Learn more** opens the mark's page.

**Key for this song**
- The Key button (pinned beside the artist) and a new **?** in the marks sheet now show only the marks this song uses, layer by layer, with the options you picked and how many there are, then your Notes.
- Tap any of them to learn it. A song with no marks yet says so, with a link to the Marks guide.

**The Marks guide**
- A page for every mark (all 21, plus Note): what it is, how to sing it, when to mark it, an example, and the mark it's easy to mix up with (tap it to go there).
- **How to mark a song** walks through the four passes, one layer at a time, and the habits that make marks work, including the faint suggested breaths your timing leaves.
- Open it from Settings (a new row after Coach video), the **Marks guide** row in the song's ⋯ controls, or the link in "Select words to mark". The full list of marks that Key used to show is now the guide's first page.
- Back always takes you to where you were. On the Marks side your selected words and the marks sheet are still there.

## 3.31 · 30 Oct 2026
*Keyboard shortcuts that only do what you meant (Q13)*
<!-- area: fixes -->

For an iPad keyboard or a Mac.

**Once per press**
- Holding Space on the track player plays (or pauses) once, instead of flickering between the two.
- Holding a shortcut like Cmd + E counts once too. Holding an arrow still keeps moving.

**Never while you're busy**
- No shortcuts while a sheet, the Song length picker or a recording is open.
- Cmd + 1 to 4 follow the same rules as tapping the tab bar: no switching tabs during a recording, on a session step, or while you're typing. Switching from a song you're editing finishes the edit, the same as tapping the tab.
- A key that a button or picker has already used is left to it.

**The Song length picker**
- ↑ and ↓ in the picker only move its wheels. They no longer also open the next song, so Set always gives the length to the song you opened it on.

**Typing stays typing**
- Shortcuts use Cmd only on an iPad, iPhone or Mac. Ctrl + E, N and F are left alone for editing text.
- Pressing Enter to pick a word while typing in Japanese, Chinese or another script with a word picker no longer also confirms the field (search, the song title, a mark's text, comments).

## 3.30 · 30 Oct 2026
*Timing you place stays where you put it (Q12)*
<!-- area: songs -->

**Moving a section**
- Moving a timed section no longer squashes the sections around it. Its lines turn into estimates (dashed, and listed on Check timing) and its start stays where it was. No other section's times change.
- Place its lines on the track again and they're solid once more.

**Your placed lines are left alone**
- Lines you've placed are never moved by the app to make room. If two of them overlap (for example after moving a section), Check timing marks them **Overlaps** so you can re-time them.
- Adding a line between two lines that touch squeezes the new one in between, without moving either of them.
- Punch-in, Start here / End here and dragging on the line lane are only limited by the lines you've placed, never by estimates, and estimates are never saved as if you'd placed them.
- A section's start stops counting as set once its first line loses its time (for example when you change that line's words).

**Section starts from markers**
- Making a marker a section start always puts the start on the marker. Every section before it is squeezed in before it, and if there's no room at all, those lines are left as estimates.
- On a timed song, moving the first set start earlier squeezes the lines before it in from 0:00, never before it.

**Replacing a track with a shorter one**
- If any markers or lines are past the new end, the app asks first: **Trim to the new track** or **Keep them** (handy if you swap back to the longer mix). Nothing is deleted while it asks.
- Trim removes markers past the end, ends a marker at the end, and lines past it lose their time with a to-do marker.
- Both have **Undo**, which puts every marker, loop and line time back.

## 3.29 · 30 Oct 2026
*Nothing you save can quietly go missing (Q11)*
<!-- area: backup -->

**Damaged saved data is rescued**
- If the app ever can't read your saved data (for example a save cut short), it copies it exactly as it was before anything is saved over it, and tells you once.
- The copy is kept on this phone under **Settings › Backup › Rescued data**: **Save the rescued copy** puts it in Files, and **Delete the rescued copy** asks first.
- Each song is checked on its own. If one song can't be read, only that song is left out, and your data as it was is copied the same way.
- If there's nowhere to put the copy, your saved data is left untouched and nothing is saved over it that time.

<!-- area: recordings -->
**Takes are never dropped**
- If a take can't be saved (usually a full phone), it stays in the app with its audio and a **Retry** button.
- Missed the message? The app tries again when you come back to it and after your next take saves, and tells you if it still can't.
- The song practice it belongs to carries on, and the take joins it once it's saved.
- A backup or restore now stops with a message if your recordings can't be read, rather than leaving them out.

<!-- area: fixes -->
**Safer saving behind the scenes**
- Recordings, song tracks, the coach video and takes' waveforms all save through one shared, sturdier piece of code. A save that's stopped by the phone now always ends with a message instead of hanging.
- Your practice in progress warns you if it can't be saved, as everything else does.
- The 30-day copy kept before a data upgrade has moved out of the space your saved data uses, so a full phone is less likely. It's counted in Settings › Storage.
- If something goes wrong while the app starts, the launch screen still goes and says so, instead of staying on the icon.

## 3.28.1 · 30 Oct 2026
*Play-along's buttons fit the smallest phones (Q05)*

<!-- area: fixes -->
**Play-along**
- On the narrowest iPhones, the play-along transport leaves a little less room around the time, so −0.2, +0.2, the track's sound and Flag stay full-size buttons.

## 3.28 · 30 Oct 2026
*Time songs line by line from the song's own track (Q05)*

<!-- area: songs -->
**Timing runs off the song's track**
- Song Clock now always uses the song's track on this phone. No more playing the song on another device and tapping along in the app.
- Without the track, **Timing** reads **Add a track to time this song** and opens Files, the same as the song's Track row.
- On a song that isn't timed yet, Timing opens the track player to place its sections and lines.
- **Sync by sections** (the big tap pad) and **Sync again** are gone, and so is playing along without a track. Section starts come from the waveform, as since 3.24.
- Timing saved on older songs is kept exactly as it was. Check timing still shows it, and says play-along needs the song's track.

**Lines on the waveform**
- In the track player's **Phrase** and **Line** views, a lane under the waveform has a block for each lyric line. Blocks are dashed while they're an estimate and solid once you've placed them.
- Drag a block's edge to move it. Where two lines touch, one handle moves the end of one and the start of the next together.
- Or tap a block to select it, then **Start here** or **End here** at the playhead.
- With **Snapping** on (Song controls), edges snap to the playhead, section starts and the other lines' edges. The Snapping tile finally does something.
- Every change has **Undo**, and it all goes into the song's one timing. A song stops being an estimate once every line has been placed.

**Fixing lines while you sing**
- **Punch-in:** while playing along, hold the lyrics for half a second as a line starts. That line starts where your finger went down, and letting go sets its end. A toast says **Re-timed**, with Undo. A quick tap still jumps to a line.
- **Flag** at the end of the play-along transport drops a marker on the track where you are, with Undo. Paused, the same button is **Retime**, which opens the track player on the line you're on.

**Doors into the track player**
- **Hold a lyric line** for half a second in Practise or Perform: it lifts, the rest dims, and a menu offers **Retime line**, **Play from here** and **Annotate** (the Marks side with the whole line selected, on the layer you used last). In Recall a hold still peeks, and the hold never also focuses the section.
- On **Check timing**, every line, the **Section starts** row and **Time each line** open the player in Line view on that line, sliding in like Check timing does. Back returns to Check timing.
- Changing a line of lyrics still clears only that line's time. Placing it again clears its to-do marker.

**Suggested breaths**
- A gap you leave after a placed line becomes a suggested breath. It's saved with the timing and included in backups.
- It shows only in **Phrasing** on the Marks side, as a faint dashed **’ +** at the end of the line. Tap it to make it a real breath mark, with Undo. Once the line has a breath mark, the suggestion goes.

## 3.27 · 29 Oct 2026
*Marks in four layers, one stage of learning at a time (Q03)*

<!-- area: songs -->
**Four layers**
- Marks now come in four layers, one for each stage of learning a song: **1 Notes** (pitch, slide, hold, ornament, rhythm), **2 Phrasing** (phrase, chain, peak, breath, shape), **3 Words** (vowel, carry, onset, stress, say) and **4 Delivery** (register, colour, vibrato, mic, intention). A **Note** bookmark works on every layer.
- Only one layer shows at a time. Pick it with the chips 1–4 above the lyrics, in Practise and while marking; the app remembers it on this device. Switching keeps the line you're looking at where it is.
- Labels sit above their words like chords over lyrics, with " · " between two on one word. Phrases are brackets over their words, stress is a thick line under them, and a hold is a line running past its word. Breaths, chains, carries and Notes sit just after their words. An intention is one line under its section's label.

**Marking**
- The edit switch is **Marks · Lyrics**, in the top bar and in the pencil's row on the song page.
- Tap a word to select it, then tap another on the same line to select the words between. Tap inside to start again from that word, or the only selected word to clear it.
- A sheet rises with the layer's five marks and Note. Marks with options show them underneath, one tap deep; Sing as, Say, Intention and Notes take a few words. **On these words** lists what's already there, each with ✕, and adding or removing a mark offers **Undo**.
- Marks on a linked chorus show on every repeat, and selecting words lights them up in every copy.
- A mark whose word changed is flagged on every layer, with **Keep** in the sheet; one whose word was removed waits at the top of its section, as before.
- Your marks from before moved into their layers: breaths into Phrasing, runs and higher or lower into Notes, sing-as into Words, and notes became Notes. Nothing was lost.

**While singing**
- **Recall** shows phrase brackets, chains, breaths and Notes over the hidden words; they never move as you hide more.
- **Marks while playing** has a third setting, **Active layer**: the chosen layer's marks show on the line you're singing and the next one, with breaths on every line. Lines never change height as the song moves on. **Perform** follows the same setting.
- **Marking while listening:** tap the pencil while playing along and the Marks side opens with the song still going. The time is a pill at the top (tap to pause), and the line being sung is softly lit without the page moving.

## 3.26 · 28 Oct 2026
*Apple's text sizes, colours and layers throughout (Q10)*

<!-- area: look -->
**Text and colour**
- Every piece of text now uses one of Apple's text styles, from Large Title down to Caption, so the same kind of text is always the same size. In-between sizes are gone, so some text moves by a point or two: notes and banners go from 14 to 15, the big lines in Song Clock settle at 28, and the numbers on Progress at 22.
- The app's colours are now Apple's own, in light and dark: red for recording and songs, orange for stars, pause and the loop, purple for markers, and indigo, teal and orange for the Progress bar (its last colour is the loop's orange).
- Stars and pause were using the dark-mode orange in light mode; they're the proper light orange now.
- Warnings are a soft orange tint with dark text.

**Markers**
- A marker's number sits on a light purple wash in dark text, with a purple dot, so it's easy to read at a glance. The marker playing has a red dot.
- The numbered tabs on the waveform use a deeper purple for the same reason.
- On an iPad or a Mac, the marker tiles follow how wide their side of the screen is: three across with room, one across when it's narrow.
- The row of marker chips under the waveform fades softly at whichever edge has more chips behind it.

**Layers**
- A box inside a card is a slightly darker grey with no outline, as in Apple's apps (the song's title fields while you edit them in Song Clock, the takes inside a section).
- An empty value in a list shows a faint dash instead of a gap.
- Selected text in the lyrics editor and text boxes is a light wash of the app's blue.

<!-- area: recordings -->
**All takes**
- All takes is grouped by section: a row for each section with how many takes it has. Tap one to fold its takes open; the blue chevron turns down. More than one can be open.
- It opens with the section you came from already open, and a take opened from Search shows inside its section. A song whose takes are all from one section keeps the plain list.

<!-- area: look -->
**On a Mac**
- Resting the pointer on an icon-only button shows what it does after a moment: the track player's buttons, and the round buttons in the top bar (Back, ⋯ and Search). Never on touch.

## 3.25 · 26 Oct 2026
*Bigger rehearsal controls on the track player (Q09)*

<!-- area: songs -->
**Markers**
- Three big pads replace the round buttons: **Replay**, **Play/Pause** (the widest) and **Next**, with two pills above them: **Backing Sound** and **Loop**.
- **Backing Sound** off keeps the track playing silently: the playhead, the loop and Next carry on, so you can sing the marker on your own. It's on whenever you open the player, and only Markers is silenced.
- **Loop** turns the loop on or off. With no loop yet, it loops the marker you're in.
- **Replay** starts the marker you're in again. **Next** goes to the next marker in time order and scrolls its tile into view.
- Tiles are taller (108 pt), and each tile's loop button is bigger and sits at the bottom right, where your thumb lands.

**Looping**
- The jump back at the end of a loop happens right at the end, so the pause there is shorter, at every speed. The pitch stays the same at 0.75× and 0.5×.

<!-- area: look -->
**The player**
- The left and right jog wheels grow while you hold them, staying where they are on the edge (they no longer slide in).
- In Song, the rows sit in a card, with the **Lyrics** pill at its top right.
- The lyric card above the waveform moves the new line into place with a soft pulse when it changes (a fade with Reduce Motion).

## 3.24 · 26 Oct 2026
*Waveform sections on the track player (Q02)*

<!-- area: songs -->
**Section starts on the waveform**
- Hold a marker and choose **Make this a section start…**, then pick the section. The marker becomes that section's start in Song Clock, so there's one timing for the song, and the toast's **Undo** puts back both the timing and the marker.
- Starts stay in time order: a section that would start before an earlier one (or after a later one) is greyed in the picker, with the reason.
- On a song that's already timed, that section moves to the marker and the other starts stay where they are. On one that isn't, its lines are spread from there, as Sync by sections does.
- Section starts show on the waveform as blue lines with their names. Scrubbing the waveform takes the place of the Timeline that was planned for Song Clock.

**Four views**
- **Phrase** (6 s) and **Line** (16 s): a taller strip, with a card above it showing the line before, the line at the playhead (with its section) and the next.
- **Song**: the whole song in rows of 24 s. The last row ends at the track's end (a 3:14 track ends with a 3:12–3:14 row). The lyrics sit under each row; tap one to go to it, or hide them with the **Lyrics** pill.
- **Markers**: a big tile for each marker. Tap one to play it and loop it to its own end, or to the next marker (the last one runs to the track's end). Markers under half a second apart don't loop. Each tile has its own loop button, the one you picked is outlined and the one playing is tinted, and the last tile adds a marker at the playhead. Its transport is Replay, Play/Pause and Next.
- The view you used before this update is reset to Line, once.

**Play along with the track**
- When the song's track is on this device, play-along plays it and the lyrics follow the track's time. It's on to start with, and the new button beside −0.2 and +0.2 mutes it. Without the track, play-along works as before, lyrics only.
- Pausing play-along pauses the track, and pausing the track (from the lock screen, say) pauses play-along.

<!-- area: look -->
**The player**
- The jog wheel can sit on the left, on the right, or as a full-width roller under the strip (the player's ⋯ menu). The edge wheels slide further in under your finger.
- The playhead is red, in light and dark.
- With the screen locked, the loop is kept as well as iOS allows, and waking puts a playhead that drifted out of the loop back at its start.

## 3.23 · 26 Oct 2026
*Bars, pages and Today that feel like iOS 27 (Q08)*
<!-- area: look -->

**The bars where Apple's are**
- On iPhone, the tab bar now sits low, 21 points from the bottom edge in the home indicator's area, with 21-point margins either side, as in Music and Notes. The four tabs share the bar's width, and the search circle beside it is as tall as the bar.
- The buttons at the top (the gear, Back and the step pill) sit 6 points higher, where Apple's do.
- Everything that rests on the tab bar moved down with it: the floating window, a session's button, Song Clock's and the track player's controls, and Recall's capsule. iPad, Mac and landscape are unchanged.

**A soft edge when you scroll**
- Scrolling a page no longer turns the top bar into a rounded card. Instead, a full-width blur starts behind the status bar and fades away at its lower edge, with no line, and the page scrolls softly under it. The buttons stay glass and the title sits in the middle.

**Today's gradient**
- A soft wash of coral, blue and orange now sits behind Today's date and title, fading out about a third of the way down. Three blobs of colour drift very slowly over a faint grain, and it scrolls away with the page. The cards and Start session are exactly as they were.
- With Reduce motion on it holds still.
- **Settings › Appearance** is new, with one switch: **Gradient background**, on unless you switch it off. It's for this device only and isn't in backups.

**Pages that push in, as on iPhone**
- Songs, Today's pinned songs, Show all songs, Search's songs, lyrics and exercises, the Exercises list, Sync by sections and Check timing from a song, and Settings' rows and Changelog now push their page in from the right. The page underneath slides a little to the left and dims, on the same spring as the zooms.
- Back and swipe back reverse it: the page follows your finger and the one underneath slides back. Let go past about a fifth of the screen, or with a flick, and it finishes at your finger's speed; otherwise it settles back. You can turn it round halfway, either way.
- Everything else that opened with a zoom still does: Song practice, the track, the coach video, Start session, the weekly goal, Show all sessions and the suggested rotation.
- With Reduce motion on, pushes become a short fade.

**The tab bar's collapse**
- Scrolling down a long page now shrinks the tab bar to a small pill at the left, holding the tab you're on, with the search circle staying at the right, the same height. Scrolling up, or tapping the pill, brings it back.
- It moves smoothly now: the bar fades and slides away towards the left while the pill grows in, with no wobble, no jumping icon and nothing else on screen moving.
- It waits for about 30 points of steady scrolling down and comes back after about 20 points up, so a small nudge or the bounce at either end of a page doesn't make it flicker. Scrolls the app makes itself (like going back to where a list was) don't count.
- It only happens on pages with real room to scroll, never in the first 120 points, and never on Search, while you're typing or with a sheet open. Every new page starts with the full bar.

## 3.22 · 26 Oct 2026
*Search, from every tab (Q01)*

<!-- area: look -->
**The search circle**
- A search circle now sits beside the tab bar on every tab, like the iPhone's own apps. It stays beside the tab bar when that shrinks as you scroll, and it's tinted while Search is open.
- On iPad it's a circle at the end of the tab capsule at the top; on a Mac-sized window it's a Search row at the top of the sidebar. Cmd/Ctrl+F opens it from a keyboard.
- The floating window keeps clear of it, in every corner.

<!-- area: songs -->
**The search page**
- Before you type: your recent searches and your pinned songs. Recent searches stay on this device and aren't in backups.
- As you type, results appear straight away, grouped: Songs, Lyrics, Exercises, Sessions and Takes. Each group shows its top three, with "Show all" to see the rest in place.
- Lyrics show the matching line, highlighted, with the song and section under it. Exercises match their names and their write-ups, and say which part matched. Sessions match their notes and feedback words. Takes match the names you've given them and your comments.
- The matching is as forgiving as the Songs list's: capitals, punctuation, accents, word order and a slipped letter in longer words don't matter.
- A song or an exercise zooms open from its result, and Back shrinks it into the same result, with your search still there. A lyric opens its song in Practise, scrolled to that section with it focused. A session opens its details.
- A take opens its song with the takes sheet on All takes and that take expanded. A comment does the same, with the playhead at its time and the comment showing.
- Cancel clears the search and puts the keyboard away.

**The Songs list**
- Songs keeps its own search for filtering the list, now a field under the title on iPhone (the circle beside the tab bar is Search).

## 3.21.1 · 24 Oct 2026
*Exercise pages that read like Apple Health*
<!-- area: look -->

- Exercise pages now have bold, sentence-case titles in place of the small grey labels: "About vocal slides", "Why it helps", "In a song" and "Last done". Other pages keep their labels.
- The About and Why it helps text for all 12 exercises is rewritten in a calm, factual tone: what the exercise is first, then how it's done, then what it does for your voice, ending with one practical tip on what to adjust. Every detail from before is kept.
- Half squeaky now says "squeaky hinge", matching the exercise's name.

---

## 3.21 · 24 Oct 2026
*Settings, like the iPhone's: a row for each, a page for each*
<!-- area: look -->

**The Settings list**
- Settings is now a list of rows, each with its own icon, like the iPhone's Settings app: Backup, Storage, Recall, Coach video, Accessibility, Changelog and View on GitHub. Tap a row to open its page; it zooms open from the row, and Back (or a swipe from anywhere) shrinks it back.
- Each row shows where things stand on the right: when you last backed up (red after two weeks, or if you never have), the space used, the peek length, whether the coach video is added, and the Reduce motion setting.
- The two resets stay at the bottom of the list, in red, and still ask first.
- At the very bottom: the app's icon, name, version and release date. Tap it for the Changelog.

**Backup and Storage pages**
- Both open with a card explaining what the page is for, with a big icon.
- Backup has Export, Import, Check a backup and Undo last restore, when you last backed up, and Backup history, Where backups go and Save a read-me file. Undoing a restore brings you back here.
- Storage shows one bar split by what's using the space (recordings, song tracks, the coach video, and sessions and songs), then the same rows as before: Recordings, Review old takes, Song tracks, Coach video and Storage protection.

**Accessibility**
- New page. **Reduce motion:** Match iPhone (the default), On or Off. On swaps zooms and slides for short fades even if your iPhone's Reduce Motion is off; Off keeps the motion even if it's on.
- **Slow motion** plays every animation four times slower, to check how it feels.
- Both are kept on this device only and are never in backups.

## 3.20.1 · 23 Oct 2026
*Song Clock: pausing keeps your line in place*
<!-- area: fixes -->

- Fixed: pausing play-along near the end of a short song could move the line you were on down the screen. The song page now has room below the lyrics while paused, so the line stays where your eye was.

## 3.20 · 23 Oct 2026
*Songs, takes and markers: one place for every take, and a ✕ that always closes*
<!-- area: songs -->

**Adding a song**
- The Songs list has one +. It opens with a switch: **Add media** (the default) or **Manually**. This replaces New song and New song from track.
- Add media: choose the song's audio from Files. Once it's read, the form opens with its length filled in and linked to the track. The title and artist start empty, since a file's details often aren't right; leave the title blank and the file's name is used. Lyrics are optional.
- Manually is the same form as before, now with a Length.
- Save opens the song. Nothing is kept if you cancel or choose a different file.

**The song list**
- Every song has a play button that plays its track, here and in Today's pinned songs. Without a track on this phone it's greyed, and says "Upload a track to play".
- Each song shows when you last practised it and how many takes it has, recent first, with nothing to grade.
- Today's Song practice card now opens the Songs tab. Recording a take on any song's page starts (or carries on) song practice for that song, timed from the first take. Your past song practice is all still there.

**Takes**
- **Takes** beside the song's title opens every take. From a section, a switch moves between that section's takes and All takes.
- Tap a take to play it and open it out: a waveform you drag to scrub, back and forward 5 seconds, and its name, which you can tap to change.
- Comments at a moment in the take: the time is set the moment you start typing (tap it to nudge it). While the take plays, each comment pops up as it's reached, and dots under the waveform jump to them.
- Swipe right to star a take, left to delete it (it always asks), or hold it for Star, Rename and Delete.
- Every take is kept now, not just the last three. Settings › Storage shows how many there are and has Review old takes, to clear unstarred takes with no comments by hand.
- Names and comments are always in backups, even with Exclude recordings, and the backup sheet shows the size with and without recordings.

**The track player**
- Markers: Marker drops one at the playhead, playing or not. They show in purple on the waveform and as numbered chips under it: tap one to jump there. Give one an end with End here, and it gets its own loop button. Drag the orange handles to fine-tune it.
- Hold a chip to rename, move, change its end or delete it, or clear them all.
- Tapping in Section and Song views moves the playhead and keeps the view. The level buttons (or a pinch) change the zoom.

**Song length**
- With a track, the song's length follows it, shown with a link. Changing it asks "Unlink from track?" first. A length of your own shows a broken link and the track's length beside it; tap it to relink.

**Playing**
- One sound at a time: a take, a recording, the coach video, a song's track or play-along. Starting one stops the others, and the lock screen follows the one playing.
- The floating window's ✕ is on every sound, playing or paused. It stops it and closes the window for good, until you play it again. Nothing else pops up in its place.
- Fixed: takes and tracks play again from the start after they finish.
- Fixed: takes play in both ears with earphones. New takes are recorded as one channel, and older takes with the voice on one side play from a copy made for both ears. Your recordings themselves are never changed.

## 3.19.1 · 23 Oct 2026
*Track player: MP3s can be picked in Files*
<!-- area: fixes -->

- Fixed: on iPhone, audio files were greyed out in Files when adding a track. The picker now names MP3, M4A, WAV, AAC and AIFF files one by one, so they can be chosen.

## 3.19 · 23 Oct 2026
*Track player: loop a phrase of the real song, slowly*
<!-- area: songs -->

**A song's track**
- New: add a song's audio from Files, from the Track row in the song's Practice group, the Add track tile in Song controls, or New song from track on the Songs list (it makes the song, titled from the file name, and you can paste the lyrics later).
- MP3, M4A and WAV all work. Songs from Apple Music can't be added, and a file that won't open says so.
- The track stays on this phone and isn't included in backups, so they stay small. A restored song keeps its loop and timings and says "Track not on this device", with Add track to put the same file back.
- The waveform is read once, when you add the track, so the player opens straight away after that.

**The player**
- Four zoom levels: Phrase and Line are a strip that moves under a fixed playhead; Section and Song show the whole song in rows. Tap a level or pinch, and tap a row to zoom into Line view there.
- The jog wheel on the right: drag slowly for precision, quickly to skim.
- Set start and Set end at the playhead, or drag the orange handles. Audio outside the loop is dimmed, and a double-tap outside it clears it.
- Speed 0.5×, 0.75× or 1×, with the pitch kept, so it stays in key when slowed.
- The loop is saved with the song. The zoom level and speed are remembered on this phone.
- Leave while it plays and a small window says "Playing · song title". Only one thing plays at a time: the track, a take, the coach video or play-along.

## 3.18 · 22 Oct 2026
*Song Clock: sync a song and sing along*
<!-- area: songs -->

**Timing a song**
- New: Sync. Play the song on another device or in your music app, and tap the big pad as each section starts. Your first tap starts the clock, and every tap allows a little for your finger.
- While you sync you see the clock, which section you're on, what you just marked and what's next. Undo takes back the last tap, and tapping a section you've done redoes from there.
- Pause works on one phone: scrub the song back a little, then tap as the section starts, and the clock carries on from there.
- After the last tap, each section's lines are spread evenly by their syllables, so the whole song moves straight away.

**Playing along**
- Turn on Timing and tap the first line as it's sung. The lyrics turn big, the line you're singing sits about a third of the way down, and its words fill as they're sung.
- Lines you've sung dim, and the ones coming up blur a little more the further away they are (Blur ahead).
- Tap any line to jump there. −0.2 and +0.2 move all the lyrics earlier or later, saved, with Undo.
- Pause shows the normal lyrics page with the line you were on highlighted, right where your eye was. Tapping a section still focuses it.
- The screen stays awake while you're timing (Stay awake).
- Leave the song while it plays and a small window says "Playing along" with the time and section. Its button pauses, and tapping it takes you back in step.

**Marks while playing**
- Breaths only (the default): your own breath marks show, and lines with a long gap after them and no breath mark of yours get a small breath dot. Everything else (sing-as labels, runs, higher and lower, notes) is hidden while you sing.
- Off hides breath marks and dots too.

**Check timing**
- A list of every section and line with a bar for how long it lasts. Very short and very long lines are flagged, and so are lines to look at again.
- It shows the song length and how many section starts are set, and Sync again from the start.

**The song's header**
- The artist line now shows the song's length ("Artist · 3:58"). Tap it to change it on clock-style wheels.
- Beside it are up to three pinned buttons (Timing and Key to start with) and ⋯, which opens Song controls: Timing, Check timing, Key, Marks while playing, Blur ahead, Snapping, Stay awake, Sync again and Lyrics. Blue means on. Edit chooses which ones are pinned.
- The pencil now edits the title, artist and length in place, with Edit lyrics, Marks and Done.
- Changing a line of lyrics only clears that line's timing, and marks it to look at again.
- Timing is saved with the song and included in backups. Settings like Blur ahead stay on this device.

## 3.17 · 22 Oct 2026
*Tab order, new icons and tidier lyrics*
<!-- area: look -->

**Tabs**
- The tabs are now in the order Today, Progress, Songs, Exercises: in the tab bar, the iPad's top capsule and the Mac's sidebar. Cmd/Ctrl + 3 opens Songs and Cmd/Ctrl + 4 opens Exercises.
- New icons: Progress is a ring about three quarters full, like Today's goal arch, and Exercises is a small deck of cards.

**Today's title**
- "Today" now sits at exactly the same height as the titles on Progress, Songs and Exercises, so the header no longer jumps when you switch tabs. On iPad and Mac the Songs title lines up too.
- The date sits just above the title, tight to its letters, and still opens the practice calendar.
- The chevron beside "Today" is centred on its letters.

**Sing-as labels**
- A word with a sing-as label now makes room for it, like chords over lyrics: the label sits above its word and the gap after the word grows, so labels never overlap each other, the lyrics or the line above.
- Only lines with a label get taller. The note marker always sits beside its word.
- Recall still hides the labels in place, and Perform still leaves them out.

**Fixes**
- Closing the coach video's small window with ✕ now always hides it. On iPhone it could stay on screen on every page, showing a black box, the exercise name and Play. Only playing the video again brings it back.

## 3.16.1 · 21 Oct 2026
*Coach video chapters from YouTube*
<!-- area: fixes -->

**Fixes**
- Each exercise in the coach video now starts at its YouTube timestamp (Humming at 7:15, Falsetto voice at 19:30, and so on). The times read from the video's slides were a few seconds late, and the level times were off.
- YouTube only marks where each exercise starts, so tapping an exercise plays it from the top, and Loop repeats the whole exercise. The L1 · L2 · L3 picker is gone for now.
- The times live in one list in the app's content file. If you add level times there later (three per exercise), the level picker comes back for those exercises.

## 3.16 · 21 Oct 2026
*Coach video in the app*
<!-- area: practice -->

**Adding it**
- Settings › Coach video › **Add coach video…** picks the video from Files. It stays on this iPhone: it's never put online and isn't in your backups, so keep the file in Files to add it again (after re-adding the app, for example).
- Once added, Settings shows its name, its 12 exercises and 36 levels, and its size, with **Replace video…** and **Remove video**. Reset all data leaves it alone; only Remove removes it.

**The player**
- Exercises › **Coach video** opens it. The row says where you paused, so it doubles as Resume.
- The bar under the video covers only the exercise you're on, as its three levels, so dragging is precise.
- **L1 · L2 · L3** jumps to the start of that level. **Loop** repeats the level you're on. **Speed** goes 0.75× · 1× · 1.25× without changing the pitch.
- Tap any exercise in the list to play it from your current level. The one playing shows small wave bars.
- Back and forward 10 seconds, full screen, and play and pause from the lock screen.

**Other ways in**
- Each exercise's page (1 to 12) has **Play with coach**, starting it at your current level.
- In a session, Foundation and Rotation have a **Coach video** row. It stays hidden until you tap it; then the video sits under the step's title for the rest of the session, playing that step's first exercise at your level. ‹ and › move to the step's other exercises. Next and Back cue the next step's exercise, paused. The session clock carries on separately.

**While you're elsewhere**
- Leave the player (or the session step) while the video plays and it carries on in a small window you can drag to any corner, with a play/pause button. Paused, a small ✕ closes it. Tap it to go back.
- A playing take still wins the window. Playing a take or starting a recording pauses the coach video, and playing the video stops a take.

## 3.15.1 · 19 Oct 2026
*Swipe back shadow*
<!-- area: look -->

**Fixes**
- After swiping back, the page's soft shadow now shrinks with it into its card. Before, it stayed the size of the screen while the page shrank.

## 3.15 · 19 Oct 2026
*Card zoom and swipe back*
<!-- area: look -->

**Opening and closing pages**
- Tapping a card that opens a page now zooms into it: exercises (in Exercises and Today's suggested rotation), songs (in Songs and Today's pinned songs), Show all sessions, Show all song practice, Show all songs, Changelog and the song page's Song practice.
- The page grows out of the card with its title starting where the card's name is, beginning in the card's colour so dark mode never shows an empty dark box.
- Back shrinks the page back into the card it came from, and the list is where you left it, not back at the top.
- If the card has scrolled out of sight, the page just fades and shrinks a little.
- Tapping Back in the middle of a zoom turns it round from wherever it is. Nothing ever waits for a zoom to finish before you can tap.

**Swipe back**
- On any page with a Back button, swipe right from anywhere (not just the edge). The page follows your finger and shrinks a little, with the screen you came from underneath.
- Let go past about a fifth of the screen, or flick, and it goes back into its card. Let go before that and it settles back.
- Whatever your finger lands on comes first: swiping a row to pin or delete it, the level buttons, charts you slide across, sliders and anything that scrolls sideways never start a swipe back.
- On Rotation and Application it goes back a step, like Back.

**Sessions**
- Start session (and Resume session) expands from the button into the session. Song practice expands from its card, on Today or on a song.
- Back from Foundation shrinks the session back into Resume session.
- Finishing shrinks the session back into Start session on Today, behind the summary. Song practice shrinks back into its card.

**Also**
- The weekly goal arc zooms into Progress.
- Tapping a day in the practice calendar grows that day's sessions out of the day.
- Saving a new song shrinks the paste sheet into the song's new row in Songs, then the row opens the song.
- With Reduce Motion on, zooms become a short fade, and a swipe back moves the page sideways without shrinking it.

## 3.14 · 19 Oct 2026
*Motion details*
<!-- area: look -->

**Lists**
- Deleting a session, song practice, exercise or song: the row shrinks away and the rows below slide up to close the gap.
- A new exercise slides into its place in the list.
- Pinning a song makes it travel up into Pinned (and back down when you unpin it). Songs you pin elsewhere slide into Today's pinned list.
- Changing how songs are sorted slides each song to its new place, one after another.
- In All sessions, switching between Sessions and Song practice brings the new rows in one after another.

**Progress**
- Changing the range (D, W, M…) makes the bars ripple to their new heights, left to right.
- The arrows send the ripple the way time goes: earlier runs right to left, later left to right. The total slides the same way, without rolling digits.
- The breakdown bars grow from the left, one row after another.
- Tapping or sliding across the bars still follows your finger instantly.

**Today**
- Once the app has opened, the weekly goal arc fills to this week's minutes and the Monday to Sunday circles ripple in.
- After finishing a session, today's circle pops in once you close the summary.
- After you back up, the backup reminder shrinks away and the page closes the gap.
- The practice calendar's days ripple in when it opens and when you change month.

**Recall**
- Stepping down a hint level hides the lyrics word by word, in reading order. Stepping back up shows them again from the end backwards.
- A line you peek at settles in with a small spring.

**Sessions and songs**
- Next brings the next step in from the right, and Back brings the earlier one in from the left.
- Switching between Practise, Recall and Perform brings the bottom buttons in with a spring. Changing the hint level leaves them still.
- A new take slides in at the top of the takes sheet, and starring a take gives the star a small pop.
- An exercise's level chart draws from left to right, ending on the latest level.

**Backup**
- "Preparing backup" turns into "Backup ready" in the same sheet, which grows to fit instead of rising again.
- After backing up, the red "Last backed up" line fades to its normal colour.

**Reduce Motion**
- With Reduce Motion on (Settings › Accessibility › Motion), nothing slides, pops or ripples. Changes now fade in and out over about a fifth of a second instead of snapping. Before this, every animation was simply switched off.

## 3.13 · 17 Oct 2026
*The launch ripple*
<!-- area: look -->

**Opening the app**
- When the app opens fresh, the sound-wave bars on the icon pulse one after another, like a ripple.
- The launch screen then fades away with a slight zoom, and Today's blocks rise in from top to bottom.
- It only plays when the app opens fresh, or reloads after an update. Switching tabs or coming back to the app doesn't replay it.
- After importing a backup, the ripple plays again on Today, then "Backup restored" shows.
- The first moment looks the same as before: the plain background with the icon, with no white flash or jump.
- If a session is running, its floating window appears once Today has risen in.
- With Reduce Motion on (Settings › Accessibility › Motion), nothing pulses or rises: the launch screen just fades.

## 3.12 · 17 Oct 2026
*A floating window for sessions and takes*
<!-- area: practice -->

**Floating window**
- Leave a session and a small window stays on every other screen, showing what's running (like "Focused session · Rotation") and its time.
- Its button pauses the session without leaving the page. While paused, it says Paused and the time stops.
- Tap it to go straight back to the same step, scrolled to where you were.
- Song practice gets the window once its first take starts, since that's when its clock starts.
- Today's Resume button and the In progress row still work as before.

<!-- area: recordings -->
**Takes**
- Switch away while a take is playing and the window shows the take instead: "Playing · Chorus 2" (or the song's name for song practice), its time and progress, and a pause button.
- Tap it to go back to the song with that section's takes open, or to song practice.
- If a session and a take are both going, the take is shown. The window goes when the take ends.
- Closing a section's takes now lets the take carry on playing, with the window there to pause it.

<!-- area: look -->
**Moving it**
- Drag it to any corner and it springs there, like picture in picture on iPhone. A quick flick sends it to the corner you throw it towards.
- It remembers its corner on this device, starting in the bottom right above the tab bar.
- It stays out of the way: hidden on its own screen, while a sheet is open and while recording, and clear of the tab bar, Recall's hint capsule and the sidebar on iPad and Mac.

## 3.11 · 17 Oct 2026
*Lyrics as one page, and the app's own springs*
<!-- area: songs -->

**The lyrics page**
- A song is now one continuous page. The boxes around each section are gone: small grey labels and a little space separate them, and the lyrics are a comfortable reading size.
- Tap a section to focus it. A soft patch appears behind just that section, with **Record**, its takes and **Marks**.
- While a section is focused, the rest of the song dims and softly blurs, more the further away it is. Far lyrics stay recognisable, and the section labels never blur, so it's easy to pick where to go next.
- Tap the same section again, or anywhere away from the lyrics, and it melts back into the page.
- **Marks** opens Annotate at that section.
- In Recall, tapping a line still peeks at it; tap a section's label to focus it.
- With Reduce Motion on in your iPhone's settings, other sections only dim, with no blur and no easing.
- The lyrics editor keeps its boxes, since they help while typing.

<!-- area: look -->
**Motion**
- The app now has one shared set of springs, so movement can feel the same everywhere: a gentle one for most things, a slightly quicker one for moving between pages, and a livelier one for small pops. The lyrics focus is the first thing to use them, and more will follow.

## 3.10.2 · 16 Oct 2026
*Recall stays put*
<!-- area: songs -->

- Changing the hint level in Recall no longer shows a tip line above the lyrics, so the sections stay exactly where they are.

## 3.10.1 · 16 Oct 2026
*Steadier sheets, honest timing, softer Recall*
<!-- area: fixes -->

**Sheets**
- Scrolling a sheet no longer scrolls the page behind it. When a sheet reaches its top or bottom, or the swipe is on the dimmed page around it, everything behind stays still. This applies to every sheet and to the session clock, with touch and with a mouse or trackpad.
- Tall sheets still scroll inside themselves, and dragging a sheet down by its top still closes it.

<!-- area: practice -->
**Song practice**
- Song practice is timed from your **first take**, not from when it opens. Choosing a song or warming up is never counted.
- Until then the timer says **Not started**, there's no clock or Pause, and the button at the bottom says **Record a take first**.
- Leaving before you've recorded anything drops it quietly, with nothing to resume or discard. Today only shows song practice as in progress once it's timed.
- This works the same from Today, a pinned song or the bottom of a song. Song practice already in progress carries on as before.

<!-- area: progress -->
**Weekly goal**
- Tap the weekly goal on Today to open Progress on this week's sessions.

<!-- area: songs -->
**Recall**
- Hidden letters are now soft rounded pills instead of thin lines. The letters keep their place, so nothing moves as you change level, and the pills fade in.
- Tapping a line shows only that line, and tapping it again while it shows starts its time again.
- **Hold a line** to keep it showing until you let go.
- **Settings › Recall › Peek length** sets how long a tapped line shows: 1, 2, 3 or 5 seconds (2 to start). It's included in backups.
- Screen readers no longer read hidden words aloud.

## 3.10 · 16 Oct 2026
*Songs: Recall, sing it from memory*
<!-- area: songs -->

**Recall**
- **Recall** is a new mode for a song, between Practise and Perform. It hides the lyrics a step at a time, so you can learn them by heart.
- Five levels: **Full lyrics**, **Word shapes** (each word's first letter), **First words** (the first word of each line), **Cues only** and **Blank**. Hidden letters become faint lines in place, so nothing on the page moves as you change level.
- Marks stay visible at every level, so breaths, runs and pitch marks still guide you.
- The hint capsule at the bottom steps between levels: the open eye shows more, the closed eye hides more, and tapping the level's name opens a menu of all five.
- Tap a hidden line to peek at it for a couple of seconds. Tap a section's heading to select it and record, as in Practise.
- The options button (•••) offers **From the start**, **From the end** (sections listed last first) and **Start anywhere**, which picks a section at random and points to it.
- Recall always starts at Full lyrics, from the start.

<!-- area: look -->
**Small screens**
- The Practise, Recall and Perform switch fits beside its buttons on the smallest iPhones.

## 3.9 · 16 Oct 2026
*Songs: record a section and hear it back*
<!-- area: recordings -->

**Record a section**
- In **Practise** or **Perform**, tap a section to select it. It gets a blue outline and two buttons: **Record**, and how many takes it has. Tap it again to let go.
- **Record** starts straight away. The page scrolls to the section, the top bar says what's recording (for example "Recording Chorus 2"), and a recording bar at the bottom shows the time, a level meter and Stop.
- While recording, the screen stays on that section: the Practise and Perform switch dims, other sections can't be tapped, and there's no back or edit until you stop.
- A take stops by itself after 2 minutes. Leaving the app or the song stops it and saves it, as song practice already does.
- Recordings are AAC mono at about 96 kbps where the phone offers it, with the phone's voice processing (echo and noise reduction, automatic volume) turned off, so the take sounds like your voice in the room.

**Hear it back**
- Stopping opens the section's takes over the song: the new take, big, with play, its progress, a star and a reminder that fresh ears help.
- Below it are every take you've starred for that section, and the latest and first while they're kept. **Record again** is at the bottom, and tapping a take adds notes, as in song practice.
- The same sheet opens from the section's takes button. A section that isn't selected shows how many takes it has in its heading.

**Where takes live**
- Each take belongs to one place in the song. Linked repeats share their lyrics, but Chorus 1 and Chorus 2 keep their own takes.
- Unlinking or moving a section keeps its takes with it.
- The keep rule is the same: the last 3 takes of a song, from any section, plus every take you star.
- Takes from before 3.9 belong to the whole song and still play in song practice, which now says which section each take came from.
- Recording a take counts as practising the song, so **Practised today** and the Recently practised order update straight away.

<!-- area: backup -->
**Backups**
- Backups still include recordings. **Exclude recordings** on Backup ready makes a smaller file without them.
- Check a backup and Import say **Recordings not included** for such a file. Restoring it keeps the recordings already on the device, and undoing that restore leaves them alone too.

## 3.8 · 15 Oct 2026
*Songs: lyrics you can mark up*
<!-- area: songs -->

**Songs**
- **Songs** is a new tab. Paste the lyrics of a song you're learning and they're split into labelled sections: verse, pre-chorus, chorus, bridge and the rest.
- Labels are found however the lyrics were written: `[Chorus]`, `Verse 2:`, `PRECHORUS`, `[Chorus: Sam]`. Blank lines split sections too, and a chorus that repeats itself is split in two.
- Website clutter is cleaned out of the paste: links, "You might also like", "Embed" and the "Lyrics" title line. Curly quotes become straight ones.
- Before saving, check the labels. Guesses are marked **Guessed**, and exact repeats are linked, so marks only need adding once. Tap the tick at the top to save.
- The lyrics you pasted are kept exactly as they were, alongside the sections.
- Titles and artists are capitalised for you.

**Marking up a song**
- Each section sits in its own card, one phrase per line, with repeats numbered (Chorus 1, Chorus 2). Long lines shrink to fit, and wrap only as a last resort.
- The pencil opens **Annotate**. Tap a word for Breath, Run, Higher, Lower, Sing as (the vowel to aim for) or a Note. Add an expressive cue to any section.
- A mark on a linked section shows on every repeat, and the same word lights up in each one.
- **Lyrics** edits the words. Marks follow their words as you edit. If a marked word changes, its mark is flagged to check; if it's removed, the mark waits at the top of the section to be moved or removed. The pencil shows how many need checking.
- Hold a section to drag it somewhere else in the song. **Undo** steps back through any change.
- **Unlink** gives one repeat its own copy, so it can change on its own.
- **Practise** shows every mark. **Perform** hides the technical ones and leaves the expressive cues. **Key** explains each mark.
- **Song practice** at the bottom of a song starts song practice with that song picked.

**Finding songs**
- Pin up to 3 songs. They sit at the top of Songs and on **Today**.
- The rest sort by Recently practised, Recently added or Title A–Z, chosen from the heading. Songs not practised yet say **New**.
- Swipe right to pin, left to delete. Press and hold for Pin, Rename and Delete. **Edit** selects several at once.
- **Search** sits at the bottom, beside the tab bar. It searches titles, artists and lyrics, ignores punctuation and accents, finds words in any order (even across lines) and forgives a slipped letter. Recent searches are kept.
- Songs from song practice are in Songs too. **Add lyrics** gives them lyrics and keeps their recordings.

<!-- area: look -->
**Settings moves to Today**
- **Settings** is now the gear at the top right of Today, and Songs takes its place in the tab bar.
- Songs are managed in Songs, so they're no longer listed in Exercises.
- On iPad and Mac, songs are listed on the left and the open song is on the right. New shortcuts: Cmd+F searches songs, Cmd+N adds one, Cmd+E edits, ↑ ↓ move between songs and Cmd+, opens Settings.

<!-- area: backup -->
**Kept safe**
- Backups include every song with its lyrics, marks and original paste.
- Each song is checked on its own when the app opens or a backup is read, so one damaged song can't affect the others. If a song's sections are damaged, they're rebuilt from the original paste.
- Songs you already had are upgraded in place: same name, same recordings, with a date added from their first song practice.

## 3.7.2 · 15 Oct 2026
*Your practice content in one place*
<!-- area: fixes -->

Nothing looks or works differently.
- Everything about your practice that you might want to change now lives in one file, `js/content.js`: goals, the coach video and its timings, the exercises and their write-ups, the quick words, and the Toggl tags. <!-- area: practice -->
- The file starts with a short guide to what's safe to change, and the one thing never to change: an exercise's id, which links it to your history.
- A new check runs with every update and after any edit to that file. It makes sure every exercise has a write-up, quick words and a video timing, and spells out exactly what's missing if not.

## 3.7.1 · 15 Oct 2026
*Tidier inside, the same on the outside*
<!-- area: fixes -->

Nothing looks or works differently. This release makes the app easier and safer to keep improving.
- The app's code is split from one very long file into a dozen readable ones: styles, settings, saved data, screens, the Changelog, backups, sessions and gestures.
- Updates now arrive all at once. The offline copy only switches to a new version after every part of it has downloaded, so a patchy connection mid-update can never leave a half-updated app.
- Every screen was compared before and after, and backups made before and after the change are identical.

## 3.7 · 15 Oct 2026
*Changelog, and data built to last*

<!-- area: look -->
**Changelog**
- **Changelog** in Settings shows every version of the app on a timeline, newest first, grouped into Version 3, 2 and 1.
- A growth chart shows every improvement since the first release, coloured by area. Tap a point to see that version, then jump to it.
- Each version shows its highlights, with **Show all** for the full list. Switch to **Every change** to open them all.
- It reads this changelog directly, so it's always up to date. It works offline too.
- Tapping the version number at the bottom of Settings opens it as well.

<!-- area: backup -->
**Data built to last**
- Your saved data now has a version number, so future updates can upgrade it one tested step at a time. Before any upgrade, the app keeps a copy of your data as it was.
- A backup made by a newer version of the app says so before you restore it, and suggests updating first.
- The app asks iOS to protect its data from being cleared when your iPhone runs low on space. **Storage protection** in Settings shows whether iOS agreed.
- Every update is now checked automatically before it goes live: every screen on every device, backups from earlier versions, and thousands of random taps. <!-- area: fixes -->

## 3.6 · 15 Oct 2026
*Organised, checked backups*
<!-- area: backup -->

**Organised backups**
- Backups are named by month and device, such as **Vocal Sessions backup · 2026-10 · iPhone.json**. Backing up again in the same month, Files asks to replace that month's file, so you keep one per month for each device.
- **Where backups go** in Settings shows how to make an **iCloud Drive › Vocal Sessions › Backups** folder. The first backup offers it too.
- **Backup history** in Settings lists every backup made on this device, with its size and what was in it.

**Checked backups**
- Each backup has a check code, a fingerprint of everything inside it.
- Before you save, the app reads the finished file back and checks it.
- **Check a backup** in Settings tells you whether a file is complete, what's inside and when it was made, without changing anything. It spots files that were cut short while copying, edited, or have damaged recordings.
- Backups from earlier versions still import. They're checked for readability, but have no check code.

**Safer restores**
- Import now shows the backup side by side with what's on this device.
- If anything here isn't in the backup, it tells you what would be removed and offers to back up first.
- **Undo last restore** in Settings puts everything back as it was, recordings included, for 30 days.

**Easy to recognise later**
- Each backup file starts with a short note in plain English: what it is, which device made it, what's inside and how to restore it.
- **Save a read-me file** in Settings saves a text file explaining the backups, to keep in the same folder.

## 3.5 · 15 Oct 2026
*History becomes Progress*

<!-- area: progress -->
**History is now Progress**
- **Recent:** your last 5 sessions, each with a small bar showing how its time split, and **Show all sessions**.
- **Practice time:**
  - A **D · W · M · 6M · Y · All** switch, like the Health app.
  - Your total for the period, with arrows to go back through earlier ones.
  - A stacked bar chart of Foundation, Rotation and Application. Tap or slide across the bars to see each hour, day, week or month.
  - A breakdown with time and percentage for each step.
- **Song practice:** this week's and this month's totals, your last 3 song practices, and **Show all song practice**.
- **All sessions** holds the full Sessions | Song practice list, with the same details, Copy for Toggl, edit and delete as before. On iPad and Mac it keeps its detail pane.

<!-- area: practice -->
**Time per step**
- Each session now saves the real time spent on Foundation, Rotation and Application, from the session clock.
- If a step took under 2 minutes, you probably filled it in at the end, for example while following the coach video in the car. These sessions show as a blended bar on the chart. Their time is still split using the coach video's length for each exercise, scaled by the levels you did, with Application as whatever's left.
- Sessions from before this version are split the same way.
- Session details show the time per step. Edit lets you switch between timed and filled in at the end, and set the minutes for each step.

<!-- area: look -->
**Colours**
- The chart uses indigo (Foundation), teal (Rotation) and amber (Application). They're checked for colour-blind separation and contrast in light and dark mode.

<!-- area: look -->
**More ways to the same place**
- Every summary leads to the same full lists and details. Song practice can be reached from Today, Progress, the calendar, and each song in Exercises.

<!-- area: backup -->
**Works offline**
- The app now keeps a copy of itself on your device, so it opens with no signal. When you're online it still loads fresh and picks up updates, including through pull to refresh.

## 3.4.1 · 14 Oct 2026
*A cleaner launch*
<!-- area: fixes -->

- The launch screen no longer flashes white before the icon appears. The right background colour is set on the very first frame, and the icon is built into the page so it appears at the same moment.
- The icon no longer jumps a few pixels as the app opens. It's centred on the full screen height, so it doesn't move when iOS adjusts the layout at launch, and it lines up exactly with the iOS launch image.

## 3.4 · 14 Oct 2026
*Launch screen*
<!-- area: look -->

**Launch screen**
- Opening the app shows the app icon in the middle of your normal background, light or dark, like a native iOS app.
- It stays up only until your data and recordings are ready, which is at least 0.6 seconds and never more than 2.5. Then it fades away with a slight zoom.
- iOS launch images for every recent iPhone and iPad (portrait and landscape on iPad), in light and dark. iOS shows these the instant you tap the icon, before the app has loaded, so there's no white flash.
  - These images take effect after the app is re-added to the Home Screen. The in-app launch screen works straight away.

## 3.3.2 · 14 Oct 2026
*Fixes from a full audit*
<!-- area: fixes -->

Fixes from a full audit: about 9,000 random taps across every screen and screen size, plus targeted tests and a code review.

- A damaged backup file no longer breaks the app. It's checked first, and all recordings are read before anything on your phone is replaced.
- Damaged saved data, or a full storage space when the app opens, no longer stops it starting.
- Leaving the Application or Song practice screen mid-recording now stops and saves the take, instead of recording in the background.
- On iPad and Mac, scrolling back up in the History or Exercises detail pane no longer triggers pull to refresh.
- Pull to refresh only ever updates to a newer version, never an older cached one.
- Edit and the long-session check refuse minutes that don't make sense (0, negative, or over 600) instead of quietly saving 1 minute.
- If a sheet has nothing to show (for example, notes for a take that was removed), it closes instead of hiding the tab bar.
- The page no longer nudges sideways when a segmented control bounces near the edge of the screen.
- The tab bar no longer stays shrunk when you're back at the top of a page after finishing.
- Coming back to the app refreshes the date and week, so Today is right the next morning.
- History stays in date order even if older data was saved out of order.

## 3.3.1 · 14 Oct 2026
*A way out of every sheet*
<!-- area: look -->

- Every sheet (session details, calendar, edit and others) has a close button (✕) at the top right, as in iOS 27. It stays in place while you scroll, so you can always get out.
- Drag a sheet down by its top to close it.
- Session and song practice details have an edit button (pencil) next to the ✕, replacing the "Edit session" text button. On iPad and Mac, the pencil sits beside the title in the detail pane.
- The extra "Close" button at the bottom of session details has been removed, because the ✕ does the same job.

## 3.3 · 14 Oct 2026
*Pull to refresh, and every screen size*

<!-- area: practice -->
**Pull to refresh**
- On Today and History, pull down from the top to refresh, like a native iOS app.
- The page follows your finger and the spinner fills in as you pull. Let go past the point where it's full to refresh, or earlier to cancel.
- Refreshing re-reads your saved data, updates the date and week, and checks GitHub for a newer version of the app. If there is one, it loads it straight away, so you no longer need to close and reopen the app after an update. <!-- area: backup -->

<!-- area: look -->
**Works on any screen**
- **iPhone on its side:** a compact tab bar with icons beside their labels. Today splits into two columns, and sheets stay a comfortable width.
- **iPad, or a narrower Mac window:**
  - Tabs move to a floating bar at the top, as on iPadOS.
  - Today becomes a two-column dashboard of cards.
  - History and Exercises become split views: pick on the left, see the details on the right.
  - Sheets open as centred cards.
  - Settings and the session steps stay at a readable width.
- **Mac, or iPad in landscape:** a sidebar with Today, History, Exercises and Settings.
- Turning your phone or resizing a window switches the layout straight away.
- With a mouse or trackpad, rows highlight when you hover over them.
- On a keyboard, Cmd (or Ctrl) + 1 to 4 switches between sections.

## 3.2 · 14 Oct 2026
*How did it go?*
<!-- area: practice -->

**How did it go?**
- Finishing a session or song practice opens a short "How did it go?" sheet.
  - Tap any words that fit, such as In control, Bit tight or Breath ran short.
  - Add your own words with "+ Your own". They're saved as chips for next time.
  - "Add a note" opens a text box only when you tap it.
  - Everything is optional, and ✕ skips it.
- How it went shows on the summary, in History, and in Toggl as a "How it went:" line.

**Notes on each exercise**
- A pencil on every Foundation and Rotation exercise opens quick words written for that exercise (for example "Buzz in the mask" for Humming), plus your own words and an optional note.
- These replace the old general note presets.
- Notes show on the summary, in Toggl next to the exercise, and on the exercise's History tab.

**Skip**
- Foundation levels are now Skip · 1 · 2 · 3.
- Skipped exercises don't count as done, and Toggl says "skipped".

**Song practice**
- A new Song practice card on Today for when you just want to sing a song, record takes and see how it went.
- It has its own stats and never counts towards your weekly goal, streak, monthly minutes, last-done dates or suggestions. <!-- area: progress -->
- History has a Sessions | Song practice switch, and song practice shows as a coral dot on the calendar. <!-- area: progress -->
- In Toggl it's tagged `#song-practice`. The Application step in a full session stays `#application`.

<!-- area: recordings -->
**Notes on takes**
- Tap a take to add quick words (like "Flat on the high note") and a note. This works in song practice and Application.
- Take notes are included in backups. <!-- area: backup -->

**Session clock**
- The top bar shows a live timer, such as "1 of 3 · 12:40".
- Tap it to open a larger clock with Pause, Resume and a time for each step. Paused time isn't counted.
- If a session has been running for over 90 minutes when you finish, the app asks how long you actually practised.

<!-- area: progress -->
**Edit finished sessions**
- Open any session or song practice and tap Edit to change the date, minutes, levels, notes and how it went.
- Monthly minutes, your streak, last-done dates and the exercise charts update to match.

<!-- area: practice -->
**Also new**
- Suggested rotation now picks the exercise that's gone longest since you last did it. Exercises you've never done come first.
- A backup reminder appears on Today if you've never backed up, or if it's been more than two weeks. <!-- area: backup -->
- Tap the date or the "Today" title to open the calendar, as well as the arrow. <!-- area: progress -->
- If you leave the app while recording, the take is stopped and saved, and the app tells you when you come back. <!-- area: recordings -->
- A tip about watching the coach video in picture-in-picture with YouTube Premium.
- Sheets no longer replay their slide-up animation when you tap something inside them. <!-- area: look -->

## 3.1 · 14 Oct 2026
*Liquid Glass*
<!-- area: look -->

**Liquid Glass upgrades** (a CSS imitation; the real material is only available to native apps)
- Bars, buttons and sheets have a brighter rim, a soft inner glow and a highlight along the top edge.
- A soft fade sits under the top bar when content scrolls beneath it.
- The tab bar shrinks to a small circle as you scroll down, and comes back when you scroll up or tap it.
- Level pickers have a glass knob that slides between 1, 2 and 3 and stretches slightly as it moves.
- Buttons spring back when pressed, sheets spring up, and the screen eases back behind an open sheet.
- The main session button is tinted glass.

**Exercise glyphs**
- Each exercise has its own icon, coloured by focus area:
  - Blue: cord closure
  - Purple: register
  - Teal: resonance
  - Amber: agility
  - Coral: blend
- Your own exercises get a sparkle icon.
- The glyphs appear on the Exercises tab, in the rotation picker, on each exercise page and in Today's suggestion.

<!-- area: progress -->
**Practice calendar**
- Today shows the full date above the title, with an arrow that opens a calendar of the month.
- Days you practised are highlighted and today is outlined. Arrows move between months.
- Tap a highlighted day to see its session, then tap the session for full details. Closing it returns you to the calendar.
- The calendar shows each month's session count and total time.

**Settings**
- New About section with a link to this GitHub repo.
- The version and release date show at the bottom of Settings.

## 3.0.1 · 14 Oct 2026
*No more accidental zoom*
<!-- area: fixes -->

- Pinch to zoom and double-tap to zoom are turned off, and tapping a text box no longer zooms the page. Quick repeated taps still register.

## 3.0 · 14 Oct 2026
*Today, Settings and exercise pages*
<!-- era: Liquid Glass · Native look, deeper tracking, and an app that stands on its own -->

<!-- area: look -->
**New app icon:** coral background with solid white sound-wave bars.

<!-- area: progress -->
**Today, in the style of Apple Books**
- A progress arch shows this week's minutes against a 70-minute goal.
- A Monday-to-Sunday row fills in each day you practised.
- The streak counts weeks in a row where you hit 70 minutes. The current week never breaks it while it's still in progress.
- Rows for this month's minutes (against 280) and the suggested rotation exercise.

<!-- area: backup -->
**Settings tab (new)**
- **Export backup:** saves one file with everything: sessions, minutes, exercises, songs, settings and recordings.
- **Import backup:** shows what's inside, then replaces this phone's data after you confirm. It also restores the last-backed-up time.
- The last backup time shows under the backup options, and turns red after 14 days.
- Recordings storage, reset this month and reset all data moved here from Today. Reset all data offers to export a backup first.

<!-- area: practice -->
**Exercise pages**
- Tap any exercise to open its own page, with **Summary** and **History** tabs.
- **Summary:** what it is, why it helps, and where it shows up in songs, taken from the vocal exercise write-ups.
- **History:** a chart of your level over time, plus every session the exercise was in.
- Your own exercises can have a description you write yourself.

<!-- area: practice -->
**Exercises tab**
- Descriptions show when each exercise was last done instead of a count. Practice from before 14 Oct shows as "last done before 14 Oct".
- One Coach video link replaces the Watch button on every exercise. During a session, it's a video button in the top bar.

<!-- area: practice -->
**Deleting**
- Swipe left to delete past sessions, takes, songs and your own exercises. Every delete asks "Are you sure?" first.
- Takes can be deleted one at a time.
- Deleting a session takes its minutes off that month and updates last-done dates.

## 2.0 · 14 Oct 2026
*A native iOS redesign*
<!-- era: Native iOS · Rebuilt to look and feel like an iPhone app -->

A full redesign to look and feel like a native iOS app.

<!-- area: look -->
**Look**
- iOS system font, system blue and automatic dark mode. The old orange ivanc.digital styling and Barlow fonts are gone.
- Large titles, rounded list groups and glass bars.

<!-- area: look -->
**Tabs:** Today, History and Exercises.

<!-- area: practice -->
**Sessions**
- Levels use an inline 1 · 2 · 3 picker.
- Rotation lets you pick several exercises, each with its own level.
- Notes come from presets or your own words.
- An unfinished session is saved, so you can resume or discard it later.

<!-- area: recordings -->
**Application step**
- A song library, so you pick a song instead of typing it.
- Record and play back takes:
  - Mono and compressed, up to 2 minutes each
  - Keeps the last 3 takes per song, plus any you star
- Rate pitch, tone and ease from 1 to 3.
- Share a take to Files or iCloud Drive.

<!-- area: progress -->
**History:** every finished session, with Copy for Toggl.

<!-- area: backup -->
**Data**
- Your existing streak, minutes and custom exercises carried over.
- First app icon.

## 1.0 · 25 May 2026
*First release*
<!-- era: The tracker · A simple three-block session tracker -->
<!-- area: practice -->

First release.
- A three-block session tracker: Foundation, Rotation and Application.
- Exercise levels with a confirm step before logging.
- Toggl-ready copy with `#tags`, including Copy All.
- Streak counter and a monthly progress bar towards 280 minutes. <!-- area: progress -->
- Smart rotation suggestions and custom exercises.
- Light-mode design in the ivanc.digital style. <!-- area: look -->
