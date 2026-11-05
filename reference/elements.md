# Element sheet · Vocal Sessions

Every named part in the app: its name, where it is named, how the app finds it, the parts kit part it is and its status. Written by `tools/reference/elements.py` from `js/register.js`; don't edit by hand. Values (sizes, springs, corners) come later. The naming rules: [MAINTAINING › Screen IDs › Naming rules](../MAINTAINING.md#naming-rules).

A note points at a part as `VS-009 › song-row`; a shared or by-action part is named the same on every screen it shows on.

**35 shared parts, 377 names by action, 207 parts named on their screens.**

## Shared

Named wherever they show: the tab bar, Back, Close, the standard roles, fields and links.

| Name | Found by | Kit part | Status |
|---|---|---|---|
| `today-tab` | `[data-a="tab"][data-v="today"]` |  | In use |
| `progress-tab` | `[data-a="tab"][data-v="history"]` |  | In use |
| `songs-tab` | `[data-a="tab"][data-v="songs"]` |  | In use |
| `exercises-tab` | `[data-a="tab"][data-v="exercises"]` |  | In use |
| `search-button` | `[data-a="findOpen"]` |  | In use |
| `settings-button` | `[data-a="openSettings"]` |  | In use |
| `back-button` | `#barL button[aria-label^="Back"], [data-a="allBack"], [data-a="ckCheckBack"], [data-a="coachBack"], [data-a="exBack"], [data-a="gdBack"], [data-a="keyBack"], [data-a="logBack"], [data-a="mpBack"], [data-a="patBack"], [data-a="setBack"], [data-a="setPgBack"], [data-a="sgBack"], [data-a="trkBack"]` |  | In use |
| `close-button` | `.shbtn[data-a="close"], .pk-sheet-close` | `pk-sheet-close` | In use |
| `done-button` | `[data-a="close"][data-v="done"]` |  | In use |
| `cancel-button` | `[data-a="close"][data-v="cancel"], .pk-alert-btn[data-a="no"], .pk-action.pk-cancel` | `pk-action`, `pk-alert-btn`, `pk-cancel` | In use |
| `confirm-button` | `.pk-alert-btn[data-a="yes"]` | `pk-alert-btn` | In use |
| `grabber` | `.pk-grabber` | `pk-grabber` | In use |
| `undo-button` | `.pk-toast-undo` | `pk-toast-undo` | In use |
| `search-field` | `#fq` |  | In use |
| `song-search-field` | `#sgqi` |  | In use |
| `note-field` | `.notebox .field` |  | In use |
| `minutes-field` | `#longMins, #edMins` |  | In use |
| `date-field` | `#edDate` |  | In use |
| `foundation-minutes-field` | `#edF` |  | In use |
| `rotation-minutes-field` | `#edR` |  | In use |
| `word-field` | `#wordIn` |  | In use |
| `song-field` | `#songIn` |  | In use |
| `exercise-name-field` | `#exName` |  | In use |
| `description-field` | `#exWhat, #whatIn` |  | In use |
| `title-field` | `#sgRenIn, #sgTitle, #ckTitle` |  | In use |
| `artist-field` | `#sgRenArt, #sgArtist, #ckArtist` |  | In use |
| `lyrics-field` | `#sgLyr` |  | In use |
| `cue-field` | `#sgCueIn` |  | In use |
| `mark-text-field` | `#mkIn` |  | In use |
| `take-name-field` | `#tkNameIn` |  | In use |
| `comment-field` | `#tkCIn` |  | In use |
| `marker-name-field` | `#trkMkIn` |  | In use |
| `tempo-field` | `#melTempoIn` |  | In use |
| `coach-video-link` | `#coachVideoLink` |  | In use |
| `github-link` | `#githubLink` |  | In use |

## By action

Wherever the action shows, its button gets this name. A screen's own parts and the shared ones win over these.


### already named on a screen (Q36 to Q47): the same name wherever else the action shows

