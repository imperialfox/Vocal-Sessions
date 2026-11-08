# Element sheet · Vocal Sessions

Every named part in the app: its name, where it is named, how the app finds it, the parts kit part it is (by its gallery number), how it presses, its corner and its motion, and its status. An app's own part, with no kit part, says why. Written by `tools/reference/elements.py` from `js/register.js` and from the app itself (headless, the tests' sample data, motion off), so the values are what the page really uses, mapped back to their names; don't edit by hand. The naming rules: [MAINTAINING › Screen IDs › Naming rules](../MAINTAINING.md#naming-rules).

A note points at a part as `VS-009 › song-row`; a shared or by-action part is named the same on every screen it shows on.

**How to read the values.** Kit part: the gallery number in `tools/parts-kit/README.md` › Parts. Press: how it presses (the Presses section below). Corner: a named corner (`--r-card` …), `capsule`, `circle` or `none`. Motion: the springs and named timings its own transitions use (`gentle`, `--ease-out` …), `none` when it doesn't move at rest; a press's own motion is in Presses. A part that shows in more than one place lists each value it has (`a · b`). A dash: the sample data doesn't reach it ([Not reached](#not-reached)).

**35 shared parts, 377 names by action, 207 parts named on their screens. 240 of 618 in use read from the app.**

## Shared

Named wherever they show: the tab bar, Back, Close, the standard roles, fields and links.

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status |
|---|---|---|---|---|---|---|---|
| `today-tab` | `[data-a="tab"][data-v="today"]` | 1 Glass, 4 Tab bar | none | none | none |  | In use |
| `progress-tab` | `[data-a="tab"][data-v="history"]` | 1 Glass, 4 Tab bar | none | none | none |  | In use |
| `songs-tab` | `[data-a="tab"][data-v="songs"]` | 1 Glass, 4 Tab bar | none | none | none |  | In use |
| `exercises-tab` | `[data-a="tab"][data-v="exercises"]` | 1 Glass, 4 Tab bar | none | none | none |  | In use |
| `search-button` | `[data-a="findOpen"]` | 1 Glass, 6 Tab bar search, 12 Glass button | Glass, grows | circle | `--ease-out`, `pill` |  | In use |
| `settings-button` | `[data-a="openSettings"]` | 12 Glass button | Glass, grows | circle | none |  | In use |
| `back-button` | `#barL button[aria-label^="Back"], [data-a="allBack"], [data-a="ckCheckBack"], [data-a="coachBack"], [data-a="exBack"], [data-a="gdBack"], [data-a="keyBack"], [data-a="logBack"], [data-a="mpBack"], [data-a="patBack"], [data-a="setBack"], [data-a="setPgBack"], [data-a="sgBack"], [data-a="trkBack"]` | 12 Glass button | Glass, grows | circle | none |  | In use |
| `close-button` | `.shbtn[data-a="close"], .pk-sheet-close` | 12 Glass button | Glass, grows | circle | none |  | In use |
| `done-button` | `[data-a="close"][data-v="done"]` |  | none | none | none | A plain text button; the kit has no plain text button | In use |
| `cancel-button` | `[data-a="close"][data-v="cancel"], .pk-alert-btn[data-a="no"], .pk-action.pk-cancel` | 47 Action sheet | none | none | none |  | In use |
| `confirm-button` | `.pk-alert-btn[data-a="yes"]` | 48 Alert | — | — | — |  | In use |
| `grabber` | `.pk-grabber` | 41 Sheet | none | capsule | none |  | In use |
| `undo-button` | `.pk-toast-undo` | 49 Toast | — | — | — |  | In use |
| `search-field` | `#fq` | 1 Glass, 6 Tab bar search | none | none | none |  | In use |
| `song-search-field` | `#sgqi` | 26 Search field | none | none | none |  | In use |
| `note-field` | `.notebox .field` |  | — | — | — |  | In use |
| `minutes-field` | `#longMins, #edMins` |  | none | `--r-medium` | none | The app's own text field, not kit part 27 | In use |
| `date-field` | `#edDate` |  | — | — | — |  | In use |
| `foundation-minutes-field` | `#edF` |  | — | — | — |  | In use |
| `rotation-minutes-field` | `#edR` |  | — | — | — |  | In use |
| `word-field` | `#wordIn` |  | none | `--r-medium` | none | The app's own text field, not kit part 27 | In use |
| `song-field` | `#songIn` |  | none | `--r-medium` | none | The app's own text field, not kit part 27 | In use |
| `exercise-name-field` | `#exName` |  | none | `--r-medium` | none | The app's own text field, not kit part 27 | In use |
| `description-field` | `#exWhat, #whatIn` |  | none | `--r-medium` | none | The app's own text field, not kit part 27 | In use |
| `title-field` | `#sgRenIn, #sgTitle, #ckTitle` |  | none | `--r-medium` | none | The app's own text field, not kit part 27 | In use |
| `artist-field` | `#sgRenArt, #sgArtist, #ckArtist` |  | none | `--r-medium` | none | The app's own text field, not kit part 27 | In use |
| `lyrics-field` | `#sgLyr` |  | — | — | — |  | In use |
| `cue-field` | `#sgCueIn` |  | — | — | — |  | In use |
| `mark-text-field` | `#mkIn` |  | — | — | — |  | In use |
| `take-name-field` | `#tkNameIn` |  | — | — | — |  | In use |
| `comment-field` | `#tkCIn` |  | — | — | — |  | In use |
| `marker-name-field` | `#trkMkIn` |  | — | — | — |  | In use |
| `tempo-field` | `#melTempoIn` |  | — | — | — |  | In use |
| `coach-video-link` | `#coachVideoLink` | 12 Glass button | Glass, grows | circle | none |  | In use |
| `github-link` | `#githubLink` | 35 List row | Row, highlights | none | none |  | In use |

## By action

Wherever the action shows, its button gets this name. A screen's own parts and the shared ones win over these.


