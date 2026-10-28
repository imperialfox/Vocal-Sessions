/* Vocal Sessions · search.js
   3.22 Search (Q01): a search circle beside the tab bar on every main tab (iPad: at the end of the top capsule; wide
   sidebar: a Search row at the top) opens the search page, U.tab = 'find'. It finds songs, lyrics, exercises,
   sessions and takes, grouped, with the same forgiving matching as the Songs list (fold, scoreText, hlWords in
   songs.js). Each group shows its top few, with "Show all n" to expand in place. Results redraw in place as you type,
   so the keyboard stays up and nothing eases (motion rule 5). Search is a tab of its own, so every Back that returns
   "to where you came from" (a song's sgBack, an exercise's exBack) lands back on the results.
   Plain script (not a module): files share one global scope and load in the order listed in index.html. */

const FIND = (() => {
  const SHOW = 3; // results shown per group before "Show all"
  const RECENT = 5;
  const GROUPS = [
    ['songs', 'Songs'],
    ['lyrics', 'Lyrics'],
    ['exercises', 'Exercises'],
    ['sessions', 'Sessions'],
    ['takes', 'Takes'],
  ];

  /* ----- the tiles beside each kind of result ----- */
  const T = (col, p) => '<span class="tile" style="background:' + col + '">' + GL(p) + '</span>';
  const TILE = {
    song: T('var(--coral)', '<path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>'),
    lyric: T('var(--note)', '<path d="M5 7h14M5 12h14M5 17h9"/>'),
    session: T(
      'var(--accent)',
      '<rect x="4" y="5.5" width="16" height="14.5" rx="3"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/>'
    ),
    take: T('var(--sys-orange)', '<path d="M4 12h1.5M8 8.5v7M11.5 5v14M15 9v6M18.5 11v2"/>'),
  };

  /* ----- recent searches: this device only (vocalSongPrefs.findRecent), never in backups ----- */
  function recents() {
    const r = sgp().findRecent;
    return Array.isArray(r) ? r.filter((x) => typeof x === 'string' && x.trim()).slice(0, RECENT) : [];
  }
  function remember(q) {
    q = (q || '').trim();
    if (!q) return;
    sgp().findRecent = [q].concat(recents().filter((r) => r.toLowerCase() !== q.toLowerCase())).slice(0, RECENT);
    saveSGP();
  }
  function forget(q) {
    sgp().findRecent = q == null ? [] : recents().filter((r) => r !== q);
    saveSGP();
  }

  /* ----- matching ----- */
  const plain = (h) =>
    String(h || '')
      .replace(/<[^>]*>/g, '')
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#39;|&rsquo;/g, '’');
  // the sentence of a longer text that matches best, trimmed around the first matching word
  function snippet(text, q, toks) {
    const ss = plain(text).match(/[^.!?]+[.!?]*/g) || [plain(text)];
    let best = null,
      bs = 0;
    ss.forEach((s) => {
      const sc = scoreText(s, q, toks);
      if (sc > bs) {
        bs = sc;
        best = s;
      }
    });
    if (!best) best = ss.find((s) => toks.some((t) => fold(s).split(' ').some((w) => tokHit(t, w)))) || ss[0];
    best = best.trim();
    if (best.length <= 90) return best;
    const words = best.split(/\s+/),
      at = Math.max(
        0,
        words.findIndex((w) => toks.some((t) => tokHit(t, fold(w))))
      ),
      from = Math.max(0, at - 4);
    let out = words.slice(from).join(' ');
    if (out.length > 90) out = out.slice(0, 88).replace(/\s+\S*$/, '') + '…';
    return (from ? '…' : '') + out;
  }

  function find(q) {
    const toks = fold(q).split(' ').filter(Boolean),
      R = { toks, songs: [], lyrics: [], exercises: [], sessions: [], takes: [] };
    if (!toks.length) return R;
    const sorted = sortedSongs(D.songs);
    // Songs: title and artist. Lyrics: every line of every section once (linked repeats share their lines)
    sorted.forEach((s, rank) => {
      const sc = Math.max(scoreText(songTitle(s), q, toks), scoreText(s.artist || '', q, toks));
      if (sc) R.songs.push({ s, sc, rank });
      if (!hasLyrics(s)) return;
      const seen = new Set();
      s.order.forEach((x, oi) => {
        if (seen.has(x.sid)) return;
        seen.add(x.sid);
        s.sections[x.sid].lines.forEach((ln, li) => {
          const t = ln.join(' '),
            lc = scoreText(t, q, toks);
          if (lc) R.lyrics.push({ s, oi, o: x.o, li, t, sc: lc, rank });
        });
      });
    });
    R.songs.sort((a, b) => b.sc - a.sc || a.rank - b.rank);
    R.lyrics.sort((a, b) => b.sc - a.sc || a.rank - b.rank || a.oi - b.oi || a.li - b.li);
    // Exercises: the name first, then their write-up
    FOUND.concat(allRot()).forEach((e, i) => {
      const nc = scoreText(e.name, q, toks);
      if (nc) return R.exercises.push({ e, sc: 10 + nc, i });
      const d = DESC[e.id];
      if (!d) return;
      const parts = [
        ['About', d.what],
        ['Why it helps', d.why],
      ].concat((d.song || []).map((p) => ['In a song', p[0] + '. ' + p[1]]));
      let best = null;
      parts.forEach(([lab, txt]) => {
        const sc = scoreText(plain(txt), q, toks);
        if (sc && (!best || sc > best.sc)) best = { lab, txt, sc };
      });
      if (best) R.exercises.push({ e, sc: best.sc, i, lab: best.lab, snip: snippet(best.txt, q, toks) });
    });
    R.exercises.sort((a, b) => b.sc - a.sc || a.i - b.i);
    // Sessions: their notes and feedback words (not exercise names, which every session has)
    D.sessions
      .map((x) => ({ x, song: false }))
      .concat(D.songSessions.map((x) => ({ x, song: true })))
      .forEach(({ x, song }) => {
        const texts = [];
        (x.how || []).forEach((w) => texts.push(w));
        if (x.howNote) texts.push(x.howNote);
        if (x.fNote) texts.push(x.fNote);
        if (x.rNote) texts.push(x.rNote);
        Object.keys(x.xn || {}).forEach((id) => {
          const n = noteStr(x.xn[id]);
          if (!n) return;
          const e = exById(id);
          texts.push((e ? e.name : (x.rotNames && x.rotNames[id]) || 'Exercise') + ': ' + n);
        });
        let best = null;
        texts.forEach((t) => {
          const sc = scoreText(t, q, toks);
          if (sc && (!best || sc > best.sc)) best = { t, sc };
        });
        if (best) R.sessions.push({ x, song, t: best.t, sc: best.sc });
      });
    R.sessions.sort((a, b) => new Date(b.x.date) - new Date(a.x.date));
    // Takes: renamed takes and comment text (takes on this device only, so a hit can open)
    D.songs.forEach((s) => {
      const tn = s.takeNotes || {};
      Object.keys(tn).forEach((id) => {
        const tk = TAKES.find((t) => t.id === id && t.songId === s.id);
        if (!tk) return;
        const n = tn[id] || {};
        if (n.name && scoreText(n.name, q, toks)) R.takes.push({ s, tk, text: n.name });
        (n.comments || []).forEach((c) => {
          if (c && c.text && scoreText(c.text, q, toks)) R.takes.push({ s, tk, text: c.text, at: c.t });
        });
      });
    });
    R.takes.sort((a, b) => (b.tk.created || 0) - (a.tk.created || 0) || (a.at || 0) - (b.at || 0));
    return R;
  }

  /* ----- drawing ----- */
  const fmt = (s) => {
    s = Math.max(0, Math.floor(s || 0));
    return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
  };
  const takeNo = (tk) => TAKES.filter((t) => t.songId === tk.songId).indexOf(tk) + 1;
  const row = (attrs, tileH, main, sub) =>
    '<button class="row frow" ' +
    attrs +
    '>' +
    tileH +
    '<span class="lbl">' +
    main +
    (sub ? '<small>' + sub + '</small>' : '') +
    '</span>' +
    chev +
    '</button>';
  function songRow(s, toks, pm) {
    const lp = lastPractised(s, pm);
    return row(
      'data-zk="sg:' + s.id + '" data-push data-a="sgOpen" data-v="find" data-k="' + s.id + '"',
      TILE.song,
      hlWords(songTitle(s), toks),
      (s.artist ? hlWords(s.artist, toks) + ' · ' : '') + (lp ? practisedText(lp) : 'Not practised yet')
    );
  }
  function rowsFor(k, R) {
    const toks = R.toks,
      pm = practisedMap();
    if (k === 'songs') return R.songs.map((r) => songRow(r.s, toks, pm));
    if (k === 'lyrics')
      return R.lyrics.map((r, i) =>
        row(
          'data-zk="fl:' + i + '" data-push data-a="findLyr" data-k="' + r.s.id + '" data-o="' + esc(r.o) + '"',
          TILE.lyric,
          '<span class="fline">' + hlWords(r.t, toks) + '</span>',
          esc(songTitle(r.s)) + ' · ' + esc(occLabel(r.s, r.oi))
        )
      );
    if (k === 'exercises')
      return R.exercises.map((r) =>
        row(
          'data-zk="ex:' + r.e.id + '" data-push data-a="openEx" data-k="' + r.e.id + '"',
          tile(r.e),
          hlWords(r.e.name, toks),
          r.lab
            ? '<span class="fsnip"><i>' + r.lab + ' ·</i> ' + hlWords(r.snip, toks) + '</span>'
            : esc(r.e.focus) + ' · ' + lastDone(r.e.id)
        )
      );
    if (k === 'sessions')
      return R.sessions.map((r) =>
        row(
          'data-a="sheet" data-v="' + (r.song ? 'songSession' : 'session') + '" data-k="' + r.x.id + '"',
          r.song ? songTile : TILE.session,
          esc(dayLabel(r.x.date)) +
            (r.song ? ' · Song practice' + (r.x.songName ? ' · ' + esc(r.x.songName) : '') : ''),
          '<span class="fsnip">' + hlWords(r.t, toks) + '</span>'
        )
      );
    return R.takes.map((r) =>
      row(
        'data-zk="ft:' +
          r.tk.id +
          (r.at != null ? ':' + r.at : '') +
          '" data-a="findTake" data-k="' +
          r.tk.id +
          '"' +
          (r.at != null ? ' data-t="' + r.at + '"' : ''),
        TILE.take,
        '<span class="fline">' + hlWords(r.text, toks) + '</span>',
        esc(songTitle(r.s)) +
          ' · Take ' +
          takeNo(r.tk) +
          ' · ' +
          relDay(new Date(r.tk.created || Date.now()).toISOString()) +
          (r.at != null ? ' · ' + fmt(r.at) : '')
      )
    );
  }
  function listHTML() {
    const q = (U.fq || '').trim();
    if (!q) {
      const rc = recents(),
        pins = pinnedSongs(),
        pm = practisedMap();
      let h = '';
      if (rc.length)
        h +=
          '<div class="hdr sghdr"><span>Recent</span><button data-a="findClearRecent">Clear</button></div><div class="grp">' +
          rc
            .map(
              (r) =>
                '<div class="recent"><button class="rtxt2" data-a="findRecent" data-v="' +
                esc(r) +
                '">' +
                SGI.clock +
                '<span>' +
                esc(r) +
                '</span></button><button class="rx" data-a="findRmRecent" data-v="' +
                esc(r) +
                '" aria-label="Remove ' +
                esc(r) +
                '">' +
                SGI.x +
                '</button></div>'
            )
            .join('') +
          '</div>';
      if (pins.length)
        h +=
          '<div class="hdr">Pinned songs</div><div class="grp tiled">' +
          pins.map((s) => songRow(s, null, pm)).join('') +
          '</div>';
      return h || '<p class="note fnote">Search your songs, lyrics, exercises and sessions.</p>';
    }
    const R = find(q),
      open = U.fAll || [];
    let h = '';
    GROUPS.forEach(([k, title]) => {
      const rows = rowsFor(k, R);
      if (!rows.length) return;
      const all = open.includes(k) || rows.length <= SHOW + 1;
      h +=
        '<div class="hdr">' +
        title +
        '</div><div class="grp tiled" data-fg="' +
        k +
        '">' +
        (all ? rows : rows.slice(0, SHOW)).join('') +
        (all
          ? ''
          : '<button class="row fmore" data-a="findMore" data-k="' +
            k +
            '"><span class="lbl acc">Show all ' +
            rows.length +
            '</span></button>') +
        '</div>';
    });
    return (
      h ||
      '<div class="sgempty">' +
        SGI.search +
        '<b>No results for “' +
        esc(q) +
        '”</b>Check the spelling or try fewer words.</div>'
    );
  }
  function page() {
    const q = U.fq || '';
    return (
      '<h1>Search</h1><div class="fbar' +
      (q.trim() ? ' on' : '') +
      '"><label class="sfield inl ffield">' +
      SGI.search +
      '<input id="fq" type="search" placeholder="Search" autocomplete="off" autocorrect="off" spellcheck="false" enterkeyhint="search" aria-label="Search" value="' +
      esc(q) +
      '"><button class="sclear" data-a="findClear" aria-label="Clear search"' +
      (q.trim() ? '' : ' hidden') +
      '>' +
      SGI.xc +
      '</button></label><button class="scancel" data-a="findCancel">Cancel</button></div><div id="flist">' +
      listHTML() +
      '</div>'
    );
  }
  // only the results change while typing, so the field (and the keyboard) stays
  function update() {
    const l = $('flist');
    if (l) l.innerHTML = listHTML();
    const has = !!(U.fq || '').trim(),
      c = document.querySelector('.ffield .sclear'),
      b = document.querySelector('.fbar');
    if (c) c.hidden = !has;
    if (b) b.classList.toggle('on', has || document.activeElement === $('fq'));
  }
  const shown = () => U.tab === 'find' && !U.view;
  function after() {
    if (!shown() || !U.fFocus) return;
    U.fFocus = false;
    const i = $('fq');
    if (i && !U.sheet) {
      i.focus();
      if (i.value) i.setSelectionRange(i.value.length, i.value.length);
    }
  }

  /* ----- the circle and the other doors ----- */
  const circle = () =>
    '<button class="circ glass scirc' +
    (U.tab === 'find' ? ' on' : '') +
    '" data-a="findOpen" aria-label="Search" aria-current="' +
    (U.tab === 'find' ? 'page' : 'false') +
    '"><span class="ring" aria-hidden="true"></span>' +
    SGI.search +
    '</button>';
  const capsuleBtn = () =>
    '<button class="tsr' +
    (U.tab === 'find' ? ' on' : '') +
    '" data-a="findOpen" aria-label="Search" aria-current="' +
    (U.tab === 'find' ? 'page' : 'false') +
    '">' +
    SGI.search +
    '</button>';
  const sideRow = () =>
    '<button class="sbi' +
    (U.tab === 'find' ? ' on' : '') +
    '" data-a="findOpen" aria-current="' +
    (U.tab === 'find' ? 'page' : 'false') +
    '">' +
    SGI.search +
    '<span>Search</span></button>';
  function open() {
    if (U.sheet) return;
    U.clock = false;
    if (U.sFocus) {
      U.sFocus = false;
      U.sq = '';
    }
    if (shown()) {
      const i = $('fq');
      if (i) i.focus();
      return;
    }
    go(() => {
      U.tab = 'find';
      U.view = null;
      U.fFocus = true;
    });
  }

  /* ----- opening a result ----- */
  // a lyric: the song in Practise, scrolled to its section with that section focused (zooming from the row)
  function openLyric(id, o) {
    const sg = songById(id);
    if (!sg) return;
    if (rec) return toast('Stop recording first');
    if (split()) {
      openSong(id);
      U.sSec = o;
      rerender();
      toSec(o);
      return;
    }
    const was = U.view,
      z = ZOOM.before();
    U.sRet = 'find';
    U.songId = id;
    U.tab = 'songs';
    U.view = 'lyr';
    U.sMode = 'practise';
    U.sSec = o;
    if (typeof FW !== 'undefined') FW.shut = false;
    window.scrollTo(0, 0);
    render();
    toSec(o);
    if (!ZOOM.after(z)) DET.stepIn(DET.stepDir(was, U.view));
  }
  function toSec(o) {
    const s = document.querySelector('.sgsec[data-o="' + (window.CSS && CSS.escape ? CSS.escape(o) : o) + '"]');
    if (!s) return;
    const bar = $('bar'),
      top = bar ? bar.getBoundingClientRect().bottom : 70;
    window.scrollTo(0, Math.max(0, s.getBoundingClientRect().top + window.scrollY - top - 12));
  }
  // a take or a comment: its song, the takes sheet on All takes with the take expanded (and for a comment, the
  // playhead at its time with the comment showing)
  function openTake(id, at) {
    const tk = TAKES.find((t) => t.id === id);
    if (!tk || !songById(tk.songId)) return;
    if (rec) return toast('Stop recording first');
    openSong(tk.songId, 'find');
    TAKE.openAt(id, at);
  }

  /* ----- actions (data-a="find…") ----- */
  Object.assign(SG_ACT, {
    findOpen() {
      open();
    },
    findClear() {
      U.fq = '';
      U.fAll = [];
      const i = $('fq');
      if (i) {
        i.value = '';
        i.focus();
      }
      update();
    },
    findCancel() {
      U.fq = '';
      U.fAll = [];
      const i = $('fq');
      if (i) {
        i.value = '';
        i.blur();
      }
      update();
    },
    findMore(el, v, k) {
      U.fAll = (U.fAll || []).concat(k);
      update();
    },
    findRecent(el, v) {
      U.fq = v;
      U.fAll = [];
      remember(v);
      const i = $('fq');
      if (i) {
        i.value = v;
        i.blur();
      }
      update();
    },
    findRmRecent(el, v) {
      forget(v);
      update();
    },
    findClearRecent() {
      forget(null);
      update();
    },
    findLyr(el, v, k) {
      openLyric(k, el.dataset.o);
    },
    findTake(el, v, k) {
      openTake(k, el.dataset.t != null ? +el.dataset.t : null);
    },
  });

  /* ----- typing ----- */
  document.addEventListener('input', (e) => {
    if (e.target.id !== 'fq') return;
    const v = e.target.value;
    if (v.trim() !== (U.fq || '').trim()) U.fAll = [];
    U.fq = v;
    update();
  });
  document.addEventListener('keydown', (e) => {
    if (e.target.id !== 'fq') return;
    if (e.key === 'Enter') {
      e.preventDefault();
      remember(U.fq);
      e.target.blur();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      if ((U.fq || '').trim()) SG_ACT.findClear();
      else e.target.blur();
    }
  });
  document.addEventListener('focusin', (e) => {
    if (e.target.id === 'fq') update();
  });
  document.addEventListener('focusout', (e) => {
    if (e.target.id !== 'fq') return;
    setTimeout(update, 0);
    // the keyboard is away: a floating window can come back straight away (window.js also checks a moment later)
    if (document.activeElement !== e.target && typeof fwUpdate === 'function') fwUpdate();
  });
  // tapping a result remembers what was searched
  document.addEventListener(
    'click',
    (e) => {
      if (!shown() || !(U.fq || '').trim()) return;
      if (e.target.closest && e.target.closest('#flist .frow')) remember(U.fq);
    },
    true
  );

  return {
    page,
    after,
    circle,
    capsuleBtn,
    sideRow,
    open,
    shown,
    // tests
    find: (q) => {
      const R = find(q);
      const out = {};
      GROUPS.forEach(([k]) => (out[k] = R[k].length));
      return out;
    },
    recents,
  };
})();