| Name | Found by | Status |
|---|---|---|
| `compare-button` | `[data-a="apCmp"]` | In use |
| `done-button` | `[data-a="apDone"]` | In use |
| `hear-both-button` | `[data-a="apHear"]` | In use |
| `sung-rungs-row` | `[data-a="apLadFold"]` | In use |
| `line-switch` | `[data-a="apLine"]` | In use |
| `ladder-switch` | `[data-a="apMode"]` | In use |
| `not-recorded-button` | `[data-a="apNoRec"]` | In use |
| `note-button` | `[data-a="apNote"]` | In use |
| `repeat-button` | `[data-a="apRpt"]` | In use |
| `sing-button` | `[data-a="apSing"]` | In use |
| `skip-rung-button` | `[data-a="apSkip"]` | In use |
| `song-row` | `[data-a="apSong"]` | In use |
| `songs-sort` | `[data-a="apSort"]` | In use |
| `stop-button` | `[data-a="apStop"]` | In use |
| `by-feel-button` | `[data-a="bfFeel"]` | In use |
| `start-button` | `[data-a="bfStart"]` | In use |
| `to-stepper` | `[data-a="bfStep"][data-v="hi"]` | In use |
| `from-stepper` | `[data-a="bfStep"][data-v="lo"]` | In use |
| `done-button` | `[data-a="bfStop"]` | In use |
| `use-button` | `[data-a="bfUse"]` | In use |
| `check-row` | `[data-a="checkPick"]` | In use |
| `controls-button` | `[data-a="ckGrid"]` | In use |
| `edit-button` | `[data-a="ckGridEdit"]` | In use |
| `control-tile` | `[data-a="ckTile"]` | In use |
| `clock-pill` | `[data-a="clock"]` | In use |
| `add-video-row` | `[data-a="coachAdd"]` | In use |
| `coach-video-row` | `[data-a="coachSettings"]` | In use |
| `level-button` | `[data-a="exLevel"]` | In use |
| `more-button` | `[data-a="exMore"]` | In use |
| `back-up-button` | `[data-a="exportPrep"]` | In use |
| `page-picker` | `[data-a="exTab"]` | In use |
| `cancel-button` | `[data-a="findCancel"]` | In use |
| `close-search-button` | `[data-a="findClose"]` | In use |
| `finish-here-button` | `[data-a="finHere"]` | In use |
| `step-summary` | `[data-a="flowOpen"]` | In use |
| `guide-row` | `[data-a="gdOpen"]` | In use |
| `close-button` | `[data-a="gdPeekClose"]` | In use |
| `learn-more-button` | `[data-a="gdPeekMore"]` | In use |
| `week-goal` | `[data-a="goalOpen"]` | In use |
| `list-picker` | `[data-a="histTab"]` | In use |
| `import-row` | `[data-a="importPick"]` | In use |
| `practise-pattern-row` | `[data-a="keyGo"]` | In use |
| `practise-play-button` | `[data-a="keyHear"]` | In use |
| `scale-lanes-chip` | `[data-a="keyLanes"]` | In use |
| `note-button` | `[data-a="keyNote"]` | In use |
| `use-button` | `[data-a="keySave"]` | In use |
| `key-choice-button` | `[data-a="keyUse"]` | In use |
| `whole-time-button` | `[data-a="longAll"]` | In use |
| `continue-button` | `[data-a="longOk"]` | In use |
| `cancel-button` | `[data-a="melCancel"]` | In use |
| `cancel-button` | `[data-a="melDrop"]` | In use |
| `sheet-settings-button` | `[data-a="melInfo"]` | In use |
| `key-row` | `[data-a="melKey"]` | In use |
| `replace-row` | `[data-a="melReplaceAsk"]` | In use |
| `add-anyway-button` | `[data-a="melSameGo"]` | In use |
| `open-button` | `[data-a="melSameOpen"]` | In use |
| `save-button` | `[data-a="melSave"]` | In use |
| `this-song-button` | `[data-a="melTitleHere"]` | In use |
| `new-song-button` | `[data-a="melTitleNew"]` | In use |
| `loop-button` | `[data-a="mpLoop"]` | In use |
| `my-note-button` | `[data-a="mpMy"]` | In use |
| `play-button` | `[data-a="mpPP"]` | In use |
| `show-all-row` | `[data-a="openAll"]` | In use |
| `date-line` | `[data-a="openCal"]` | In use |
| `exercise-row` | `[data-a="openEx"]` | In use |
| `changelog-row` | `[data-a="openLog"]` | In use |
| `bridge-cue-switch` | `[data-a="patBCue"]` | In use |
| `bridge-row` | `[data-a="patBridge"]` | In use |
| `chord-switch` | `[data-a="patCue"]` | In use |
| `drone-switch` | `[data-a="patDrone"]` | In use |
| `listen-switch` | `[data-a="patListen"]` | In use |
| `pattern-pill` | `[data-a="patOpen"]` | In use |
| `sound-row` | `[data-a="patSoundPick"]` | In use |
| `stop-past-last-switch` | `[data-a="patStopLast"]` | In use |
| `stop-at-top-switch` | `[data-a="patStopTop"]` | In use |
| `voice-type-row` | `[data-a="patVoiceType"]` | In use |
| `pause-button` | `[data-a="pauseToggle"]` | In use |
| `peek-length-picker` | `[data-a="peekLen"]` | In use |
| `earlier-button` | `[data-a="pnav"]` | In use |
| `range-picker` | `[data-a="prange"]` | In use |
| `record-button` | `[data-a="rec"]` | In use |
| `resume-session-button` | `[data-a="resume"]` | In use |
| `exercise-row` | `[data-a="ring"]` | In use |
| `more-exercises-sort` | `[data-a="rSort"]` | In use |
| `done-button` | `[data-a="savedDone"]` | In use |
| `save-button` | `[data-a="saveEdit"]` | In use |
| `add-button` | `[data-a="saveEx"]` | In use |
| `save-button` | `[data-a="saveHow"]` | In use |
| `read-me-row` | `[data-a="saveReadme"]` | In use |
| `add-button` | `[data-a="saveSong"]` | In use |
| `save-button` | `[data-a="saveWhat"]` | In use |
| `add-button` | `[data-a="saveWord"]` | In use |
| `main-button` | `[data-a="sckMain"]` | In use |
| `times` | `[data-a="sckSwap"]` | In use |
| `gradient-switch` | `[data-a="setGrad"]` | In use |
| `screen-ids-switch` | `[data-a="setIds"]` | In use |
| `settings-row` | `[data-a="setPg"]` | In use |
| `reduce-motion-picker` | `[data-a="setReduce"]` | In use |
| `slow-motion-switch` | `[data-a="setSlow"]` | In use |
| `reduce-transparency-switch` | `[data-a="setTransp"]` | In use |
| `add-lyrics-button` | `[data-a="sgAddLyrics"]` | In use |
| `sheet-music-door` | `[data-a="sgAddPdf"]` | In use |
| `edit-button` | `[data-a="sgListEdit"]` | In use |
| `new-song-button` | `[data-a="sgNew"]` | In use |
| `song-row` | `[data-a="sgOpen"]` | In use |
| `song-practice-row` | `[data-a="sgPractise"]` | In use |
| `play-button` | `[data-a="sgRowPlay"]` | In use |
| `save-button` | `[data-a="sgSave"]` | In use |
| `song-search-field` | `[data-a="sgSearch"]` | In use |
| `sort-menu` | `[data-a="sgSortMenu"]` | In use |
| `share-button` | `[data-a="shareTake"]` | In use |
| `add-exercise-row` | `[data-a="sheet"][data-v="addEx"]` | In use |
| `history-row` | `[data-a="sheet"][data-v="bkLog"]` | In use |
| `delete-all-button` | `[data-a="sheet"][data-v="clearRec"]` | In use |
| `delete-button` | `[data-a="sheet"][data-v="delTake"]` | In use |
| `discard-session-button` | `[data-a="sheet"][data-v="discard"]` | In use |
| `remove-prints-row` | `[data-a="sheet"][data-v="melPrintsDel"]` | In use |
| `reset-all-row` | `[data-a="sheet"][data-v="resetAll"]` | In use |
| `reset-month-row` | `[data-a="sheet"][data-v="resetMonth"]` | In use |
| `recordings-row` | `[data-a="sheet"][data-v="storage"]` | In use |
| `skip-button` | `[data-a="skipHow"]` | In use |
| `song-row` | `[data-a="song"]` | In use |
| `song-practice-card` | `[data-a="songStart"]` | In use |
| `start-session-button` | `[data-a="start"]` | In use |
| `takes-button` | `[data-a="tkOpenAll"]` | In use |
| `review-takes-row` | `[data-a="tkReview"]` | In use |
| `add-track-button` | `[data-a="trkAdd"]` | In use |
| `level-picker` | `[data-a="trkLevel"]` | In use |