### already named on a screen (Q36 to Q47): the same name wherever else the action shows

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status |
|---|---|---|---|---|---|---|---|
| `compare-button` | `[data-a="apCmp"]` |  | — | — | — |  | In use |
| `done-button` | `[data-a="apDone"]` |  | — | — | — |  | In use |
| `hear-both-button` | `[data-a="apHear"]` |  | — | — | — |  | In use |
| `sung-rungs-row` | `[data-a="apLadFold"]` |  | — | — | — |  | In use |
| `line-switch` | `[data-a="apLine"]` |  | — | — | — |  | In use |
| `ladder-switch` | `[data-a="apMode"]` | 23 Segmented control | none | capsule | `--ease-out` |  | In use |
| `not-recorded-button` | `[data-a="apNoRec"]` |  | none | none | none | Application card's own buttons, drawn with the card | In use |
| `note-button` | `[data-a="apNote"]` |  | — | — | — |  | In use |
| `repeat-button` | `[data-a="apRpt"]` |  | — | — | — |  | In use |
| `sing-button` | `[data-a="apSing"]` |  | none | capsule | none | Application card's own buttons, drawn with the card | In use |
| `skip-rung-button` | `[data-a="apSkip"]` |  | — | — | — |  | In use |
| `song-row` | `[data-a="apSong"]` | 35 List row | Row, highlights | none | none |  | In use |
| `songs-sort` | `[data-a="apSort"]` |  | none | none | none | A list heading that opens the sort menu; the kit has no heading button | In use |
| `stop-button` | `[data-a="apStop"]` |  | — | — | — |  | In use |
| `by-feel-button` | `[data-a="bfFeel"]` |  | — | — | — |  | In use |
| `start-button` | `[data-a="bfStart"]` |  | — | — | — |  | In use |
| `to-stepper` | `[data-a="bfStep"][data-v="hi"]` |  | — | — | — |  | In use |
| `from-stepper` | `[data-a="bfStep"][data-v="lo"]` |  | — | — | — |  | In use |
| `done-button` | `[data-a="bfStop"]` |  | — | — | — |  | In use |
| `use-button` | `[data-a="bfUse"]` |  | — | — | — |  | In use |
| `check-row` | `[data-a="checkPick"]` |  | — | — | — |  | In use |
| `controls-button` | `[data-a="ckGrid"]` | 14 Solid press | Solid, shrinks | circle | none |  | In use |
| `edit-button` | `[data-a="ckGridEdit"]` |  | — | — | — |  | In use |
| `control-tile` | `[data-a="ckTile"]` | 14 Solid press | Solid, shrinks | circle | none |  | In use |
| `clock-pill` | `[data-a="clock"]` | 12 Glass button | Glass, grows | capsule | none |  | In use |
| `add-video-row` | `[data-a="coachAdd"]` |  | — | — | — |  | In use |
| `coach-video-row` | `[data-a="coachSettings"]` |  | — | — | — |  | In use |
| `level-button` | `[data-a="exLevel"]` |  | none | circle | none | The exercise page's level buttons, the coach video's levels; the kit has no level picker | In use |
| `more-button` | `[data-a="exMore"]` |  | none | none | none | A small text link on the page; the kit has no text link | In use |
| `back-up-button` | `[data-a="exportPrep"]` | 14 Solid press | Solid, shrinks · none | capsule · none | none |  | In use |
| `page-picker` | `[data-a="exTab"]` | 23 Segmented control | none | capsule | `--ease-out` |  | In use |
| `cancel-button` | `[data-a="findCancel"]` |  | — | — | — |  | In use |
| `close-search-button` | `[data-a="findClose"]` | 1 Glass, 6 Tab bar search, 12 Glass button | Glass, grows | circle | `--ease-out`, `pill` |  | In use |
| `finish-here-button` | `[data-a="finHere"]` |  | — | — | — |  | In use |
| `step-summary` | `[data-a="flowOpen"]` |  | — | — | — |  | In use |
| `guide-row` | `[data-a="gdOpen"]` | 35 List row | Row, highlights | none | none |  | In use |
| `close-button` | `[data-a="gdPeekClose"]` |  | — | — | — |  | In use |
| `learn-more-button` | `[data-a="gdPeekMore"]` |  | — | — | — |  | In use |
| `week-goal` | `[data-a="goalOpen"]` |  | — | — | — |  | In use |
| `list-picker` | `[data-a="histTab"]` |  | — | — | — |  | In use |
| `import-row` | `[data-a="importPick"]` |  | — | — | — |  | In use |
| `practise-pattern-row` | `[data-a="keyGo"]` |  | — | — | — |  | In use |
| `practise-play-button` | `[data-a="keyHear"]` |  | — | — | — |  | In use |
| `scale-lanes-chip` | `[data-a="keyLanes"]` |  | — | — | — |  | In use |
| `note-button` | `[data-a="keyNote"]` |  | — | — | — |  | In use |
| `use-button` | `[data-a="keySave"]` |  | — | — | — |  | In use |
| `key-choice-button` | `[data-a="keyUse"]` |  | — | — | — |  | In use |
| `whole-time-button` | `[data-a="longAll"]` |  | — | — | — |  | In use |
| `continue-button` | `[data-a="longOk"]` |  | — | — | — |  | In use |
| `cancel-button` | `[data-a="melCancel"]` |  | — | — | — |  | In use |
| `cancel-button` | `[data-a="melDrop"]` |  | — | — | — |  | In use |
| `sheet-settings-button` | `[data-a="melInfo"]` |  | — | — | — |  | In use |
| `key-row` | `[data-a="melKey"]` |  | — | — | — |  | In use |
| `replace-row` | `[data-a="melReplaceAsk"]` |  | — | — | — |  | In use |
| `add-anyway-button` | `[data-a="melSameGo"]` |  | — | — | — |  | In use |
| `open-button` | `[data-a="melSameOpen"]` |  | — | — | — |  | In use |
| `save-button` | `[data-a="melSave"]` |  | — | — | — |  | In use |
| `this-song-button` | `[data-a="melTitleHere"]` |  | — | — | — |  | In use |
| `new-song-button` | `[data-a="melTitleNew"]` |  | — | — | — |  | In use |
| `loop-button` | `[data-a="mpLoop"]` |  | — | — | — |  | In use |
| `my-note-button` | `[data-a="mpMy"]` |  | — | — | — |  | In use |
| `play-button` | `[data-a="mpPP"]` |  | — | — | — |  | In use |
| `show-all-row` | `[data-a="openAll"]` |  | — | — | — |  | In use |
| `date-line` | `[data-a="openCal"]` |  | — | — | — |  | In use |
| `exercise-row` | `[data-a="openEx"]` |  | — | — | — |  | In use |
| `changelog-row` | `[data-a="openLog"]` |  | — | — | — |  | In use |
| `bridge-cue-switch` | `[data-a="patBCue"]` |  | — | — | — |  | In use |
| `bridge-row` | `[data-a="patBridge"]` |  | — | — | — |  | In use |
| `chord-switch` | `[data-a="patCue"]` |  | — | — | — |  | In use |
| `drone-switch` | `[data-a="patDrone"]` |  | — | — | — |  | In use |
| `listen-switch` | `[data-a="patListen"]` |  | — | — | — |  | In use |
| `pattern-pill` | `[data-a="patOpen"]` |  | — | — | — |  | In use |
| `sound-row` | `[data-a="patSoundPick"]` |  | — | — | — |  | In use |
| `stop-past-last-switch` | `[data-a="patStopLast"]` |  | — | — | — |  | In use |
| `stop-at-top-switch` | `[data-a="patStopTop"]` |  | — | — | — |  | In use |
| `voice-type-row` | `[data-a="patVoiceType"]` |  | — | — | — |  | In use |
| `pause-button` | `[data-a="pauseToggle"]` |  | — | — | — |  | In use |
| `peek-length-picker` | `[data-a="peekLen"]` |  | — | — | — |  | In use |
| `earlier-button` | `[data-a="pnav"]` |  | — | — | — |  | In use |
| `range-picker` | `[data-a="prange"]` |  | — | — | — |  | In use |
| `record-button` | `[data-a="rec"]` |  | — | — | — |  | In use |
| `resume-session-button` | `[data-a="resume"]` |  | — | — | — |  | In use |
| `exercise-row` | `[data-a="ring"]` |  | — | — | — |  | In use |
| `more-exercises-sort` | `[data-a="rSort"]` |  | none | none | none | A list heading that opens the sort menu; the kit has no heading button | In use |
| `done-button` | `[data-a="savedDone"]` |  | — | — | — |  | In use |
| `save-button` | `[data-a="saveEdit"]` |  | — | — | — |  | In use |
| `add-button` | `[data-a="saveEx"]` |  | — | — | — |  | In use |
| `save-button` | `[data-a="saveHow"]` |  | — | — | — |  | In use |
| `read-me-row` | `[data-a="saveReadme"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |
| `add-button` | `[data-a="saveSong"]` |  | — | — | — |  | In use |
| `save-button` | `[data-a="saveWhat"]` |  | — | — | — |  | In use |
| `add-button` | `[data-a="saveWord"]` |  | — | — | — |  | In use |
| `main-button` | `[data-a="sckMain"]` |  | — | — | — |  | In use |
| `times` | `[data-a="sckSwap"]` |  | — | — | — |  | In use |
| `gradient-switch` | `[data-a="setGrad"]` |  | — | — | — |  | In use |
| `screen-ids-switch` | `[data-a="setIds"]` |  | — | — | — |  | In use |
| `settings-row` | `[data-a="setPg"]` |  | — | — | — |  | In use |
| `reduce-motion-picker` | `[data-a="setReduce"]` |  | — | — | — |  | In use |
| `slow-motion-switch` | `[data-a="setSlow"]` |  | — | — | — |  | In use |
| `reduce-transparency-switch` | `[data-a="setTransp"]` |  | — | — | — |  | In use |
| `add-lyrics-button` | `[data-a="sgAddLyrics"]` |  | — | — | — |  | In use |
| `sheet-music-door` | `[data-a="sgAddPdf"]` |  | — | — | — |  | In use |
| `edit-button` | `[data-a="sgListEdit"]` |  | — | — | — |  | In use |
| `new-song-button` | `[data-a="sgNew"]` |  | — | — | — |  | In use |
| `song-row` | `[data-a="sgOpen"]` |  | — | — | — |  | In use |
| `song-practice-row` | `[data-a="sgPractise"]` | 35 List row | Row, highlights | none | none |  | In use |
| `play-button` | `[data-a="sgRowPlay"]` |  | — | — | — |  | In use |
| `save-button` | `[data-a="sgSave"]` |  | — | — | — |  | In use |
| `song-search-field` | `[data-a="sgSearch"]` |  | — | — | — |  | In use |
| `sort-menu` | `[data-a="sgSortMenu"]` |  | — | — | — |  | In use |
| `share-button` | `[data-a="shareTake"]` |  | — | — | — |  | In use |
| `add-exercise-row` | `[data-a="sheet"][data-v="addEx"]` | 35 List row | Row, highlights | none | none |  | In use |
| `history-row` | `[data-a="sheet"][data-v="bkLog"]` |  | — | — | — |  | In use |
| `delete-all-button` | `[data-a="sheet"][data-v="clearRec"]` |  | — | — | — |  | In use |
| `delete-button` | `[data-a="sheet"][data-v="delTake"]` |  | none | none | none | A plain text button; the kit has no plain text button | In use |
| `discard-session-button` | `[data-a="sheet"][data-v="discard"]` |  | none | none | none | A plain text button; the kit has no plain text button | In use |
| `remove-prints-row` | `[data-a="sheet"][data-v="melPrintsDel"]` |  | — | — | — |  | In use |
| `reset-all-row` | `[data-a="sheet"][data-v="resetAll"]` |  | — | — | — |  | In use |
| `reset-month-row` | `[data-a="sheet"][data-v="resetMonth"]` |  | — | — | — |  | In use |
| `recordings-row` | `[data-a="sheet"][data-v="storage"]` |  | — | — | — |  | In use |
| `skip-button` | `[data-a="skipHow"]` |  | — | — | — |  | In use |
| `song-row` | `[data-a="song"]` |  | — | — | — |  | In use |
| `song-practice-card` | `[data-a="songStart"]` |  | — | — | — |  | In use |
| `start-session-button` | `[data-a="start"]` |  | — | — | — |  | In use |
| `takes-button` | `[data-a="tkOpenAll"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |
| `review-takes-row` | `[data-a="tkReview"]` |  | — | — | — |  | In use |
| `add-track-button` | `[data-a="trkAdd"]` | 35 List row | Row, highlights | none | none |  | In use |
| `level-picker` | `[data-a="trkLevel"]` |  | — | — | — |  | In use |

### Q48 options shown on one screen and named there by their group only

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status |
|---|---|---|---|---|---|---|---|
| `ending-option` | `[data-a="patEnding"]` | 23 Segmented control | none | capsule | `--ease-out` |  | In use |
| `notes-option` | `[data-a="patNotes"]` | 23 Segmented control | none | capsule | `--ease-out` |  | In use |
| `vowel-option` | `[data-a="patVowel"]` | 23 Segmented control | none | capsule | `--ease-out` |  | In use |
| `delete-exercise-button` | `[data-a="sheet"][data-v="delEx"]` |  | none | none | none | A plain text button; the kit has no plain text button | In use |

### Today, sessions and Progress

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status |
|---|---|---|---|---|---|---|---|
| `edit-session-button` | `[data-a="editSess"]` | 12 Glass button | Glass, grows | circle | none |  | In use |
| `session-row` | `[data-a="calSession"]` |  | — | — | — |  | In use |
| `day-tile` | `[data-a="calDay"]` | 14 Solid press | Solid, shrinks | circle | none |  | In use |
| `time-split-option` | `[data-a="esplit"]` |  | — | — | — |  | In use |
| `exercise-note-button` | `[data-a="exNote"]` |  | — | — | — |  | In use |
| `add-note-button` | `[data-a="openNote"]` |  | none | `--r-medium` | none | A small text link on the page; the kit has no text link | In use |
| `add-word-button` | `[data-a="addWord"]` | 14 Solid press, 18 Chips | Solid, shrinks | capsule | none |  | In use |
| `word-chip` | `[data-a="wTog"]` | 18 Chips | none | capsule | `--ease-out` |  | In use |
| `clear-notes-button` | `[data-a="xnClear"]` |  | — | — | — |  | In use |
| `focus-chip` | `[data-a="focus"]` | 18 Chips | none | capsule | `--ease-out` |  | In use |
| `done-button` | `[data-a="flowDone"]` |  | — | — | — |  | In use |
| `keep-time-button` | `[data-a="awayKeep"]` |  | — | — | — |  | In use |
| `take-time-out-button` | `[data-a="awayOut"]` |  | — | — | — |  | In use |
| `done-button` | `[data-a="sckDone"]` |  | — | — | — |  | In use |
| `fix-time-row` | `[data-a="sckFix"]` |  | — | — | — |  | In use |
| `save-time-button` | `[data-a="sckFixSave"]` |  | — | — | — |  | In use |
| `previous-month-button` | `[data-a="calMove"][data-v="-1"]` | 14 Solid press | Solid, shrinks | circle | none |  | In use |
| `next-month-button` | `[data-a="calMove"][data-v="1"]` | 14 Solid press | Solid, shrinks | circle | none |  | In use |
| `delete-session-button` | `[data-a="sheet"][data-v="delSession"]` |  | none | none | none | A plain text button; the kit has no plain text button | In use |
| `delete-song-practice-button` | `[data-a="sheet"][data-v="delSongSess"]` |  | — | — | — |  | In use |

### Application and takes

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status |
|---|---|---|---|---|---|---|---|
| `restart-ladder-button` | `[data-a="apLadAgain"]` |  | — | — | — |  | In use |
| `record-over-track-switch` | `[data-a="apOver"]` | 21 Switch, 35 List row | Row, highlights | `--r-medium` | none |  | In use |
| `song-summary-row` | `[data-a="apReopen"]` |  | — | — | — |  | In use |
| `section-pill` | `[data-a="apSec"]` |  | — | — | — |  | In use |
| `change-section-button` | `[data-a="apSecs"]` |  | — | — | — |  | In use |
| `play-take-button` | `[data-a="playTake"]` |  | none | capsule · circle | none | A take's own controls, drawn with its row in the takes list | In use |
| `star-button` | `[data-a="star"]` |  | none | capsule | none | A take's own controls, drawn with its row in the takes list | In use |
| `take-note-button` | `[data-a="takeNote"]` |  | none | none | none | A take's own controls, drawn with its row in the takes list | In use |
| `cue-chip` | `[data-a="rcue"]` |  | — | — | — |  | In use |
| `own-cue-chip` | `[data-a="rown"]` |  | — | — | — |  | In use |
| `add-song-button` | `[data-a="sheet"][data-v="addSong"]` | 35 List row | Row, highlights | none | none |  | In use |
| `headphones-button` | `[data-a="recOver"][data-v="hp"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |
| `speaker-button` | `[data-a="recOver"][data-v="spk"]` |  | none | none | none | A plain text button; the kit has no plain text button | In use |

### Exercises, the pattern player and the coach video

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status |
|---|---|---|---|---|---|---|---|
| `coach-video-row` | `[data-a="openCoach"]` |  | — | — | — |  | In use |
| `video-exercise-row` | `[data-a="coachEx"]` |  | — | — | — |  | In use |
| `full-screen-button` | `[data-a="coachFS"]` |  | — | — | — |  | In use |
| `loop-button` | `[data-a="coachLoop"]` |  | — | — | — |  | In use |
| `level-button` | `[data-a="coachLv"]` |  | — | — | — |  | In use |
| `play-button` | `[data-a="coachPlay"]` |  | — | — | — |  | In use |
| `speed-button` | `[data-a="coachSpeed"]` |  | — | — | — |  | In use |
| `level-button` | `[data-a="fwLv"]` |  | — | — | — |  | In use |
| `open-player-button` | `[data-a="fwOpen"]` |  | — | — | — |  | In use |
| `play-button` | `[data-a="fwToggle"]` |  | — | — | — |  | In use |
| `video-tile` | `[data-a="fwVTap"]` |  | — | — | — |  | In use |
| `tucked-window-tab` | `[data-a="fwTab"]` |  | — | — | — |  | In use |
| `close-button` | `[data-a="fwX"]` |  | — | — | — |  | In use |
| `favourite-button` | `[data-a="patFav"]` |  | — | — | — |  | In use |
| `group-tab` | `[data-a="patGroup"]` |  | — | — | — |  | In use |
| `stay-on-key-button` | `[data-a="patHold"]` |  | — | — | — |  | In use |
| `sound-item` | `[data-a="patMenuPick"]` |  | — | — | — |  | In use |
| `range-nudge-button` | `[data-a="patNudge"]` | 1 Glass, 15 Buttons on a bar, 24 Stepper | On a bar, lights up | capsule | none |  | In use |
| `pattern-tile` | `[data-a="patPick"]` |  | — | — | — |  | In use |
| `play-button` | `[data-a="patPlay"]` |  | — | — | — |  | In use |
| `speed-up-button` | `[data-a="patRamp"]` |  | — | — | — |  | In use |
| `sound-pill` | `[data-a="patSound"]` |  | — | — | — |  | In use |
| `speed-pill` | `[data-a="patSpd"]` |  | — | — | — |  | In use |
| `voice-range-button` | `[data-a="patVoice"]` |  | — | — | — |  | In use |
| `window-play-button` | `[data-a="patWin"]` |  | — | — | — |  | In use |
| `skip-back-button` | `[data-a="coachSkip"][data-v="-10"]` |  | — | — | — |  | In use |
| `skip-forward-button` | `[data-a="coachSkip"][data-v="10"]` |  | — | — | — |  | In use |
| `skip-back-button` | `[data-a="fwSkip"][data-v="-10"]` |  | — | — | — |  | In use |
| `skip-forward-button` | `[data-a="fwSkip"][data-v="10"]` |  | — | — | — |  | In use |
| `start-lower-button` | `[data-a="patShift"][data-v="-1"]` |  | — | — | — |  | In use |
| `start-higher-button` | `[data-a="patShift"][data-v="1"]` |  | — | — | — |  | In use |
| `slower-button` | `[data-a="patSpdStep"][data-v="-1"]` |  | — | — | — |  | In use |
| `faster-button` | `[data-a="patSpdStep"][data-v="1"]` |  | — | — | — |  | In use |
| `remove-video-button` | `[data-a="sheet"][data-v="coachDel"]` |  | — | — | — |  | In use |
| `edit-description-button` | `[data-a="sheet"][data-v="editWhat"]` |  | — | — | — |  | In use |

### Songs: the list, search and adding a song

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status |
|---|---|---|---|---|---|---|---|
| `all-songs-row` | `[data-a="sgAll"]` |  | — | — | — |  | In use |
| `swipe-delete-button` | `[data-a="sgDelRow"]` |  | none | none | none | The song list's own swipe buttons, not kit part 39 | In use |
| `swipe-pin-button` | `[data-a="sgPinRow"]` |  | none | none | none | The song list's own swipe buttons, not kit part 39 | In use |
| `delete-selected-button` | `[data-a="sgLDel"]` |  | — | — | — |  | In use |
| `pin-selected-button` | `[data-a="sgLPin"]` |  | — | — | — |  | In use |
| `select-all-button` | `[data-a="sgSelAll"]` |  | — | — | — |  | In use |
| `done-button` | `[data-a="sgListDone"]` |  | — | — | — |  | In use |
| `cancel-button` | `[data-a="sgQCancel"]` |  | — | — | — |  | Retired · 3.64 |
| `clear-song-search-button` | `[data-a="sgQClear"]` |  | — | — | — |  | In use |
| `recent-song-search-row` | `[data-a="sgRecent"]` |  | — | — | — |  | In use |
| `remove-song-recent-button` | `[data-a="sgRmRecent"]` |  | — | — | — |  | In use |
| `clear-song-recents-button` | `[data-a="sgClearRecent"]` |  | — | — | — |  | In use |
| `delete-item` | `[data-a="sgCtxDel"]` |  | — | — | — |  | In use |
| `pin-item` | `[data-a="sgCtxPin"]` |  | — | — | — |  | In use |
| `rename-item` | `[data-a="sgCtxRename"]` |  | — | — | — |  | In use |
| `order-item` | `[data-a="sgOrder"]` |  | — | — | — |  | In use |
| `sort-item` | `[data-a="sgSetSort"]` |  | — | — | — |  | In use |
| `swap-pin-button` | `[data-a="sgSwapPin"]` |  | — | — | — |  | In use |
| `save-button` | `[data-a="sgSaveRename"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |
| `confirm-delete-button` | `[data-a="sgDoDel"]` |  | — | — | — |  | In use |
| `add-mode-tab` | `[data-a="sgAddMode"]` |  | — | — | — |  | In use |
| `choose-file-button` | `[data-a="sgAddPick"]` |  | — | — | — |  | In use |
| `song-length-button` | `[data-a="sgAddLen"]` |  | — | — | — |  | In use |
| `relink-button` | `[data-a="sgAddRelink"]` |  | — | — | — |  | In use |
| `next-step-button` | `[data-a="sgSplit"]` |  | — | — | — |  | In use |
| `previous-step-button` | `[data-a="sgBackStep"]` |  | — | — | — |  | In use |
| `block-label-button` | `[data-a="sgBlockLabel"]` |  | — | — | — |  | In use |
| `label-option` | `[data-a="sgPick"]` |  | — | — | — |  | In use |

### Songs: the song page and marks

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status |
|---|---|---|---|---|---|---|---|
| `done-button` | `[data-a="sgDone"]` |  | — | — | — |  | In use |
| `edit-mode-tab` | `[data-a="sgEditMode"]` |  | — | — | — |  | In use |
| `undo-button` | `[data-a="sgUndo"]` |  | — | — | — |  | In use |
| `mode-tab` | `[data-a="sgMode"]` | 23 Segmented control | none | capsule | `--ease-out` |  | In use |
| `hint-level-button` | `[data-a="sgHMenu"]` |  | — | — | — |  | In use |
| `hint-item` | `[data-a="sgSetHint"]` |  | — | — | — |  | In use |
| `recall-options-button` | `[data-a="sgRMenu"]` |  | — | — | — |  | In use |
| `start-anywhere-item` | `[data-a="sgAnywhere"]` |  | — | — | — |  | In use |
| `section-row` | `[data-a="sgSec"]` |  | none | `--r-medium` | `gentle` | A lyric section: a tap focuses it on the song page, so it isn't a list row | In use |
| `label-button` | `[data-a="sgLabel"]` |  | — | — | — |  | In use |
| `cue-button` | `[data-a="sgCue"]` |  | — | — | — |  | In use |
| `save-cue-button` | `[data-a="sgSaveCue"]` |  | — | — | — |  | In use |
| `link-section-button` | `[data-a="sgLink"]` |  | — | — | — |  | In use |
| `unlink-button` | `[data-a="sgUnlink"]` |  | — | — | — |  | In use |
| `confirm-unlink-button` | `[data-a="sgDoUnlink"]` |  | — | — | — |  | In use |
| `relink-length-button` | `[data-a="sgLenRelinkYes"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |
| `move-section-button` | `[data-a="sgOMove"]` |  | — | — | — |  | In use |
| `remove-section-button` | `[data-a="sgORemove"]` |  | — | — | — |  | In use |
| `section-marks-button` | `[data-a="sgMarks"]` |  | — | — | — |  | In use |
| `section-takes-button` | `[data-a="sgTakes"]` |  | — | — | — |  | In use |
| `record-section-button` | `[data-a="sgRec"]` |  | — | — | — |  | In use |
| `stop-recording-button` | `[data-a="sgStop"]` |  | — | — | — |  | In use |
| `suggested-breath-button` | `[data-a="sgSugBr"]` |  | — | — | — |  | In use |
| `lyric-word` | `[data-a="sgWord"]` |  | — | — | — |  | In use |
| `edit-timing-button` | `[data-a="ckPencil"]` | 12 Glass button | Glass, grows | circle | none |  | In use |
| `key-help-button` | `[data-a="gdKey"]` |  | — | — | — |  | In use |
| `clear-selection-button` | `[data-a="mkClear"]` |  | — | — | — |  | In use |
| `keep-mark-button` | `[data-a="mkKeep"]` |  | — | — | — |  | In use |
| `layer-chip` | `[data-a="mkLayer"]` |  | none | capsule | none | The Marks layer chips, the app's own, not kit part 18 | In use |
| `mark-option` | `[data-a="mkOpt"]` |  | — | — | — |  | In use |
| `mark-type-option` | `[data-a="mkPick"]` |  | — | — | — |  | In use |
| `remove-mark-button` | `[data-a="mkRm"]` |  | — | — | — |  | In use |
| `add-text-button` | `[data-a="mkText"]` |  | — | — | — |  | In use |
| `marks-guide-row` | `[data-a="gdKeyRow"]` | 35 List row | Row, highlights | none | none |  | In use |
| `more-hints-button` | `[data-a="sgHint"][data-v="-1"]` |  | — | — | — |  | In use |
| `fewer-hints-button` | `[data-a="sgHint"][data-v="1"]` |  | — | — | — |  | In use |

### Song Clock and Check timing

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status |
|---|---|---|---|---|---|---|---|
| `add-track-button` | `[data-a="ckAddTrack"]` |  | — | — | — |  | In use |
| `done-button` | `[data-a="ckCheckDone"]` |  | — | — | — |  | In use |
| `flag-button` | `[data-a="ckFlag"]` |  | — | — | — |  | In use |
| `done-button` | `[data-a="ckHeadDone"]` |  | — | — | — |  | In use |
| `lyrics-tab` | `[data-a="ckHeadLyrics"]` |  | — | — | — |  | In use |
| `marks-tab` | `[data-a="ckHeadMarks"]` |  | — | — | — |  | In use |
| `song-length-row` | `[data-a="ckLen"]` |  | none | none | none | Song Clock's song length line, drawn with its header | In use |
| `lyric-line` | `[data-a="ckLine"]` |  | — | — | — |  | In use |
| `annotate-item` | `[data-a="ckLmMark"]` |  | — | — | — |  | In use |
| `play-from-here-item` | `[data-a="ckLmPlay"]` |  | — | — | — |  | In use |
| `retime-line-item` | `[data-a="ckLmRetime"]` |  | — | — | — |  | In use |
| `mute-button` | `[data-a="ckMute"]` |  | — | — | — |  | In use |
| `play-button` | `[data-a="ckPP"]` |  | — | — | — |  | In use |
| `set-length-button` | `[data-a="ckPickSet"]` |  | — | — | — |  | In use |
| `relink-button` | `[data-a="ckRelink"]` |  | — | — | — |  | In use |
| `retime-section-button` | `[data-a="ckRetime"]` |  | — | — | — |  | In use |
| `retime-line-button` | `[data-a="ckRetimeNow"]` |  | — | — | — |  | In use |
| `nudge-earlier-button` | `[data-a="ckNudge"][data-v="-0.2"]` |  | — | — | — |  | In use |
| `nudge-later-button` | `[data-a="ckNudge"][data-v="0.2"]` |  | — | — | — |  | In use |

### The track player and markers

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status |
|---|---|---|---|---|---|---|---|
| `play-button` | `[data-a="trkPP"]` | 15 Buttons on a bar | On a bar, lights up | circle | none |  | In use |
| `marker-chip` | `[data-a="trkChip"]` |  | — | — | — |  | In use |
| `chip-loop-button` | `[data-a="trkChipLoop"]` |  | — | — | — |  | In use |
| `end-here-button` | `[data-a="trkEndHere"]` |  | — | — | — |  | In use |
| `jog-side-option` | `[data-a="trkJogPos"]` | 35 List row | Row, highlights | none | none |  | In use |
| `line-start-button` | `[data-a="trkLnStart"]` |  | — | — | — |  | In use |
| `line-end-button` | `[data-a="trkLnEnd"]` |  | — | — | — |  | In use |
| `deselect-line-button` | `[data-a="trkLnX"]` |  | — | — | — |  | In use |
| `loop-button` | `[data-a="trkLoop"]` | 15 Buttons on a bar | On a bar, lights up | circle | `--dur-fade`, `ease` |  | In use |
| `loop-button` | `[data-a="trkMdLoop"]` |  | — | — | — |  | In use |
| `track-lyric-line` | `[data-a="trkLyr"]` |  | — | — | — |  | In use |
| `track-settings-button` | `[data-a="trkMenu"]` | 12 Glass button | Glass, grows | circle | none |  | In use |
| `add-marker-button` | `[data-a="trkMkAdd"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |
| `save-button` | `[data-a="trkMkSaveName"]` |  | — | — | — |  | In use |
| `section-start-row` | `[data-a="trkMkSec"]` |  | — | — | — |  | In use |
| `section-option` | `[data-a="trkMkSecPick"]` |  | — | — | — |  | In use |
| `next-marker-button` | `[data-a="trkNext"]` |  | — | — | — |  | In use |
| `open-track-button` | `[data-a="trkOpen"]` | 35 List row | Row, highlights | none | none |  | In use |
| `keep-markers-button` | `[data-a="trkPastKeep"]` |  | — | — | — |  | In use |
| `trim-button` | `[data-a="trkPastTrim"]` |  | — | — | — |  | In use |
| `replace-track-button` | `[data-a="trkReplace"]` | 35 List row | Row, highlights | none | none |  | In use |
| `replay-marker-button` | `[data-a="trkReplay"]` |  | — | — | — |  | In use |
| `track-lyric-row` | `[data-a="trkRow"]` |  | — | — | — |  | In use |
| `sound-button` | `[data-a="trkSnd"]` |  | — | — | — |  | In use |
| `lyrics-button` | `[data-a="trkSongLyrics"]` |  | — | — | — |  | In use |
| `speed-pill` | `[data-a="trkSpeed"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |
| `marker-tile` | `[data-a="trkTile"]` |  | — | — | — |  | In use |
| `tile-loop-button` | `[data-a="trkTileLoop"]` |  | — | — | — |  | In use |
| `loop-start-button` | `[data-a="trkToStart"]` | 15 Buttons on a bar | On a bar, lights up | circle | `--dur-fade`, `ease` |  | In use |
| `import-anyway-button` | `[data-a="trkBigYes"]` |  | — | — | — |  | In use |
| `set-start-button` | `[data-a="trkSet"][data-v="start"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |
| `set-end-button` | `[data-a="trkSet"][data-v="end"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |
| `remove-track-button` | `[data-a="sheet"][data-v="trkDel"]` | 35 List row | Row, highlights | none | none |  | In use |
| `clear-markers-button` | `[data-a="sheet"][data-v="trkMkClear"]` |  | — | — | — |  | In use |

### Takes on a song

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status |
|---|---|---|---|---|---|---|---|
| `delete-comment-button` | `[data-a="tkCDel"]` |  | — | — | — |  | In use |
| `edit-comment-button` | `[data-a="tkCEdit"]` |  | — | — | — |  | In use |
| `comment-chip` | `[data-a="tkCJump"]` |  | — | — | — |  | In use |
| `collapse-button` | `[data-a="tkCollapse"]` |  | — | — | — |  | In use |
| `delete-take-button` | `[data-a="tkDel"]` |  | none | none | none | A take's own controls, drawn with its row in the takes list | In use |
| `fold-button` | `[data-a="tkFold"]` |  | — | — | — |  | In use |
| `rename-take-button` | `[data-a="tkMenuRename"]` |  | — | — | — |  | In use |
| `clear-name-button` | `[data-a="tkNameClear"]` |  | — | — | — |  | In use |
| `done-button` | `[data-a="tkNameDone"]` |  | — | — | — |  | In use |
| `nudge-button` | `[data-a="tkNudge"]` |  | — | — | — |  | In use |
| `play-take-button` | `[data-a="tkPlay"]` |  | none | circle | none | A take's own controls, drawn with its row in the takes list | In use |
| `post-comment-button` | `[data-a="tkPost"]` |  | — | — | — |  | In use |
| `rename-take-button` | `[data-a="tkRename"]` |  | — | — | — |  | In use |
| `delete-old-take-button` | `[data-a="tkRvDel"]` |  | none | capsule | none | A take's own controls, drawn with its row in the takes list | In use |
| `timestamp-chip` | `[data-a="tkStamp"]` |  | — | — | — |  | In use |
| `star-button` | `[data-a="tkStar"]` |  | none | none | none | A take's own controls, drawn with its row in the takes list | In use |
| `takes-tab` | `[data-a="tkTab"]` |  | — | — | — |  | In use |
| `take-row` | `[data-a="tkTap"]` |  | none | none | none | A take's own controls, drawn with its row in the takes list | In use |
| `skip-back-button` | `[data-a="tkSkip"][data-v="-5"]` |  | — | — | — |  | In use |
| `skip-forward-button` | `[data-a="tkSkip"][data-v="5"]` |  | — | — | — |  | In use |

### Sheet music

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status |
|---|---|---|---|---|---|---|---|
| `show-all-button` | `[data-a="melAll"]` |  | — | — | — |  | In use |
| `octave-option` | `[data-a="melOct"]` |  | — | — | — |  | In use |
| `score-bar` | `[data-a="mpBar"]` |  | — | — | — |  | In use |
| `note-dot` | `[data-a="mpDot"]` |  | — | — | — |  | In use |
| `change-loop-button` | `[data-a="mpPick"]` |  | — | — | — |  | In use |
| `cancel-loop-button` | `[data-a="mpPickX"]` |  | — | — | — |  | In use |
| `view-option` | `[data-a="mpView"]` |  | — | — | — |  | In use |
| `slower-button` | `[data-a="melTempo"][data-v="-1"]` |  | — | — | — |  | In use |
| `faster-button` | `[data-a="melTempo"][data-v="1"]` |  | — | — | — |  | In use |
| `slower-button` | `[data-a="mpSpd"][data-v="-1"]` |  | — | — | — |  | In use |
| `faster-button` | `[data-a="mpSpd"][data-v="1"]` |  | — | — | — |  | In use |
| `fewer-bars-button` | `[data-a="mpZoom"][data-v="-1"]` |  | — | — | — |  | In use |
| `more-bars-button` | `[data-a="mpZoom"][data-v="1"]` |  | — | — | — |  | In use |
| `sheet-music-orphan-row` | `[data-a="sheet"][data-v="melOrphanDel"]` |  | — | — | — |  | In use |

### Search

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status |
|---|---|---|---|---|---|---|---|
| `clear-search-button` | `[data-a="findClear"]` |  | — | — | — |  | In use |
| `clear-recents-button` | `[data-a="findClearRecent"]` |  | — | — | — |  | In use |
| `lyric-result-row` | `[data-a="findLyr"]` |  | — | — | — |  | In use |
| `more-results-button` | `[data-a="findMore"]` |  | — | — | — |  | In use |
| `recent-search-row` | `[data-a="findRecent"]` |  | — | — | — |  | In use |
| `remove-recent-button` | `[data-a="findRmRecent"]` |  | — | — | — |  | In use |
| `take-result-row` | `[data-a="findTake"]` |  | — | — | — |  | In use |

### Settings, backups and the Changelog

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status |
|---|---|---|---|---|---|---|---|
| `set-up-folder-button` | `[data-a="bkGuideFrom"]` |  | — | — | — |  | In use |
| `restore-this-backup-button` | `[data-a="bkToImport"]` |  | — | — | — |  | In use |
| `exclude-recordings-switch` | `[data-a="exportNoRec"]` |  | — | — | — |  | In use |
| `save-backup-button` | `[data-a="exportSave"]` |  | — | — | — |  | In use |
| `restore-button` | `[data-a="importYes"]` |  | — | — | — |  | In use |
| `undo-restore-button` | `[data-a="undoYes"]` |  | — | — | — |  | In use |
| `ask-again-button` | `[data-a="persistAsk"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |
| `save-copy-button` | `[data-a="rescueSave"]` |  | — | — | — |  | In use |
| `delete-everything-button` | `[data-a="resetAll"]` |  | — | — | — |  | In use |
| `mode-option` | `[data-a="keyMode"]` | 23 Segmented control | none | capsule | `--ease-out` |  | In use |
| `show-in-timeline-button` | `[data-a="lgjump"]` |  | — | — | — |  | In use |
| `version-dot` | `[data-a="lgpick"]` |  | — | — | — |  | In use |
| `view-tab` | `[data-a="logMode"]` |  | — | — | — |  | In use |
| `show-more-button` | `[data-a="logMore"]` |  | — | — | — |  | In use |
| `try-again-button` | `[data-a="logRetry"]` |  | — | — | — |  | In use |
| `backup-guide-row` | `[data-a="sheet"][data-v="bkGuide"]` | 35 List row | Row, highlights | none | none |  | In use |
| `storage-protection-row` | `[data-a="sheet"][data-v="persist"]` | 35 List row | Row, highlights | none | none |  | In use |
| `delete-copy-button` | `[data-a="sheet"][data-v="rescueDel"]` |  | — | — | — |  | In use |
| `undo-restore-row` | `[data-a="sheet"][data-v="undoRestore"]` |  | — | — | — |  | In use |

## Presses

How each kind of button presses (Q53, 3.67). `KITPRESS` in `js/gestures.js` gives a button its kit class by what it is, so a new button with one of these classes gets the press for free. Every press is the kit's own: reused, none new. Rows highlight instead (D06, `row.press`).

| Kind | Kit part | Buttons | Press | Animation | Status |
|---|---|---|---|---|---|
| Glass button | 12 · `.pk-press` | `.glass:is(.circ, .shbtn, .txtbtn, .cta, .trkpad, .trkpill, .ppill, .prep, .mktp), #timer[data-a="clock"]` | Grows 17 pt on its longest side, lights up | Reused (the kit's) | In use |
| Button on a glass bar | 15 · `.pk-press-bar` | `.toptabs button, .trkb, .trkpp, .fwbtn, .pstep button, .pvstep .pk-stepper > button` | Lights up, same size | Reused (the kit's) | In use |
| Solid button | 14 · `.pk-press-solid` | `.cta, .circ, .shbtn, .txtbtn, .trkpad, .trkpill, .ppill, .prep, .pplay, .chip.add, .calbtn, .cal button, .nudge, .ckpi, .cktile, .sgplay, .sgtkb, .tkb, .tkbig, .cvpp, .cvpill, .ladnote, .ladrpt` | Shrinks to `--press` (0.93), back on `release` | Reused (the kit's) | In use |
| Picking chip | 18 · `.pk-chip` in `.pk-chips.pk-static` | `.chip.pk-chip` | No press; the colour fades as it's picked | Reused (the kit's) | In use |
| Note stepper | 24 · `.pk-stepper.pk-glass` | `.pvstep .pk-stepper` | Its halves are buttons on a glass bar (15) | Reused (the kit's) | In use |

<details><summary>Retired (1)</summary>

| Kind | Was | Replaced by | Status |
|---|---|---|---|
| The app's own press | `PRESS` in `js/gestures.js` (Q33): glass grew on `press`, settled on `release`, lit up with a registered `--lift`; solid buttons shrank on `:active` with a 0.5 s `--ease-pop` release | The kit's parts 12, 14, 15 (`tools/parts-kit/REPLACED.md`) | Retired · 3.67 |

</details>


## Named motion

Animations that took a named value or a kit spring in Q54 (3.68), so the app keeps one feel. Every one is reused, none new. What's left written by hand, with its reason, is in `tests/test_values.py`. Last checked 5 Nov 2026.

| Animation | Parts | Was | Now | Animation | Status |
|---|---|---|---|---|---|
| Row moves | `.rowc`, `.crow`, `.tkfg`, `.sw .fg` | own bounce, 0.22 to 0.35 s | `gentle` spring | Reused | In use |
| Pattern dots and vowel swap | `.pdraw .pnt`, `.pdraw .prip`, `.pvowel b.swap` | 0.25 to 0.6 s, own bounces | `ripple` spring | Reused | In use |
| Pattern steps | `.pt` | own bounce | `--ease-knob` | Reused | In use |
| Pattern player bubble and dim | `.phbub`, `#pHud .phscrim`, `.pt .pst > span` | 0.25 to 0.45 s | `gentle`, `--dur-fade` | Reused | In use |
| Pull to refresh | `#ptr.go .spin`, `main.ptr-snap` | 0.8 s spin, 0.42 s snap | kit spinner (`--dur-spin`, `--ease-steps`), `gentle` | Reused | In use |
| Launch screen (motion off) | `#splash`, `#splash .sp-icon` | 0.35 s, 0.45 s | `--dur-leave`, `--ease-accel` | Reused | In use |
| Launch ripple | `MOTION.LAUNCH` (js/launch.js) | numbers in launch.js | its own timings, named once in `MOTION.LAUNCH` | Reused | In use |
| Card zoom fades | `MOTION.ZOOM` (js/zoom.js) | 24 numbers in zoom.js | `MOTION.ms('quick')`, `('fade')` and its own, named in `MOTION.ZOOM` | Reused | In use |
| Session clock | `#layer .sck`, `.clockscrim` | 140 to 300 ms | kit part 50: `appear` 250, `leave` 350; Reduce Motion `--dur-reduced` | Reused | In use |
| Recall's hidden words | `.hx`, `.hxin .hx`, `.rl.peeking .hx` | 0.22 to 0.35 s | `--dur-fade`, `--ease-out` | Reused | In use |
| Sideways scroll fade, pointer hint | `[data-edge-fade]`, `.hint` | 0.18 s, 0.25 s | `--dur-fade`, `--ease-out` | Reused | In use |
| Note box | `.notebox` | 0.3 s | `--dur-appear` | Reused | In use |
| Takes closing | `VS-054` | 140 ms | `MOTION.ms('close')`, `MOTION.EASE.accel` | Reused | In use |
| Changelog timeline | `.tl-card`, `.tl-in.seen`, `.tl-more svg.i` | 0.3 to 0.6 s | `gentle` | Reused | In use |
| Changelog now dot | `.tl-item.now .tl-node::after` | pulsed forever | three pulses, then rests (as the exercise glow) | Reused | In use |
| Rung nudge | `.rgi.rneed > .rgrow` | 1.1 s | the same 1.2 s as `.rgi.rnudge` | Reused | In use |

<details><summary>Retired (4)</summary>

| Animation | Was | Status |
|---|---|---|
| `pop` keyframes | unused since the parts kit | Retired · 3.68 |
| `up` keyframes | unused | Retired · 3.68 |
| `pmIn` keyframes | the old pull-up menu, unused since the parts kit's menus | Retired · 3.68 |
| The Changelog now dot's endless pulse | `lgpulse` infinite | Retired · 3.68 |

</details>

## On their screens

### VS-001 · Today

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `date-line` | `[data-a="openCal"]` | 3 Large title, 14 Solid press | Solid, shrinks · none | none | none |  | In use |  |
| `backup-nudge` | `[data-a="exportPrep"]` | 14 Solid press | Solid, shrinks | `--r-medium` | none |  | In use |  |
| `week-goal` | `[data-a="goalOpen"]` | 35 List row | Row, highlights | `--r-large` | none |  | In use |  |
| `start-session-button` | `[data-a="start"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |
| `resume-session-button` | `[data-a="resume"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |
| `discard-session-button` | `[data-a="sheet"][data-v="discard"]` |  | none | none | none | A plain text button; the kit has no plain text button | In use |  |
| `rotation-row` | `[data-a="openEx"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `song-practice-card` | `[data-a="songStart"]` | 35 List row | Row, highlights | none | none |  | In use |  |

### VS-002 · Session · Foundation

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `step-button` | `#dock [data-a="cta"]` | 12 Glass button | Glass, grows | capsule | none |  | In use |  |
| `clock-pill` | `[data-a="clock"]` | 12 Glass button | Glass, grows | capsule | none |  | In use |  |
| `exercise-row` | `[data-a="ring"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `more-exercises-sort` | `[data-a="rSort"]` |  | none | none | none | A list heading that opens the sort menu; the kit has no heading button | In use |  |
| `add-exercise-row` | `[data-a="sheet"][data-v="addEx"]` | 35 List row | Row, highlights | none | none |  | In use |  |

### VS-003 · Session · Rotation

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `step-button` | `#dock [data-a="cta"]` | 12 Glass button | Glass, grows | capsule | none |  | In use |  |
| `clock-pill` | `[data-a="clock"]` | 12 Glass button | Glass, grows | capsule | none |  | In use |  |
| `finish-here-button` | `[data-a="finHere"]` |  | none | none | none | A small text link on the page; the kit has no text link | In use |  |
| `step-summary` | `[data-a="flowOpen"]` | 35 List row | Row, highlights | `--r-card` | none |  | In use |  |
| `exercise-row` | `[data-a="ring"]` | 35 List row | Row, highlights | none | none |  | In use |  |

### VS-004 · Session · Application

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `step-button` | `#dock [data-a="cta"]` | 12 Glass button | Glass, grows | capsule | none |  | In use |  |
| `clock-pill` | `[data-a="clock"]` | 12 Glass button | Glass, grows | capsule | none |  | In use |  |
| `step-summary` | `[data-a="flowOpen"]` | 35 List row | Row, highlights | `--r-card` | none |  | In use |  |
| `carry-on-card` | `#apcard` | 23 Segmented control | none | `--r-card` | none |  | In use |  |
| `sing-button` | `[data-a="apSing"]` |  | none | capsule | none | Application card's own buttons, drawn with the card | In use |  |
| `stop-button` | `[data-a="apStop"]` |  | — | — | — |  | In use |  |
| `compare-button` | `[data-a="apCmp"]` |  | — | — | — |  | In use |  |
| `done-button` | `[data-a="apDone"]` |  | — | — | — |  | In use |  |
| `not-recorded-button` | `[data-a="apNoRec"]` |  | none | none | none | Application card's own buttons, drawn with the card | In use |  |
| `song-row` | `[data-a="apSong"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `songs-sort` | `[data-a="apSort"]` |  | none | none | none | A list heading that opens the sort menu; the kit has no heading button | In use |  |
| `ladder-switch` | `[data-a="apMode"]` | 23 Segmented control | none | capsule | `--ease-out` |  | In use |  |
| `sung-rungs-row` | `[data-a="apLadFold"]` |  | — | — | — |  | In use |  |
| `skip-rung-button` | `[data-a="apSkip"]` |  | — | — | — |  | In use |  |
| `live-pitch-line` | `#apLive` |  | — | — | — |  | In use |  |
| `line-switch` | `[data-a="apLine"]` |  | — | — | — |  | In use |  |
| `hear-both-button` | `[data-a="apHear"]` |  | — | — | — |  | In use |  |
| `note-button` | `[data-a="apNote"]` |  | — | — | — |  | In use |  |
| `repeat-button` | `[data-a="apRpt"]` |  | — | — | — |  | In use |  |
| `scale-lanes-chip` | `[data-a="keyLanes"]` |  | — | — | — |  | In use |  |
| `key-choice-button` | `[data-a="keyUse"]` |  | — | — | — |  | In use |  |
| `key-change-button` | `.keyblk [data-a="keyChange"]` |  | — | — | — |  | In use |  |
| `practise-play-button` | `[data-a="keyHear"]` |  | — | — | — |  | In use |  |
| `practise-pattern-row` | `[data-a="keyGo"]` |  | — | — | — |  | In use |  |

### VS-005 · Session saved

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `done-button` | `[data-a="savedDone"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |

### VS-006 · Progress

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `range-picker` | `[data-a="prange"]` | 23 Segmented control | none | capsule | `--ease-out` |  | In use |  |
| `earlier-button` | `[data-a="pnav"]` |  | none | circle | none | The Progress chart's own arrows, drawn with the chart | In use |  |
| `session-row` | `[data-a="sheet"][data-v="session"],[data-a="sheet"][data-v="songSession"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `show-all-row` | `[data-a="openAll"]` | 35 List row | Row, highlights | none | none |  | In use |  |

### VS-007 · All sessions

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `list-picker` | `[data-a="histTab"]` | 23 Segmented control | none | capsule | `--ease-out` |  | In use |  |
| `session-row` | `[data-a="sheet"][data-v="session"],[data-a="sheet"][data-v="songSession"]` | 35 List row | Row, highlights | none | none |  | In use |  |

### VS-008 · Songs

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `edit-button` | `[data-a="sgListEdit"]` | 12 Glass button | Glass, grows | capsule | none |  | In use |  |
| `new-song-button` | `[data-a="sgNew"]` | 12 Glass button | Glass, grows | circle | none |  | In use |  |
| `song-search-field` | `[data-a="sgSearch"]` | 26 Search field | none | `--r-medium` | `sheet` |  | In use | search-field |
| `close-search-button` | `.pk-search-close[data-a="findClose"]` | 1 Glass, 6 Tab bar search, 12 Glass button | Glass, grows | circle | `--ease-out`, `pill` |  | In use |  |
| `sort-menu` | `[data-a="sgSortMenu"]` |  | none | none | none | A list heading that opens the sort menu; the kit has no heading button | In use |  |
| `song-row` | `[data-a="sgOpen"]` | 35 List row, 46 Long-press menu | Row, highlights | none | `--dur-fade`, `ease`, `gentle` |  | In use |  |
| `play-button` | `[data-a="sgRowPlay"]` | 14 Solid press | Solid, shrinks | circle | none |  | In use |  |

### VS-009 · Song page

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `controls-button` | `[data-a="ckGrid"]` |  | — | — | — |  | In use |  |
| `takes-button` | `[data-a="tkOpenAll"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |
| `add-lyrics-button` | `[data-a="sgAddLyrics"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |
| `song-practice-row` | `[data-a="sgPractise"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `add-track-row` | `[data-a="trkAdd"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `sheet-music-row` | `[data-a="melAdd"], [data-a="melOpen"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `key-row` | `.grp [data-a="keyChange"]` | 35 List row | Row, highlights | none | none |  | In use |  |

### VS-010 · Track player

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `add-track-button` | `[data-a="trkAdd"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |
| `level-picker` | `[data-a="trkLevel"]` | 23 Segmented control | none | capsule | `--ease-out` |  | In use |  |

### VS-012 · Song practice

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `save-button` | `#dock [data-a="cta"]` | 12 Glass button | Glass, grows | capsule | none |  | In use |  |
| `song-row` | `[data-a="song"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `record-button` | `[data-a="rec"]` | 35 List row | Row, highlights | none | none |  | In use |  |

### VS-013 · Exercises

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `coach-video-row` | `[data-a="coachSettings"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `exercise-row` | `[data-a="openEx"]` | 35 List row | Row, highlights | none | none |  | In use |  |

### VS-014 · Exercise page

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `page-picker` | `[data-a="exTab"]` | 23 Segmented control | none | capsule | `--ease-out` |  | In use |  |
| `level-button` | `[data-a="exLevel"]` |  | none | circle | none | The exercise page's level buttons, the coach video's levels; the kit has no level picker | In use |  |
| `more-button` | `[data-a="exMore"]` |  | none | none | none | A small text link on the page; the kit has no text link | In use |  |
| `bridge-line` | `#pcBridge` |  | — | — | — |  | In use |  |
| `listen-switch` | `#pcListen` |  | — | — | — |  | In use |  |

### VS-015 · Coach video

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `coach-video-row` | `[data-a="coachSettings"]` | 35 List row | Row, highlights | none | none |  | In use |  |

### VS-017 · Search

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `search-field` | `#fq` | 1 Glass, 6 Tab bar search | none | none | none |  | In use |  |
| `cancel-button` | `[data-a="findCancel"]` |  | — | — | — |  | In use |  |
| `close-search-button` | `[data-a="findClose"]` | 1 Glass, 6 Tab bar search, 12 Glass button | Glass, grows | circle | `--ease-out`, `pill` |  | In use |  |

### VS-018 · Settings

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `settings-row` | `[data-a="setPg"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `marks-guide-row` | `[data-a="gdOpen"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `changelog-row` | `[data-a="openLog"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `reset-month-row` | `[data-a="sheet"][data-v="resetMonth"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `reset-all-row` | `[data-a="sheet"][data-v="resetAll"]` | 35 List row | Row, highlights | none | none |  | In use |  |

### VS-019 · Settings › Backup

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `export-row` | `[data-a="exportPrep"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `import-row` | `[data-a="importPick"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `check-row` | `[data-a="checkPick"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `history-row` | `[data-a="sheet"][data-v="bkLog"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `read-me-row` | `[data-a="saveReadme"]` | 35 List row | Row, highlights | none | none |  | In use |  |

### VS-020 · Settings › Storage

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `recordings-row` | `[data-a="sheet"][data-v="storage"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `review-takes-row` | `[data-a="tkReview"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `remove-prints-row` | `[data-a="sheet"][data-v="melPrintsDel"]` |  | — | — | — |  | In use |  |

### VS-021 · Settings › Recall

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `peek-length-picker` | `[data-a="peekLen"]` | 23 Segmented control | none | capsule | `--ease-out` |  | In use |  |

### VS-022 · Settings › Coach video

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `add-video-row` | `[data-a="coachAdd"]` | 35 List row | Row, highlights | none | none |  | In use |  |

### VS-023 · Settings › Your voice

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `voice-type-row` | `[data-a="patVoiceType"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `stop-at-top-switch` | `[data-a="patStopTop"]` | 21 Switch, 35 List row | Row, highlights | none | none |  | In use |  |
| `stop-past-last-switch` | `[data-a="patStopLast"]` | 21 Switch, 35 List row | Row, highlights | none | none |  | In use |  |
| `bridge-row` | `[data-a="patBridge"]` | 35 List row | Row, highlights | none | none |  | In use |  |

### VS-024 · Settings › Pattern player

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `sound-row` | `[data-a="patSoundPick"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `drone-switch` | `[data-a="patDrone"]` | 21 Switch, 35 List row | Row, highlights | none | none |  | In use |  |
| `chord-switch` | `[data-a="patCue"]` | 21 Switch, 35 List row | Row, highlights | none | none |  | In use |  |
| `bridge-cue-switch` | `[data-a="patBCue"]` | 21 Switch, 35 List row | Row, highlights | none | none |  | In use |  |
| `listen-switch` | `[data-a="patListen"]` | 21 Switch, 35 List row | Row, highlights | none | none |  | In use |  |

### VS-025 · Settings › Appearance

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `gradient-switch` | `[data-a="setGrad"]` | 21 Switch, 35 List row | Row, highlights | none | none |  | In use |  |
| `screen-ids-switch` | `[data-a="setIds"]` | 21 Switch, 35 List row | Row, highlights | none | none |  | In use |  |

### VS-026 · Settings › Accessibility

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `reduce-motion-picker` | `[data-a="setReduce"]` | 35 List row | Row, highlights | none | none |  | In use |  |
| `reduce-transparency-switch` | `[data-a="setTransp"]` | 21 Switch, 35 List row | Row, highlights | none | none |  | In use |  |
| `slow-motion-switch` | `[data-a="setSlow"]` | 21 Switch, 35 List row | Row, highlights | none | none |  | In use |  |

### VS-028 · Marks guide

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `guide-row` | `[data-a="gdOpen"]` | 35 List row | Row, highlights | none | none |  | In use |  |

### VS-031 · How did it go?

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `save-button` | `[data-a="saveHow"]` | 14 Solid press | Solid, shrinks | circle | none |  | In use |  |
| `skip-button` | `[data-a="skipHow"]` | 12 Glass button | Glass, grows | circle | none |  | In use |  |

### VS-032 · How long did you practise?

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `continue-button` | `[data-a="longOk"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |
| `whole-time-button` | `[data-a="longAll"]` |  | none | none | none | A plain text button; the kit has no plain text button | In use |  |

### VS-033 · Exercise notes

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `done-button` | `.cta[data-a="close"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |

### VS-034 · Your own words

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `add-button` | `[data-a="saveWord"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |

### VS-037 · Discard session

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-040 · Edit session

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `save-button` | `[data-a="saveEdit"]` |  | — | — | — |  | In use |  |

### VS-041 · Delete session

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-043 · Delete song practice

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-045 · Add song

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `add-button` | `[data-a="saveSong"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |

### VS-046 · Delete song

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-048 · Take notes

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `done-button` | `.cta[data-a="close"]` |  | — | — | — |  | In use |  |
| `share-button` | `[data-a="shareTake"]` |  | — | — | — |  | In use |  |
| `delete-button` | `[data-a="sheet"][data-v="delTake"]` |  | — | — | — |  | In use |  |

### VS-049 · Delete take

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-050 · Song controls

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `edit-button` | `[data-a="ckGridEdit"]` | 12 Glass button | Glass, grows | capsule | none |  | In use |  |
| `control-tile` | `[data-a="ckTile"]` | 14 Solid press | Solid, shrinks | none | none |  | In use |  |

### VS-051 · New song

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `save-button` | `[data-a="sgSave"]` |  | — | — | — |  | In use |  |
| `sheet-music-door` | `[data-a="sgAddPdf"]` |  | — | — | — |  | In use |  |

### VS-056 · Delete this take

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 48 Alert | — | — | — |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 48 Alert | — | — | — |  | In use |  |

### VS-059 · Unlink from track

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-067 · Remove the track

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-071 · Clear all markers

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-074 · Add exercise

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `add-button` | `[data-a="saveEx"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |

### VS-075 · Exercise description

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `save-button` | `[data-a="saveWhat"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |

### VS-076 · Delete exercise

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-077 · Recordings (storage)

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `delete-all-button` | `[data-a="sheet"][data-v="clearRec"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |

### VS-078 · Delete all recordings

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-079 · Remove the coach video

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-080 · Delete the rescued copy

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-081 · Reset this month

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-082 · Reset all data

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `[data-a="resetAll"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |
| `cancel-button` | `.ghost[data-a="close"]` |  | none | none | none | A plain text button; the kit has no plain text button | In use |  |

### VS-092 · Session clock

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `pause-button` | `[data-a="pauseToggle"]` |  | — | — | — |  | In use |  |
| `main-button` | `[data-a="sckMain"]` |  | — | — | — |  | In use |  |
| `times` | `[data-a="sckSwap"]` |  | — | — | — |  | In use |  |

### VS-095 · Peek card

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `close-button` | `[data-a="gdPeekClose"]` |  | — | — | — |  | In use |  |
| `learn-more-button` | `[data-a="gdPeekMore"]` |  | — | — | — |  | In use |  |

### VS-096 · Find your bridge

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `start-button` | `[data-a="bfStart"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |
| `by-feel-button` | `[data-a="bfFeel"]` |  | none | none | none | A plain text button; the kit has no plain text button | In use |  |
| `done-button` | `[data-a="bfStop"]` |  | — | — | — |  | In use |  |
| `from-stepper` | `[data-a="bfStep"][data-v="lo"]` |  | — | — | — |  | In use |  |
| `to-stepper` | `[data-a="bfStep"][data-v="hi"]` |  | — | — | — |  | In use |  |
| `use-button` | `[data-a="bfUse"]` |  | — | — | — |  | In use |  |

### VS-097 · Practise in key

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `pattern-card` | `#pcCard` |  | — | — | — |  | In use |  |
| `pattern-pill` | `[data-a="patOpen"]` |  | — | — | — |  | In use |  |
| `start-note-stepper` | `#dock .pstep` |  | — | — | — |  | In use |  |
| `stay-on-key-button` | `#pRep` |  | — | — | — |  | In use |  |
| `play-button` | `#pPlay` |  | — | — | — |  | In use |  |

### VS-098 · Song key

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `mode-picker` | `.keymode .seg` | 23 Segmented control | none | capsule | none |  | In use |  |
| `note-button` | `[data-a="keyNote"]` | 14 Solid press | Solid, shrinks | `--r-medium` | `--dur-fade`, `ease`, `release` |  | In use |  |
| `use-button` | `[data-a="keySave"]` | 14 Solid press | Solid, shrinks | capsule | none |  | In use |  |

### VS-099 · Sheet music

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `octave-picker` | `.meloct` |  | — | — | — |  | In use |  |
| `tempo-field` | `#melTempoIn` |  | — | — | — |  | In use |  |
| `key-row` | `[data-a="melKey"]` |  | — | — | — |  | In use |  |
| `replace-row` | `[data-a="melReplaceAsk"]` |  | — | — | — |  | In use |  |

### VS-100 · Sheet music read

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `octave-picker` | `.meloct` |  | — | — | — |  | In use |  |
| `tempo-field` | `#melTempoIn` |  | — | — | — |  | In use |  |
| `save-button` | `[data-a="melSave"]` |  | — | — | — |  | In use |  |
| `cancel-button` | `[data-a="melDrop"]` |  | — | — | — |  | In use |  |

### VS-101 · Already on another song

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `open-button` | `[data-a="melSameOpen"]` | 47 Action sheet | none | none | none |  | In use |  |
| `add-anyway-button` | `[data-a="melSameGo"]` | 47 Action sheet | none | none | none |  | In use |  |

### VS-102 · A different song?

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `this-song-button` | `[data-a="melTitleHere"]` |  | — | — | — |  | In use |  |
| `new-song-button` | `[data-a="melTitleNew"]` |  | — | — | — |  | In use |  |

### VS-103 · Replace the sheet music?

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-104 · Big or long PDF

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-105 · Remove the prints?

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-106 · Reading sheet music

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `cancel-button` | `[data-a="melCancel"]` |  | — | — | — |  | In use |  |

### VS-107 · Delete sheet music with no song?

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | 1 Glass, 48 Alert | none | capsule | none |  | In use |  |

### VS-108 · Sheet music page

| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |
|---|---|---|---|---|---|---|---|---|
| `sheet-settings-button` | `[data-a="melInfo"]` |  | — | — | — |  | In use |  |
| `view-picker` | `.mpview` |  | — | — | — |  | In use |  |
| `speed-stepper` | `.mpspd` |  | — | — | — |  | In use |  |
| `bars-stepper` | `.mpzoom` |  | — | — | — |  | In use |  |
| `loop-strip` | `.mploop` |  | — | — | — |  | In use |  |
| `dots-view` | `.mpdots` |  | — | — | — |  | In use |  |
| `sheet-view` | `.mpsheet` |  | — | — | — |  | In use |  |
| `my-note-button` | `[data-a="mpMy"]` |  | — | — | — |  | In use |  |
| `play-button` | `[data-a="mpPP"]` |  | — | — | — |  | In use |  |
| `loop-button` | `[data-a="mpLoop"]` |  | — | — | — |  | In use |  |

## Not reached

Parts in use that the sample data doesn't show (an iPad or Mac layout, a state such as recording, the floating window, the session clock), so their values are a dash. Their kit part, if any, is read from how they're found. Reaching more of them is a change to `collect()` in `tools/reference/elements.py`.

<details><summary>Not reached (378)</summary>

- `confirm-button`
- `undo-button`
- `note-field`
- `date-field`
- `foundation-minutes-field`
- `rotation-minutes-field`
- `lyrics-field`
- `cue-field`
- `mark-text-field`
- `take-name-field`
- `comment-field`
- `marker-name-field`
- `tempo-field`
- `compare-button` (by action: `[data-a="apCmp"]`)
- `done-button` (by action: `[data-a="apDone"]`)
- `hear-both-button` (by action: `[data-a="apHear"]`)
- `sung-rungs-row` (by action: `[data-a="apLadFold"]`)
- `line-switch` (by action: `[data-a="apLine"]`)
- `note-button` (by action: `[data-a="apNote"]`)
- `repeat-button` (by action: `[data-a="apRpt"]`)
- `skip-rung-button` (by action: `[data-a="apSkip"]`)
- `stop-button` (by action: `[data-a="apStop"]`)
- `by-feel-button` (by action: `[data-a="bfFeel"]`)
- `start-button` (by action: `[data-a="bfStart"]`)
- `to-stepper` (by action: `[data-a="bfStep"][data-v="hi"]`)
- `from-stepper` (by action: `[data-a="bfStep"][data-v="lo"]`)
- `done-button` (by action: `[data-a="bfStop"]`)
- `use-button` (by action: `[data-a="bfUse"]`)
- `check-row` (by action: `[data-a="checkPick"]`)
- `edit-button` (by action: `[data-a="ckGridEdit"]`)
- `add-video-row` (by action: `[data-a="coachAdd"]`)
- `coach-video-row` (by action: `[data-a="coachSettings"]`)
- `cancel-button` (by action: `[data-a="findCancel"]`)
- `finish-here-button` (by action: `[data-a="finHere"]`)
- `step-summary` (by action: `[data-a="flowOpen"]`)
- `close-button` (by action: `[data-a="gdPeekClose"]`)
- `learn-more-button` (by action: `[data-a="gdPeekMore"]`)
- `week-goal` (by action: `[data-a="goalOpen"]`)
- `list-picker` (by action: `[data-a="histTab"]`)
- `import-row` (by action: `[data-a="importPick"]`)
- `practise-pattern-row` (by action: `[data-a="keyGo"]`)
- `practise-play-button` (by action: `[data-a="keyHear"]`)
- `scale-lanes-chip` (by action: `[data-a="keyLanes"]`)
- `note-button` (by action: `[data-a="keyNote"]`)
- `use-button` (by action: `[data-a="keySave"]`)
- `key-choice-button` (by action: `[data-a="keyUse"]`)
- `whole-time-button` (by action: `[data-a="longAll"]`)
- `continue-button` (by action: `[data-a="longOk"]`)
- `cancel-button` (by action: `[data-a="melCancel"]`)
- `cancel-button` (by action: `[data-a="melDrop"]`)
- `sheet-settings-button` (by action: `[data-a="melInfo"]`)
- `key-row` (by action: `[data-a="melKey"]`)
- `replace-row` (by action: `[data-a="melReplaceAsk"]`)
- `add-anyway-button` (by action: `[data-a="melSameGo"]`)
- `open-button` (by action: `[data-a="melSameOpen"]`)
- `save-button` (by action: `[data-a="melSave"]`)
- `this-song-button` (by action: `[data-a="melTitleHere"]`)
- `new-song-button` (by action: `[data-a="melTitleNew"]`)
- `loop-button` (by action: `[data-a="mpLoop"]`)
- `my-note-button` (by action: `[data-a="mpMy"]`)
- `play-button` (by action: `[data-a="mpPP"]`)
- `show-all-row` (by action: `[data-a="openAll"]`)
- `date-line` (by action: `[data-a="openCal"]`)
- `exercise-row` (by action: `[data-a="openEx"]`)
- `changelog-row` (by action: `[data-a="openLog"]`)
- `bridge-cue-switch` (by action: `[data-a="patBCue"]`)
- `bridge-row` (by action: `[data-a="patBridge"]`)
- `chord-switch` (by action: `[data-a="patCue"]`)
- `drone-switch` (by action: `[data-a="patDrone"]`)
- `listen-switch` (by action: `[data-a="patListen"]`)
- `pattern-pill` (by action: `[data-a="patOpen"]`)
- `sound-row` (by action: `[data-a="patSoundPick"]`)
- `stop-past-last-switch` (by action: `[data-a="patStopLast"]`)
- `stop-at-top-switch` (by action: `[data-a="patStopTop"]`)
- `voice-type-row` (by action: `[data-a="patVoiceType"]`)
- `pause-button` (by action: `[data-a="pauseToggle"]`)
- `peek-length-picker` (by action: `[data-a="peekLen"]`)
- `earlier-button` (by action: `[data-a="pnav"]`)
- `range-picker` (by action: `[data-a="prange"]`)
- `record-button` (by action: `[data-a="rec"]`)
- `resume-session-button` (by action: `[data-a="resume"]`)
- `exercise-row` (by action: `[data-a="ring"]`)
- `done-button` (by action: `[data-a="savedDone"]`)
- `save-button` (by action: `[data-a="saveEdit"]`)
- `add-button` (by action: `[data-a="saveEx"]`)
- `save-button` (by action: `[data-a="saveHow"]`)
- `add-button` (by action: `[data-a="saveSong"]`)
- `save-button` (by action: `[data-a="saveWhat"]`)
- `add-button` (by action: `[data-a="saveWord"]`)
- `main-button` (by action: `[data-a="sckMain"]`)
- `times` (by action: `[data-a="sckSwap"]`)
- `gradient-switch` (by action: `[data-a="setGrad"]`)
- `screen-ids-switch` (by action: `[data-a="setIds"]`)
- `settings-row` (by action: `[data-a="setPg"]`)
- `reduce-motion-picker` (by action: `[data-a="setReduce"]`)
- `slow-motion-switch` (by action: `[data-a="setSlow"]`)
- `reduce-transparency-switch` (by action: `[data-a="setTransp"]`)
- `add-lyrics-button` (by action: `[data-a="sgAddLyrics"]`)
- `sheet-music-door` (by action: `[data-a="sgAddPdf"]`)
- `edit-button` (by action: `[data-a="sgListEdit"]`)
- `new-song-button` (by action: `[data-a="sgNew"]`)
- `song-row` (by action: `[data-a="sgOpen"]`)
- `play-button` (by action: `[data-a="sgRowPlay"]`)
- `save-button` (by action: `[data-a="sgSave"]`)
- `song-search-field` (by action: `[data-a="sgSearch"]`)
- `sort-menu` (by action: `[data-a="sgSortMenu"]`)
- `share-button` (by action: `[data-a="shareTake"]`)
- `history-row` (by action: `[data-a="sheet"][data-v="bkLog"]`)
- `delete-all-button` (by action: `[data-a="sheet"][data-v="clearRec"]`)
- `remove-prints-row` (by action: `[data-a="sheet"][data-v="melPrintsDel"]`)
- `reset-all-row` (by action: `[data-a="sheet"][data-v="resetAll"]`)
- `reset-month-row` (by action: `[data-a="sheet"][data-v="resetMonth"]`)
- `recordings-row` (by action: `[data-a="sheet"][data-v="storage"]`)
- `skip-button` (by action: `[data-a="skipHow"]`)
- `song-row` (by action: `[data-a="song"]`)
- `song-practice-card` (by action: `[data-a="songStart"]`)
- `start-session-button` (by action: `[data-a="start"]`)
- `review-takes-row` (by action: `[data-a="tkReview"]`)
- `level-picker` (by action: `[data-a="trkLevel"]`)
- `session-row` (by action: `[data-a="calSession"]`)
- `time-split-option` (by action: `[data-a="esplit"]`)
- `exercise-note-button` (by action: `[data-a="exNote"]`)
- `clear-notes-button` (by action: `[data-a="xnClear"]`)
- `done-button` (by action: `[data-a="flowDone"]`)
- `keep-time-button` (by action: `[data-a="awayKeep"]`)
- `take-time-out-button` (by action: `[data-a="awayOut"]`)
- `done-button` (by action: `[data-a="sckDone"]`)
- `fix-time-row` (by action: `[data-a="sckFix"]`)
- `save-time-button` (by action: `[data-a="sckFixSave"]`)
- `delete-song-practice-button` (by action: `[data-a="sheet"][data-v="delSongSess"]`)
- `restart-ladder-button` (by action: `[data-a="apLadAgain"]`)
- `song-summary-row` (by action: `[data-a="apReopen"]`)
- `section-pill` (by action: `[data-a="apSec"]`)
- `change-section-button` (by action: `[data-a="apSecs"]`)
- `cue-chip` (by action: `[data-a="rcue"]`)
- `own-cue-chip` (by action: `[data-a="rown"]`)
- `coach-video-row` (by action: `[data-a="openCoach"]`)
- `video-exercise-row` (by action: `[data-a="coachEx"]`)
- `full-screen-button` (by action: `[data-a="coachFS"]`)
- `loop-button` (by action: `[data-a="coachLoop"]`)
- `level-button` (by action: `[data-a="coachLv"]`)
- `play-button` (by action: `[data-a="coachPlay"]`)
- `speed-button` (by action: `[data-a="coachSpeed"]`)
- `level-button` (by action: `[data-a="fwLv"]`)
- `open-player-button` (by action: `[data-a="fwOpen"]`)
- `play-button` (by action: `[data-a="fwToggle"]`)
- `video-tile` (by action: `[data-a="fwVTap"]`)
- `tucked-window-tab` (by action: `[data-a="fwTab"]`)
- `close-button` (by action: `[data-a="fwX"]`)
- `favourite-button` (by action: `[data-a="patFav"]`)
- `group-tab` (by action: `[data-a="patGroup"]`)
- `stay-on-key-button` (by action: `[data-a="patHold"]`)
- `sound-item` (by action: `[data-a="patMenuPick"]`)
- `pattern-tile` (by action: `[data-a="patPick"]`)
- `play-button` (by action: `[data-a="patPlay"]`)
- `speed-up-button` (by action: `[data-a="patRamp"]`)
- `sound-pill` (by action: `[data-a="patSound"]`)
- `speed-pill` (by action: `[data-a="patSpd"]`)
- `voice-range-button` (by action: `[data-a="patVoice"]`)
- `window-play-button` (by action: `[data-a="patWin"]`)
- `skip-back-button` (by action: `[data-a="coachSkip"][data-v="-10"]`)
- `skip-forward-button` (by action: `[data-a="coachSkip"][data-v="10"]`)
- `skip-back-button` (by action: `[data-a="fwSkip"][data-v="-10"]`)
- `skip-forward-button` (by action: `[data-a="fwSkip"][data-v="10"]`)
- `start-lower-button` (by action: `[data-a="patShift"][data-v="-1"]`)
- `start-higher-button` (by action: `[data-a="patShift"][data-v="1"]`)
- `slower-button` (by action: `[data-a="patSpdStep"][data-v="-1"]`)
- `faster-button` (by action: `[data-a="patSpdStep"][data-v="1"]`)
- `remove-video-button` (by action: `[data-a="sheet"][data-v="coachDel"]`)
- `edit-description-button` (by action: `[data-a="sheet"][data-v="editWhat"]`)
- `all-songs-row` (by action: `[data-a="sgAll"]`)
- `delete-selected-button` (by action: `[data-a="sgLDel"]`)
- `pin-selected-button` (by action: `[data-a="sgLPin"]`)
- `select-all-button` (by action: `[data-a="sgSelAll"]`)
- `done-button` (by action: `[data-a="sgListDone"]`)
- `clear-song-search-button` (by action: `[data-a="sgQClear"]`)
- `recent-song-search-row` (by action: `[data-a="sgRecent"]`)
- `remove-song-recent-button` (by action: `[data-a="sgRmRecent"]`)
- `clear-song-recents-button` (by action: `[data-a="sgClearRecent"]`)
- `delete-item` (by action: `[data-a="sgCtxDel"]`)
- `pin-item` (by action: `[data-a="sgCtxPin"]`)
- `rename-item` (by action: `[data-a="sgCtxRename"]`)
- `order-item` (by action: `[data-a="sgOrder"]`)
- `sort-item` (by action: `[data-a="sgSetSort"]`)
- `swap-pin-button` (by action: `[data-a="sgSwapPin"]`)
- `confirm-delete-button` (by action: `[data-a="sgDoDel"]`)
- `add-mode-tab` (by action: `[data-a="sgAddMode"]`)
- `choose-file-button` (by action: `[data-a="sgAddPick"]`)
- `song-length-button` (by action: `[data-a="sgAddLen"]`)
- `relink-button` (by action: `[data-a="sgAddRelink"]`)
- `next-step-button` (by action: `[data-a="sgSplit"]`)
- `previous-step-button` (by action: `[data-a="sgBackStep"]`)
- `block-label-button` (by action: `[data-a="sgBlockLabel"]`)
- `label-option` (by action: `[data-a="sgPick"]`)
- `done-button` (by action: `[data-a="sgDone"]`)
- `edit-mode-tab` (by action: `[data-a="sgEditMode"]`)
- `undo-button` (by action: `[data-a="sgUndo"]`)
- `hint-level-button` (by action: `[data-a="sgHMenu"]`)
- `hint-item` (by action: `[data-a="sgSetHint"]`)
- `recall-options-button` (by action: `[data-a="sgRMenu"]`)
- `start-anywhere-item` (by action: `[data-a="sgAnywhere"]`)
- `label-button` (by action: `[data-a="sgLabel"]`)
- `cue-button` (by action: `[data-a="sgCue"]`)
- `save-cue-button` (by action: `[data-a="sgSaveCue"]`)
- `link-section-button` (by action: `[data-a="sgLink"]`)
- `unlink-button` (by action: `[data-a="sgUnlink"]`)
- `confirm-unlink-button` (by action: `[data-a="sgDoUnlink"]`)
- `move-section-button` (by action: `[data-a="sgOMove"]`)
- `remove-section-button` (by action: `[data-a="sgORemove"]`)
- `section-marks-button` (by action: `[data-a="sgMarks"]`)
- `section-takes-button` (by action: `[data-a="sgTakes"]`)
- `record-section-button` (by action: `[data-a="sgRec"]`)
- `stop-recording-button` (by action: `[data-a="sgStop"]`)
- `suggested-breath-button` (by action: `[data-a="sgSugBr"]`)
- `lyric-word` (by action: `[data-a="sgWord"]`)
- `key-help-button` (by action: `[data-a="gdKey"]`)
- `clear-selection-button` (by action: `[data-a="mkClear"]`)
- `keep-mark-button` (by action: `[data-a="mkKeep"]`)
- `mark-option` (by action: `[data-a="mkOpt"]`)
- `mark-type-option` (by action: `[data-a="mkPick"]`)
- `remove-mark-button` (by action: `[data-a="mkRm"]`)
- `add-text-button` (by action: `[data-a="mkText"]`)
- `more-hints-button` (by action: `[data-a="sgHint"][data-v="-1"]`)
- `fewer-hints-button` (by action: `[data-a="sgHint"][data-v="1"]`)
- `add-track-button` (by action: `[data-a="ckAddTrack"]`)
- `done-button` (by action: `[data-a="ckCheckDone"]`)
- `flag-button` (by action: `[data-a="ckFlag"]`)
- `done-button` (by action: `[data-a="ckHeadDone"]`)
- `lyrics-tab` (by action: `[data-a="ckHeadLyrics"]`)
- `marks-tab` (by action: `[data-a="ckHeadMarks"]`)
- `lyric-line` (by action: `[data-a="ckLine"]`)
- `annotate-item` (by action: `[data-a="ckLmMark"]`)
- `play-from-here-item` (by action: `[data-a="ckLmPlay"]`)
- `retime-line-item` (by action: `[data-a="ckLmRetime"]`)
- `mute-button` (by action: `[data-a="ckMute"]`)
- `play-button` (by action: `[data-a="ckPP"]`)
- `set-length-button` (by action: `[data-a="ckPickSet"]`)
- `relink-button` (by action: `[data-a="ckRelink"]`)
- `retime-section-button` (by action: `[data-a="ckRetime"]`)
- `retime-line-button` (by action: `[data-a="ckRetimeNow"]`)
- `nudge-earlier-button` (by action: `[data-a="ckNudge"][data-v="-0.2"]`)
- `nudge-later-button` (by action: `[data-a="ckNudge"][data-v="0.2"]`)
- `marker-chip` (by action: `[data-a="trkChip"]`)
- `chip-loop-button` (by action: `[data-a="trkChipLoop"]`)
- `end-here-button` (by action: `[data-a="trkEndHere"]`)
- `line-start-button` (by action: `[data-a="trkLnStart"]`)
- `line-end-button` (by action: `[data-a="trkLnEnd"]`)
- `deselect-line-button` (by action: `[data-a="trkLnX"]`)
- `loop-button` (by action: `[data-a="trkMdLoop"]`)
- `track-lyric-line` (by action: `[data-a="trkLyr"]`)
- `save-button` (by action: `[data-a="trkMkSaveName"]`)
- `section-start-row` (by action: `[data-a="trkMkSec"]`)
- `section-option` (by action: `[data-a="trkMkSecPick"]`)
- `next-marker-button` (by action: `[data-a="trkNext"]`)
- `keep-markers-button` (by action: `[data-a="trkPastKeep"]`)
- `trim-button` (by action: `[data-a="trkPastTrim"]`)
- `replay-marker-button` (by action: `[data-a="trkReplay"]`)
- `track-lyric-row` (by action: `[data-a="trkRow"]`)
- `sound-button` (by action: `[data-a="trkSnd"]`)
- `lyrics-button` (by action: `[data-a="trkSongLyrics"]`)
- `marker-tile` (by action: `[data-a="trkTile"]`)
- `tile-loop-button` (by action: `[data-a="trkTileLoop"]`)
- `import-anyway-button` (by action: `[data-a="trkBigYes"]`)
- `clear-markers-button` (by action: `[data-a="sheet"][data-v="trkMkClear"]`)
- `delete-comment-button` (by action: `[data-a="tkCDel"]`)
- `edit-comment-button` (by action: `[data-a="tkCEdit"]`)
- `comment-chip` (by action: `[data-a="tkCJump"]`)
- `collapse-button` (by action: `[data-a="tkCollapse"]`)
- `fold-button` (by action: `[data-a="tkFold"]`)
- `rename-take-button` (by action: `[data-a="tkMenuRename"]`)
- `clear-name-button` (by action: `[data-a="tkNameClear"]`)
- `done-button` (by action: `[data-a="tkNameDone"]`)
- `nudge-button` (by action: `[data-a="tkNudge"]`)
- `post-comment-button` (by action: `[data-a="tkPost"]`)
- `rename-take-button` (by action: `[data-a="tkRename"]`)
- `timestamp-chip` (by action: `[data-a="tkStamp"]`)
- `takes-tab` (by action: `[data-a="tkTab"]`)
- `skip-back-button` (by action: `[data-a="tkSkip"][data-v="-5"]`)
- `skip-forward-button` (by action: `[data-a="tkSkip"][data-v="5"]`)
- `show-all-button` (by action: `[data-a="melAll"]`)
- `octave-option` (by action: `[data-a="melOct"]`)
- `score-bar` (by action: `[data-a="mpBar"]`)
- `note-dot` (by action: `[data-a="mpDot"]`)
- `change-loop-button` (by action: `[data-a="mpPick"]`)
- `cancel-loop-button` (by action: `[data-a="mpPickX"]`)
- `view-option` (by action: `[data-a="mpView"]`)
- `slower-button` (by action: `[data-a="melTempo"][data-v="-1"]`)
- `faster-button` (by action: `[data-a="melTempo"][data-v="1"]`)
- `slower-button` (by action: `[data-a="mpSpd"][data-v="-1"]`)
- `faster-button` (by action: `[data-a="mpSpd"][data-v="1"]`)
- `fewer-bars-button` (by action: `[data-a="mpZoom"][data-v="-1"]`)
- `more-bars-button` (by action: `[data-a="mpZoom"][data-v="1"]`)
- `sheet-music-orphan-row` (by action: `[data-a="sheet"][data-v="melOrphanDel"]`)
- `clear-search-button` (by action: `[data-a="findClear"]`)
- `clear-recents-button` (by action: `[data-a="findClearRecent"]`)
- `lyric-result-row` (by action: `[data-a="findLyr"]`)
- `more-results-button` (by action: `[data-a="findMore"]`)
- `recent-search-row` (by action: `[data-a="findRecent"]`)
- `remove-recent-button` (by action: `[data-a="findRmRecent"]`)
- `take-result-row` (by action: `[data-a="findTake"]`)
- `set-up-folder-button` (by action: `[data-a="bkGuideFrom"]`)
- `restore-this-backup-button` (by action: `[data-a="bkToImport"]`)
- `exclude-recordings-switch` (by action: `[data-a="exportNoRec"]`)
- `save-backup-button` (by action: `[data-a="exportSave"]`)
- `restore-button` (by action: `[data-a="importYes"]`)
- `undo-restore-button` (by action: `[data-a="undoYes"]`)
- `save-copy-button` (by action: `[data-a="rescueSave"]`)
- `delete-everything-button` (by action: `[data-a="resetAll"]`)
- `show-in-timeline-button` (by action: `[data-a="lgjump"]`)
- `version-dot` (by action: `[data-a="lgpick"]`)
- `view-tab` (by action: `[data-a="logMode"]`)
- `show-more-button` (by action: `[data-a="logMore"]`)
- `try-again-button` (by action: `[data-a="logRetry"]`)
- `delete-copy-button` (by action: `[data-a="sheet"][data-v="rescueDel"]`)
- `undo-restore-row` (by action: `[data-a="sheet"][data-v="undoRestore"]`)
- `VS-004 › stop-button`
- `VS-004 › compare-button`
- `VS-004 › done-button`
- `VS-004 › sung-rungs-row`
- `VS-004 › skip-rung-button`
- `VS-004 › live-pitch-line`
- `VS-004 › line-switch`
- `VS-004 › hear-both-button`
- `VS-004 › note-button`
- `VS-004 › repeat-button`
- `VS-004 › scale-lanes-chip`
- `VS-004 › key-choice-button`
- `VS-004 › key-change-button`
- `VS-004 › practise-play-button`
- `VS-004 › practise-pattern-row`
- `VS-009 › controls-button`
- `VS-014 › bridge-line`
- `VS-014 › listen-switch`
- `VS-017 › cancel-button`
- `VS-020 › remove-prints-row`
- `VS-040 › save-button`
- `VS-048 › done-button`
- `VS-048 › share-button`
- `VS-048 › delete-button`
- `VS-051 › save-button`
- `VS-051 › sheet-music-door`
- `VS-056 › confirm-button`
- `VS-056 › cancel-button`
- `VS-092 › pause-button`
- `VS-092 › main-button`
- `VS-092 › times`
- `VS-095 › close-button`
- `VS-095 › learn-more-button`
- `VS-096 › done-button`
- `VS-096 › from-stepper`
- `VS-096 › to-stepper`
- `VS-096 › use-button`
- `VS-097 › pattern-card`
- `VS-097 › pattern-pill`
- `VS-097 › start-note-stepper`
- `VS-097 › stay-on-key-button`
- `VS-097 › play-button`
- `VS-099 › octave-picker`
- `VS-099 › tempo-field`
- `VS-099 › key-row`
- `VS-099 › replace-row`
- `VS-100 › octave-picker`
- `VS-100 › tempo-field`
- `VS-100 › save-button`
- `VS-100 › cancel-button`
- `VS-102 › this-song-button`
- `VS-102 › new-song-button`
- `VS-106 › cancel-button`
- `VS-108 › sheet-settings-button`
- `VS-108 › view-picker`
- `VS-108 › speed-stepper`
- `VS-108 › bars-stepper`
- `VS-108 › loop-strip`
- `VS-108 › dots-view`
- `VS-108 › sheet-view`
- `VS-108 › my-note-button`
- `VS-108 › play-button`
- `VS-108 › loop-button`

</details>
