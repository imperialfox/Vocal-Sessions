"""js/content.js: the exercises, write-ups, words, goals, video timings and Toggl tags fit together.
Run after editing content:  python tests/run.py content"""

CHECKS = r"""(()=>{const p=[];const all=FOUND.concat(ROT),ids=all.map(e=>e.id);
  const str=x=>typeof x==='string'&&x.trim().length>0;
  const list=(name,a)=>{if(!Array.isArray(a)||!a.length)p.push(name+' should be a list of words');else{a.forEach(w=>{if(!str(w))p.push(name+' has an empty word')});
    const d=a.filter((w,i)=>a.indexOf(w)!==i);if(d.length)p.push(name+' repeats '+d.join(', '));}};
  if(new Set(ids).size!==ids.length)p.push('two exercises share an id');
  all.forEach(e=>{if(!/^[a-z]+$/.test(e.id||''))p.push('exercise id "'+e.id+'" should be lowercase letters');
    if(!str(e.name))p.push(e.id+' needs a name');if(!FOCI.includes(e.focus))p.push(e.id+' focus "'+e.focus+'" should be one of '+FOCI.join(', '));});
  all.forEach(e=>{const d=DESC[e.id];if(!d){p.push(e.id+' has no write-up in DESC');return;}
    if(!str(d.what)||!str(d.why))p.push(e.id+' write-up needs what and why');
    if(!Array.isArray(d.song)||d.song.some(s=>!Array.isArray(s)||s.length!==2||!str(s[0])||!str(s[1])))p.push(e.id+' write-up: song should be pairs of [title, text]');
    [d.what,d.why].concat((d.song||[]).flat()).forEach(t=>{if(/&(?!amp;|lt;|gt;|quot;|#\d+;)/.test(String(t)))p.push(e.id+' write-up has a bare & (write &amp;)');});});
  Object.keys(DESC).forEach(k=>{if(!ids.includes(k))p.push('DESC has a write-up for unknown exercise "'+k+'"')});
  const ns=Object.values(DESC).map(d=>d.n);if(new Set(ns).size!==ns.length)p.push('two write-ups share the same n');
  all.forEach(e=>{if(!EX_WORDS[e.id])p.push(e.id+' has no quick words in EX_WORDS');});
  Object.keys(EX_WORDS).forEach(k=>{if(!ids.includes(k))p.push('EX_WORDS has words for unknown exercise "'+k+'"');list('EX_WORDS.'+k,EX_WORDS[k]);});
  list('HOW_WORDS',HOW_WORDS);list('TAKE_WORDS',TAKE_WORDS);list('EX_WORDS_DEFAULT',EX_WORDS_DEFAULT);
  all.forEach(e=>{if(!(VID[e.id]>0))p.push(e.id+' has no coach-video timing in VID');});
  Object.keys(VID).forEach(k=>{if(!ids.includes(k))p.push('VID has a timing for unknown exercise "'+k+'"')});
  if(!(Number.isInteger(TARGET)&&TARGET>0&&Number.isInteger(WEEK_TARGET)&&WEEK_TARGET>0))p.push('TARGET and WEEK_TARGET should be whole minutes');
  if(!/^https:\/\//.test(VIDEO))p.push('VIDEO should be an https link');
  ['foundation','rotation','application','song'].forEach(k=>{if(!/^#\S/.test(TOGGL[k]||''))p.push('TOGGL.'+k+' should start with #');});
  return p;})()"""

def run(b, t):
    pg = t.page(b, data=None)
    problems = pg.evaluate(CHECKS)
    for msg in problems: t.ok(False, 'content.js: ' + msg)
    if not problems: t.ok(True, f'content.js fits together: {pg.evaluate("FOUND.length+ROT.length")} exercises with write-ups, words and video timings')
    # every exercise page opens, and its Summary shows the write-up
    bad = pg.evaluate("""(()=>{const bad=[];for(const e of FOUND.concat(ROT)){U.view='ex';U.exId=e.id;U.exTab='summary';render();
      const t=document.getElementById('app').innerText;if(!t.includes(e.name)||t.length<200)bad.push(e.id);}U.view=null;render();return bad})()""")
    t.ok(not bad, 'every exercise page shows its write-up' + (': missing ' + ', '.join(bad) if bad else ''))
    # Toggl text uses the tags from content.js
    tags = pg.evaluate("TOGGL")
    pg.evaluate("D.sessions.push({id:'tg',date:new Date().toISOString(),mins:30,f:{slides:2},rot:{rung:3},xn:{},rate:{},takes:[],how:[],howNote:''})")
    lines = pg.evaluate("togglLines(D.sessions.find(s=>s.id==='tg'))").split('\n')
    t.ok(lines[0].endswith(tags['foundation']) and lines[1].endswith(tags['rotation'] + ' #resonance') and lines[2].endswith(tags['application']),
         'Copy for Toggl uses the tags from content.js')