### Q48 options shown on one screen and named there by their group only

| Name | Found by | Status |
|---|---|---|
| `ending-option` | `[data-a="patEnding"]` | In use |
| `notes-option` | `[data-a="patNotes"]` | In use |
| `vowel-option` | `[data-a="patVowel"]` | In use |
| `delete-exercise-button` | `[data-a="sheet"][data-v="delEx"]` | In use |

### Today, sessions and Progress

| Name | Found by | Status |
|---|---|---|
| `edit-session-button` | `[data-a="editSess"]` | In use |
| `session-row` | `[data-a="calSession"]` | In use |
| `day-tile` | `[data-a="calDay"]` | In use |
| `time-split-option` | `[data-a="esplit"]` | In use |
| `exercise-note-button` | `[data-a="exNote"]` | In use |
| `add-note-button` | `[data-a="openNote"]` | In use |
| `add-word-button` | `[data-a="addWord"]` | In use |
| `word-chip` | `[data-a="wTog"]` | In use |
| `clear-notes-button` | `[data-a="xnClear"]` | In use |
| `focus-chip` | `[data-a="focus"]` | In use |
| `done-button` | `[data-a="flowDone"]` | In use |
| `keep-time-button` | `[data-a="awayKeep"]` | In use |
| `take-time-out-button` | `[data-a="awayOut"]` | In use |
| `done-button` | `[data-a="sckDone"]` | In use |
| `fix-time-row` | `[data-a="sckFix"]` | In use |
| `save-time-button` | `[data-a="sckFixSave"]` | In use |
| `previous-month-button` | `[data-a="calMove"][data-v="-1"]` | In use |
| `next-month-button` | `[data-a="calMove"][data-v="1"]` | In use |
| `delete-session-button` | `[data-a="sheet"][data-v="delSession"]` | In use |
| `delete-song-practice-button` | `[data-a="sheet"][data-v="delSongSess"]` | In use |

### Application and takes

| Name | Found by | Status |
|---|---|---|
| `restart-ladder-button` | `[data-a="apLadAgain"]` | In use |
| `record-over-track-switch` | `[data-a="apOver"]` | In use |
| `song-summary-row` | `[data-a="apReopen"]` | In use |
| `section-pill` | `[data-a="apSec"]` | In use |
| `change-section-button` | `[data-a="apSecs"]` | In use |
| `play-take-button` | `[data-a="playTake"]` | In use |
| `star-button` | `[data-a="star"]` | In use |
| `take-note-button` | `[data-a="takeNote"]` | In use |
| `cue-chip` | `[data-a="rcue"]` | In use |
| `own-cue-chip` | `[data-a="rown"]` | In use |
| `add-song-button` | `[data-a="sheet"][data-v="addSong"]` | In use |
| `headphones-button` | `[data-a="recOver"][data-v="hp"]` | In use |
| `speaker-button` | `[data-a="recOver"][data-v="spk"]` | In use |

### Exercises, the pattern player and the coach video

| Name | Found by | Status |
|---|---|---|
| `coach-video-row` | `[data-a="openCoach"]` | In use |
| `video-exercise-row` | `[data-a="coachEx"]` | In use |
| `full-screen-button` | `[data-a="coachFS"]` | In use |
| `loop-button` | `[data-a="coachLoop"]` | In use |
| `level-button` | `[data-a="coachLv"]` | In use |
| `play-button` | `[data-a="coachPlay"]` | In use |
| `speed-button` | `[data-a="coachSpeed"]` | In use |
| `level-button` | `[data-a="fwLv"]` | In use |
| `open-player-button` | `[data-a="fwOpen"]` | In use |
| `play-button` | `[data-a="fwToggle"]` | In use |
| `video-tile` | `[data-a="fwVTap"]` | In use |
| `tucked-window-tab` | `[data-a="fwTab"]` | In use |
| `close-button` | `[data-a="fwX"]` | In use |
| `favourite-button` | `[data-a="patFav"]` | In use |
| `group-tab` | `[data-a="patGroup"]` | In use |
| `stay-on-key-button` | `[data-a="patHold"]` | In use |
| `sound-item` | `[data-a="patMenuPick"]` | In use |
| `range-nudge-button` | `[data-a="patNudge"]` | In use |
| `pattern-tile` | `[data-a="patPick"]` | In use |
| `play-button` | `[data-a="patPlay"]` | In use |
| `speed-up-button` | `[data-a="patRamp"]` | In use |
| `sound-pill` | `[data-a="patSound"]` | In use |
| `speed-pill` | `[data-a="patSpd"]` | In use |
| `voice-range-button` | `[data-a="patVoice"]` | In use |
| `window-play-button` | `[data-a="patWin"]` | In use |
| `skip-back-button` | `[data-a="coachSkip"][data-v="-10"]` | In use |
| `skip-forward-button` | `[data-a="coachSkip"][data-v="10"]` | In use |
| `skip-back-button` | `[data-a="fwSkip"][data-v="-10"]` | In use |
| `skip-forward-button` | `[data-a="fwSkip"][data-v="10"]` | In use |
| `start-lower-button` | `[data-a="patShift"][data-v="-1"]` | In use |
| `start-higher-button` | `[data-a="patShift"][data-v="1"]` | In use |
| `slower-button` | `[data-a="patSpdStep"][data-v="-1"]` | In use |
| `faster-button` | `[data-a="patSpdStep"][data-v="1"]` | In use |
| `remove-video-button` | `[data-a="sheet"][data-v="coachDel"]` | In use |
| `edit-description-button` | `[data-a="sheet"][data-v="editWhat"]` | In use |

### Songs: the list, search and adding a song

| Name | Found by | Status |
|---|---|---|
| `all-songs-row` | `[data-a="sgAll"]` | In use |
| `swipe-delete-button` | `[data-a="sgDelRow"]` | In use |
| `swipe-pin-button` | `[data-a="sgPinRow"]` | In use |
| `delete-selected-button` | `[data-a="sgLDel"]` | In use |
| `pin-selected-button` | `[data-a="sgLPin"]` | In use |
| `select-all-button` | `[data-a="sgSelAll"]` | In use |
| `done-button` | `[data-a="sgListDone"]` | In use |
| `cancel-button` | `[data-a="sgQCancel"]` | Retired · 3.64 |
| `clear-song-search-button` | `[data-a="sgQClear"]` | In use |
| `recent-song-search-row` | `[data-a="sgRecent"]` | In use |
| `remove-song-recent-button` | `[data-a="sgRmRecent"]` | In use |
| `clear-song-recents-button` | `[data-a="sgClearRecent"]` | In use |
| `delete-item` | `[data-a="sgCtxDel"]` | In use |
| `pin-item` | `[data-a="sgCtxPin"]` | In use |
| `rename-item` | `[data-a="sgCtxRename"]` | In use |
| `order-item` | `[data-a="sgOrder"]` | In use |
| `sort-item` | `[data-a="sgSetSort"]` | In use |
| `swap-pin-button` | `[data-a="sgSwapPin"]` | In use |
| `save-button` | `[data-a="sgSaveRename"]` | In use |
| `confirm-delete-button` | `[data-a="sgDoDel"]` | In use |
| `add-mode-tab` | `[data-a="sgAddMode"]` | In use |
| `choose-file-button` | `[data-a="sgAddPick"]` | In use |
| `song-length-button` | `[data-a="sgAddLen"]` | In use |
| `relink-button` | `[data-a="sgAddRelink"]` | In use |
| `next-step-button` | `[data-a="sgSplit"]` | In use |
| `previous-step-button` | `[data-a="sgBackStep"]` | In use |
| `block-label-button` | `[data-a="sgBlockLabel"]` | In use |
| `label-option` | `[data-a="sgPick"]` | In use |

### Songs: the song page and marks

| Name | Found by | Status |
|---|---|---|
| `done-button` | `[data-a="sgDone"]` | In use |
| `edit-mode-tab` | `[data-a="sgEditMode"]` | In use |
| `undo-button` | `[data-a="sgUndo"]` | In use |
| `mode-tab` | `[data-a="sgMode"]` | In use |
| `hint-level-button` | `[data-a="sgHMenu"]` | In use |
| `hint-item` | `[data-a="sgSetHint"]` | In use |
| `recall-options-button` | `[data-a="sgRMenu"]` | In use |
| `start-anywhere-item` | `[data-a="sgAnywhere"]` | In use |
| `section-row` | `[data-a="sgSec"]` | In use |
| `label-button` | `[data-a="sgLabel"]` | In use |
| `cue-button` | `[data-a="sgCue"]` | In use |
| `save-cue-button` | `[data-a="sgSaveCue"]` | In use |
| `link-section-button` | `[data-a="sgLink"]` | In use |
| `unlink-button` | `[data-a="sgUnlink"]` | In use |
| `confirm-unlink-button` | `[data-a="sgDoUnlink"]` | In use |
| `relink-length-button` | `[data-a="sgLenRelinkYes"]` | In use |
| `move-section-button` | `[data-a="sgOMove"]` | In use |
| `remove-section-button` | `[data-a="sgORemove"]` | In use |
| `section-marks-button` | `[data-a="sgMarks"]` | In use |
| `section-takes-button` | `[data-a="sgTakes"]` | In use |
| `record-section-button` | `[data-a="sgRec"]` | In use |
| `stop-recording-button` | `[data-a="sgStop"]` | In use |
| `suggested-breath-button` | `[data-a="sgSugBr"]` | In use |
| `lyric-word` | `[data-a="sgWord"]` | In use |
| `edit-timing-button` | `[data-a="ckPencil"]` | In use |
| `key-help-button` | `[data-a="gdKey"]` | In use |
| `clear-selection-button` | `[data-a="mkClear"]` | In use |
| `keep-mark-button` | `[data-a="mkKeep"]` | In use |
| `layer-chip` | `[data-a="mkLayer"]` | In use |
| `mark-option` | `[data-a="mkOpt"]` | In use |
| `mark-type-option` | `[data-a="mkPick"]` | In use |
| `remove-mark-button` | `[data-a="mkRm"]` | In use |
| `add-text-button` | `[data-a="mkText"]` | In use |
| `marks-guide-row` | `[data-a="gdKeyRow"]` | In use |
| `more-hints-button` | `[data-a="sgHint"][data-v="-1"]` | In use |
| `fewer-hints-button` | `[data-a="sgHint"][data-v="1"]` | In use |

### Song Clock and Check timing

| Name | Found by | Status |
|---|---|---|
| `add-track-button` | `[data-a="ckAddTrack"]` | In use |
| `done-button` | `[data-a="ckCheckDone"]` | In use |
| `flag-button` | `[data-a="ckFlag"]` | In use |
| `done-button` | `[data-a="ckHeadDone"]` | In use |
| `lyrics-tab` | `[data-a="ckHeadLyrics"]` | In use |
| `marks-tab` | `[data-a="ckHeadMarks"]` | In use |
| `song-length-row` | `[data-a="ckLen"]` | In use |
| `lyric-line` | `[data-a="ckLine"]` | In use |
| `annotate-item` | `[data-a="ckLmMark"]` | In use |
| `play-from-here-item` | `[data-a="ckLmPlay"]` | In use |
| `retime-line-item` | `[data-a="ckLmRetime"]` | In use |
| `mute-button` | `[data-a="ckMute"]` | In use |
| `play-button` | `[data-a="ckPP"]` | In use |
| `set-length-button` | `[data-a="ckPickSet"]` | In use |
| `relink-button` | `[data-a="ckRelink"]` | In use |
| `retime-section-button` | `[data-a="ckRetime"]` | In use |
| `retime-line-button` | `[data-a="ckRetimeNow"]` | In use |
| `nudge-earlier-button` | `[data-a="ckNudge"][data-v="-0.2"]` | In use |
| `nudge-later-button` | `[data-a="ckNudge"][data-v="0.2"]` | In use |

### The track player and markers

| Name | Found by | Status |
|---|---|---|
| `play-button` | `[data-a="trkPP"]` | In use |
| `marker-chip` | `[data-a="trkChip"]` | In use |
| `chip-loop-button` | `[data-a="trkChipLoop"]` | In use |
| `end-here-button` | `[data-a="trkEndHere"]` | In use |
| `jog-side-option` | `[data-a="trkJogPos"]` | In use |
| `line-start-button` | `[data-a="trkLnStart"]` | In use |
| `line-end-button` | `[data-a="trkLnEnd"]` | In use |
| `deselect-line-button` | `[data-a="trkLnX"]` | In use |
| `loop-button` | `[data-a="trkLoop"]` | In use |
| `loop-button` | `[data-a="trkMdLoop"]` | In use |
| `track-lyric-line` | `[data-a="trkLyr"]` | In use |
| `track-settings-button` | `[data-a="trkMenu"]` | In use |
| `add-marker-button` | `[data-a="trkMkAdd"]` | In use |
| `save-button` | `[data-a="trkMkSaveName"]` | In use |
| `section-start-row` | `[data-a="trkMkSec"]` | In use |
| `section-option` | `[data-a="trkMkSecPick"]` | In use |
| `next-marker-button` | `[data-a="trkNext"]` | In use |
| `open-track-button` | `[data-a="trkOpen"]` | In use |
| `keep-markers-button` | `[data-a="trkPastKeep"]` | In use |
| `trim-button` | `[data-a="trkPastTrim"]` | In use |
| `replace-track-button` | `[data-a="trkReplace"]` | In use |
| `replay-marker-button` | `[data-a="trkReplay"]` | In use |
| `track-lyric-row` | `[data-a="trkRow"]` | In use |
| `sound-button` | `[data-a="trkSnd"]` | In use |
| `lyrics-button` | `[data-a="trkSongLyrics"]` | In use |
| `speed-pill` | `[data-a="trkSpeed"]` | In use |
| `marker-tile` | `[data-a="trkTile"]` | In use |
| `tile-loop-button` | `[data-a="trkTileLoop"]` | In use |
| `loop-start-button` | `[data-a="trkToStart"]` | In use |
| `import-anyway-button` | `[data-a="trkBigYes"]` | In use |
| `set-start-button` | `[data-a="trkSet"][data-v="start"]` | In use |
| `set-end-button` | `[data-a="trkSet"][data-v="end"]` | In use |
| `remove-track-button` | `[data-a="sheet"][data-v="trkDel"]` | In use |
| `clear-markers-button` | `[data-a="sheet"][data-v="trkMkClear"]` | In use |

### Takes on a song

| Name | Found by | Status |
|---|---|---|
| `delete-comment-button` | `[data-a="tkCDel"]` | In use |
| `edit-comment-button` | `[data-a="tkCEdit"]` | In use |
| `comment-chip` | `[data-a="tkCJump"]` | In use |
| `collapse-button` | `[data-a="tkCollapse"]` | In use |
| `delete-take-button` | `[data-a="tkDel"]` | In use |
| `fold-button` | `[data-a="tkFold"]` | In use |
| `rename-take-button` | `[data-a="tkMenuRename"]` | In use |
| `clear-name-button` | `[data-a="tkNameClear"]` | In use |
| `done-button` | `[data-a="tkNameDone"]` | In use |
| `nudge-button` | `[data-a="tkNudge"]` | In use |
| `play-take-button` | `[data-a="tkPlay"]` | In use |
| `post-comment-button` | `[data-a="tkPost"]` | In use |
| `rename-take-button` | `[data-a="tkRename"]` | In use |
| `delete-old-take-button` | `[data-a="tkRvDel"]` | In use |
| `timestamp-chip` | `[data-a="tkStamp"]` | In use |
| `star-button` | `[data-a="tkStar"]` | In use |
| `takes-tab` | `[data-a="tkTab"]` | In use |
| `take-row` | `[data-a="tkTap"]` | In use |
| `skip-back-button` | `[data-a="tkSkip"][data-v="-5"]` | In use |
| `skip-forward-button` | `[data-a="tkSkip"][data-v="5"]` | In use |

### Sheet music

| Name | Found by | Status |
|---|---|---|
| `show-all-button` | `[data-a="melAll"]` | In use |
| `octave-option` | `[data-a="melOct"]` | In use |
| `score-bar` | `[data-a="mpBar"]` | In use |
| `note-dot` | `[data-a="mpDot"]` | In use |
| `change-loop-button` | `[data-a="mpPick"]` | In use |
| `cancel-loop-button` | `[data-a="mpPickX"]` | In use |
| `view-option` | `[data-a="mpView"]` | In use |
| `slower-button` | `[data-a="melTempo"][data-v="-1"]` | In use |
| `faster-button` | `[data-a="melTempo"][data-v="1"]` | In use |
| `slower-button` | `[data-a="mpSpd"][data-v="-1"]` | In use |
| `faster-button` | `[data-a="mpSpd"][data-v="1"]` | In use |
| `fewer-bars-button` | `[data-a="mpZoom"][data-v="-1"]` | In use |
| `more-bars-button` | `[data-a="mpZoom"][data-v="1"]` | In use |
| `sheet-music-orphan-row` | `[data-a="sheet"][data-v="melOrphanDel"]` | In use |

### Search

| Name | Found by | Status |
|---|---|---|
| `clear-search-button` | `[data-a="findClear"]` | In use |
| `clear-recents-button` | `[data-a="findClearRecent"]` | In use |
| `lyric-result-row` | `[data-a="findLyr"]` | In use |
| `more-results-button` | `[data-a="findMore"]` | In use |
| `recent-search-row` | `[data-a="findRecent"]` | In use |
| `remove-recent-button` | `[data-a="findRmRecent"]` | In use |
| `take-result-row` | `[data-a="findTake"]` | In use |

### Settings, backups and the Changelog

| Name | Found by | Status |
|---|---|---|
| `set-up-folder-button` | `[data-a="bkGuideFrom"]` | In use |
| `restore-this-backup-button` | `[data-a="bkToImport"]` | In use |
| `exclude-recordings-switch` | `[data-a="exportNoRec"]` | In use |
| `save-backup-button` | `[data-a="exportSave"]` | In use |
| `restore-button` | `[data-a="importYes"]` | In use |
| `undo-restore-button` | `[data-a="undoYes"]` | In use |
| `ask-again-button` | `[data-a="persistAsk"]` | In use |
| `save-copy-button` | `[data-a="rescueSave"]` | In use |
| `delete-everything-button` | `[data-a="resetAll"]` | In use |
| `mode-option` | `[data-a="keyMode"]` | In use |
| `show-in-timeline-button` | `[data-a="lgjump"]` | In use |
| `version-dot` | `[data-a="lgpick"]` | In use |
| `view-tab` | `[data-a="logMode"]` | In use |
| `show-more-button` | `[data-a="logMore"]` | In use |
| `try-again-button` | `[data-a="logRetry"]` | In use |
| `backup-guide-row` | `[data-a="sheet"][data-v="bkGuide"]` | In use |
| `storage-protection-row` | `[data-a="sheet"][data-v="persist"]` | In use |
| `delete-copy-button` | `[data-a="sheet"][data-v="rescueDel"]` | In use |
| `undo-restore-row` | `[data-a="sheet"][data-v="undoRestore"]` | In use |

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

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `date-line` | `[data-a="openCal"]` |  | In use |  |
| `backup-nudge` | `[data-a="exportPrep"]` |  | In use |  |
| `week-goal` | `[data-a="goalOpen"]` |  | In use |  |
| `start-session-button` | `[data-a="start"]` |  | In use |  |
| `resume-session-button` | `[data-a="resume"]` |  | In use |  |
| `discard-session-button` | `[data-a="sheet"][data-v="discard"]` |  | In use |  |
| `rotation-row` | `[data-a="openEx"]` |  | In use |  |
| `song-practice-card` | `[data-a="songStart"]` |  | In use |  |

### VS-002 · Session · Foundation

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `step-button` | `#dock [data-a="cta"]` |  | In use |  |
| `clock-pill` | `[data-a="clock"]` |  | In use |  |
| `exercise-row` | `[data-a="ring"]` |  | In use |  |
| `more-exercises-sort` | `[data-a="rSort"]` |  | In use |  |
| `add-exercise-row` | `[data-a="sheet"][data-v="addEx"]` |  | In use |  |

### VS-003 · Session · Rotation

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `step-button` | `#dock [data-a="cta"]` |  | In use |  |
| `clock-pill` | `[data-a="clock"]` |  | In use |  |
| `finish-here-button` | `[data-a="finHere"]` |  | In use |  |
| `step-summary` | `[data-a="flowOpen"]` |  | In use |  |
| `exercise-row` | `[data-a="ring"]` |  | In use |  |

### VS-004 · Session · Application

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `step-button` | `#dock [data-a="cta"]` |  | In use |  |
| `clock-pill` | `[data-a="clock"]` |  | In use |  |
| `step-summary` | `[data-a="flowOpen"]` |  | In use |  |
| `carry-on-card` | `#apcard` |  | In use |  |
| `sing-button` | `[data-a="apSing"]` |  | In use |  |
| `stop-button` | `[data-a="apStop"]` |  | In use |  |
| `compare-button` | `[data-a="apCmp"]` |  | In use |  |
| `done-button` | `[data-a="apDone"]` |  | In use |  |
| `not-recorded-button` | `[data-a="apNoRec"]` |  | In use |  |
| `song-row` | `[data-a="apSong"]` |  | In use |  |
| `songs-sort` | `[data-a="apSort"]` |  | In use |  |
| `ladder-switch` | `[data-a="apMode"]` |  | In use |  |
| `sung-rungs-row` | `[data-a="apLadFold"]` |  | In use |  |
| `skip-rung-button` | `[data-a="apSkip"]` |  | In use |  |
| `live-pitch-line` | `#apLive` |  | In use |  |
| `line-switch` | `[data-a="apLine"]` |  | In use |  |
| `hear-both-button` | `[data-a="apHear"]` |  | In use |  |
| `note-button` | `[data-a="apNote"]` |  | In use |  |
| `repeat-button` | `[data-a="apRpt"]` |  | In use |  |
| `scale-lanes-chip` | `[data-a="keyLanes"]` |  | In use |  |
| `key-choice-button` | `[data-a="keyUse"]` |  | In use |  |
| `key-change-button` | `.keyblk [data-a="keyChange"]` |  | In use |  |
| `practise-play-button` | `[data-a="keyHear"]` |  | In use |  |
| `practise-pattern-row` | `[data-a="keyGo"]` |  | In use |  |

### VS-005 · Session saved

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `done-button` | `[data-a="savedDone"]` |  | In use |  |

### VS-006 · Progress

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `range-picker` | `[data-a="prange"]` |  | In use |  |
| `earlier-button` | `[data-a="pnav"]` |  | In use |  |
| `session-row` | `[data-a="sheet"][data-v="session"],[data-a="sheet"][data-v="songSession"]` |  | In use |  |
| `show-all-row` | `[data-a="openAll"]` |  | In use |  |

### VS-007 · All sessions

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `list-picker` | `[data-a="histTab"]` |  | In use |  |
| `session-row` | `[data-a="sheet"][data-v="session"],[data-a="sheet"][data-v="songSession"]` |  | In use |  |

### VS-008 · Songs

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `edit-button` | `[data-a="sgListEdit"]` |  | In use |  |
| `new-song-button` | `[data-a="sgNew"]` |  | In use |  |
| `song-search-field` | `[data-a="sgSearch"]` |  | In use | search-field |
| `close-search-button` | `.pk-search-close[data-a="findClose"]` | `pk-search-close` | In use |  |
| `sort-menu` | `[data-a="sgSortMenu"]` |  | In use |  |
| `song-row` | `[data-a="sgOpen"]` |  | In use |  |
| `play-button` | `[data-a="sgRowPlay"]` |  | In use |  |

### VS-009 · Song page

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `controls-button` | `[data-a="ckGrid"]` |  | In use |  |
| `takes-button` | `[data-a="tkOpenAll"]` |  | In use |  |
| `add-lyrics-button` | `[data-a="sgAddLyrics"]` |  | In use |  |
| `song-practice-row` | `[data-a="sgPractise"]` |  | In use |  |
| `add-track-row` | `[data-a="trkAdd"]` |  | In use |  |
| `sheet-music-row` | `[data-a="melAdd"], [data-a="melOpen"]` |  | In use |  |
| `key-row` | `.grp [data-a="keyChange"]` |  | In use |  |

### VS-010 · Track player

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `add-track-button` | `[data-a="trkAdd"]` |  | In use |  |
| `level-picker` | `[data-a="trkLevel"]` |  | In use |  |

### VS-012 · Song practice

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `save-button` | `#dock [data-a="cta"]` |  | In use |  |
| `song-row` | `[data-a="song"]` |  | In use |  |
| `record-button` | `[data-a="rec"]` |  | In use |  |

### VS-013 · Exercises

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `coach-video-row` | `[data-a="coachSettings"]` |  | In use |  |
| `exercise-row` | `[data-a="openEx"]` |  | In use |  |

### VS-014 · Exercise page

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `page-picker` | `[data-a="exTab"]` |  | In use |  |
| `level-button` | `[data-a="exLevel"]` |  | In use |  |
| `more-button` | `[data-a="exMore"]` |  | In use |  |
| `bridge-line` | `#pcBridge` |  | In use |  |
| `listen-switch` | `#pcListen` |  | In use |  |

### VS-015 · Coach video

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `coach-video-row` | `[data-a="coachSettings"]` |  | In use |  |

### VS-017 · Search

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `search-field` | `#fq` |  | In use |  |
| `cancel-button` | `[data-a="findCancel"]` |  | In use |  |
| `close-search-button` | `[data-a="findClose"]` |  | In use |  |

### VS-018 · Settings

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `settings-row` | `[data-a="setPg"]` |  | In use |  |
| `marks-guide-row` | `[data-a="gdOpen"]` |  | In use |  |
| `changelog-row` | `[data-a="openLog"]` |  | In use |  |
| `reset-month-row` | `[data-a="sheet"][data-v="resetMonth"]` |  | In use |  |
| `reset-all-row` | `[data-a="sheet"][data-v="resetAll"]` |  | In use |  |

### VS-019 · Settings › Backup

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `export-row` | `[data-a="exportPrep"]` |  | In use |  |
| `import-row` | `[data-a="importPick"]` |  | In use |  |
| `check-row` | `[data-a="checkPick"]` |  | In use |  |
| `history-row` | `[data-a="sheet"][data-v="bkLog"]` |  | In use |  |
| `read-me-row` | `[data-a="saveReadme"]` |  | In use |  |

### VS-020 · Settings › Storage

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `recordings-row` | `[data-a="sheet"][data-v="storage"]` |  | In use |  |
| `review-takes-row` | `[data-a="tkReview"]` |  | In use |  |
| `remove-prints-row` | `[data-a="sheet"][data-v="melPrintsDel"]` |  | In use |  |

### VS-021 · Settings › Recall

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `peek-length-picker` | `[data-a="peekLen"]` |  | In use |  |

### VS-022 · Settings › Coach video

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `add-video-row` | `[data-a="coachAdd"]` |  | In use |  |

### VS-023 · Settings › Your voice

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `voice-type-row` | `[data-a="patVoiceType"]` |  | In use |  |
| `stop-at-top-switch` | `[data-a="patStopTop"]` |  | In use |  |
| `stop-past-last-switch` | `[data-a="patStopLast"]` |  | In use |  |
| `bridge-row` | `[data-a="patBridge"]` |  | In use |  |

### VS-024 · Settings › Pattern player

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `sound-row` | `[data-a="patSoundPick"]` |  | In use |  |
| `drone-switch` | `[data-a="patDrone"]` |  | In use |  |
| `chord-switch` | `[data-a="patCue"]` |  | In use |  |
| `bridge-cue-switch` | `[data-a="patBCue"]` |  | In use |  |
| `listen-switch` | `[data-a="patListen"]` |  | In use |  |

### VS-025 · Settings › Appearance

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `gradient-switch` | `[data-a="setGrad"]` |  | In use |  |
| `screen-ids-switch` | `[data-a="setIds"]` |  | In use |  |

### VS-026 · Settings › Accessibility

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `reduce-motion-picker` | `[data-a="setReduce"]` |  | In use |  |
| `reduce-transparency-switch` | `[data-a="setTransp"]` |  | In use |  |
| `slow-motion-switch` | `[data-a="setSlow"]` |  | In use |  |

### VS-028 · Marks guide

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `guide-row` | `[data-a="gdOpen"]` |  | In use |  |

### VS-031 · How did it go?

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `save-button` | `[data-a="saveHow"]` |  | In use |  |
| `skip-button` | `[data-a="skipHow"]` |  | In use |  |

### VS-032 · How long did you practise?

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `continue-button` | `[data-a="longOk"]` |  | In use |  |
| `whole-time-button` | `[data-a="longAll"]` |  | In use |  |

### VS-033 · Exercise notes

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `done-button` | `.cta[data-a="close"]` |  | In use |  |

### VS-034 · Your own words

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `add-button` | `[data-a="saveWord"]` |  | In use |  |

### VS-037 · Discard session

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-040 · Edit session

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `save-button` | `[data-a="saveEdit"]` |  | In use |  |

### VS-041 · Delete session

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-043 · Delete song practice

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-045 · Add song

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `add-button` | `[data-a="saveSong"]` |  | In use |  |

### VS-046 · Delete song

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-048 · Take notes

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `done-button` | `.cta[data-a="close"]` |  | In use |  |
| `share-button` | `[data-a="shareTake"]` |  | In use |  |
| `delete-button` | `[data-a="sheet"][data-v="delTake"]` |  | In use |  |

### VS-049 · Delete take

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-050 · Song controls

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `edit-button` | `[data-a="ckGridEdit"]` |  | In use |  |
| `control-tile` | `[data-a="ckTile"]` |  | In use |  |

### VS-051 · New song

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `save-button` | `[data-a="sgSave"]` |  | In use |  |
| `sheet-music-door` | `[data-a="sgAddPdf"]` |  | In use |  |

### VS-056 · Delete this take

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-059 · Unlink from track

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-067 · Remove the track

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-071 · Clear all markers

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-074 · Add exercise

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `add-button` | `[data-a="saveEx"]` |  | In use |  |

### VS-075 · Exercise description

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `save-button` | `[data-a="saveWhat"]` |  | In use |  |

### VS-076 · Delete exercise

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-077 · Recordings (storage)

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `delete-all-button` | `[data-a="sheet"][data-v="clearRec"]` |  | In use |  |

### VS-078 · Delete all recordings

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-079 · Remove the coach video

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-080 · Delete the rescued copy

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-081 · Reset this month

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-082 · Reset all data

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `[data-a="resetAll"]` |  | In use |  |
| `cancel-button` | `.ghost[data-a="close"]` |  | In use |  |

### VS-092 · Session clock

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `pause-button` | `[data-a="pauseToggle"]` |  | In use |  |
| `main-button` | `[data-a="sckMain"]` |  | In use |  |
| `times` | `[data-a="sckSwap"]` |  | In use |  |

### VS-095 · Peek card

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `close-button` | `[data-a="gdPeekClose"]` |  | In use |  |
| `learn-more-button` | `[data-a="gdPeekMore"]` |  | In use |  |

### VS-096 · Find your bridge

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `start-button` | `[data-a="bfStart"]` |  | In use |  |
| `by-feel-button` | `[data-a="bfFeel"]` |  | In use |  |
| `done-button` | `[data-a="bfStop"]` |  | In use |  |
| `from-stepper` | `[data-a="bfStep"][data-v="lo"]` |  | In use |  |
| `to-stepper` | `[data-a="bfStep"][data-v="hi"]` |  | In use |  |
| `use-button` | `[data-a="bfUse"]` |  | In use |  |

### VS-097 · Practise in key

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `pattern-card` | `#pcCard` |  | In use |  |
| `pattern-pill` | `[data-a="patOpen"]` |  | In use |  |
| `start-note-stepper` | `#dock .pstep` |  | In use |  |
| `stay-on-key-button` | `#pRep` |  | In use |  |
| `play-button` | `#pPlay` |  | In use |  |

### VS-098 · Song key

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `mode-picker` | `.keymode .seg` |  | In use |  |
| `note-button` | `[data-a="keyNote"]` |  | In use |  |
| `use-button` | `[data-a="keySave"]` |  | In use |  |

### VS-099 · Sheet music

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `octave-picker` | `.meloct` |  | In use |  |
| `tempo-field` | `#melTempoIn` |  | In use |  |
| `key-row` | `[data-a="melKey"]` |  | In use |  |
| `replace-row` | `[data-a="melReplaceAsk"]` |  | In use |  |

### VS-100 · Sheet music read

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `octave-picker` | `.meloct` |  | In use |  |
| `tempo-field` | `#melTempoIn` |  | In use |  |
| `save-button` | `[data-a="melSave"]` |  | In use |  |
| `cancel-button` | `[data-a="melDrop"]` |  | In use |  |

### VS-101 · Already on another song

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `open-button` | `[data-a="melSameOpen"]` |  | In use |  |
| `add-anyway-button` | `[data-a="melSameGo"]` |  | In use |  |

### VS-102 · A different song?

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `this-song-button` | `[data-a="melTitleHere"]` |  | In use |  |
| `new-song-button` | `[data-a="melTitleNew"]` |  | In use |  |

### VS-103 · Replace the sheet music?

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-104 · Big or long PDF

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-105 · Remove the prints?

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-106 · Reading sheet music

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `cancel-button` | `[data-a="melCancel"]` |  | In use |  |

### VS-107 · Delete sheet music with no song?

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `confirm-button` | `.pk-alert-btn.pk-red` | `pk-alert-btn`, `pk-red` | In use |  |
| `cancel-button` | `.pk-alert-btn[data-a="no"]` | `pk-alert-btn` | In use |  |

### VS-108 · Sheet music page

| Name | Found by | Kit part | Status | Was |
|---|---|---|---|---|
| `sheet-settings-button` | `[data-a="melInfo"]` |  | In use |  |
| `view-picker` | `.mpview` |  | In use |  |
| `speed-stepper` | `.mpspd` |  | In use |  |
| `bars-stepper` | `.mpzoom` |  | In use |  |
| `loop-strip` | `.mploop` |  | In use |  |
| `dots-view` | `.mpdots` |  | In use |  |
| `sheet-view` | `.mpsheet` |  | In use |  |
| `my-note-button` | `[data-a="mpMy"]` |  | In use |  |
| `play-button` | `[data-a="mpPP"]` |  | In use |  |
| `loop-button` | `[data-a="mpLoop"]` |  | In use |  |
