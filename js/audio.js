/* ===== The shared audio service (Q16) =====
   One AudioContext for everything that listens to the microphone: the mono mix a take is recorded from, the level
   meter and, later, the voice analysers (pitch, vocal weight). It only ever hears the microphone. The song's track
   stays on its own <audio> (track.js explains why: the pitch-kept slow-down, the lock screen and one sound at a time),
   and so do takes and the coach video.
   - iOS only starts a context inside a tap, so wake() is called first thing in the tap that starts a recording. When
     nothing is listening any more the context is suspended (it uses no power then, and a locked phone suspends it
     anyway); the next tap wakes it again. Anything that needs it running must still work without it: a take falls back
     to the microphone as it is (monoStream in session.js), so it's never lost.
   - listen(stream) gives one source for a microphone stream, with mono() (a one-channel stream for MediaRecorder) and
     analyser() (for the meter and, later, the analysers). close() lets go of all of it.
   - frame(fn) is the one frame clock for anything drawn from the microphone: every subscriber is called from the same
     requestAnimationFrame, with its time stamp, and nothing should look anything up on the page per frame (keep the
     elements found when the screen was drawn). It stops itself when nobody is subscribed. */
const AUDIO = (() => {
  let ac = null, // the one context
    made = 0, // how many contexts were made (tests: one, however many takes)
    users = 0; // microphones being listened to
  const AC = () => window.AudioContext || window.webkitAudioContext;
  function ctx() {
    if (ac && ac.state !== 'closed') return ac;
    ac = null;
    const C = AC();
    if (!C) return null;
    try {
      ac = new C();
      made++;
    } catch (e) {
      ac = null;
    }
    return ac;
  }
  // in a tap: make the context or wake it up. Resolves true once it runs, false if it doesn't within ms (400 by default)
  function wake(ms) {
    const c = ctx();
    if (!c) return Promise.resolve(false);
    if (c.state === 'running') return Promise.resolve(true);
    let p;
    try {
      p = Promise.resolve(c.resume()).catch(() => {});
    } catch (e) {
      p = Promise.resolve();
    }
    return Promise.race([p, new Promise((r) => setTimeout(r, ms == null ? 400 : ms))]).then(
      () => c.state === 'running'
    );
  }
  // nothing listening: rest the context (suspended, not closed, so the next take reuses it)
  function rest() {
    if (users || !ac || ac.state !== 'running') return;
    try {
      Promise.resolve(ac.suspend()).catch(() => {});
    } catch (e) {}
  }
  // the microphone, listened to once: {ctx, src, mono(), analyser(n), close()}, or null if there's no Web Audio
  function listen(stream) {
    const c = ctx();
    if (!c || !stream) return null;
    let src;
    try {
      src = c.createMediaStreamSource(stream);
    } catch (e) {
      return null;
    }
    users++;
    const nodes = [];
    let shut = false;
    return {
      ctx: c,
      src,
      // the microphone mixed down to one channel, as a stream (a headset can give the voice on one side only)
      mono() {
        const d = c.createMediaStreamDestination();
        d.channelCount = 1;
        d.channelCountMode = 'explicit';
        d.channelInterpretation = 'speakers';
        src.connect(d);
        nodes.push(d);
        return d.stream;
      },
      analyser(n) {
        const a = c.createAnalyser();
        a.fftSize = n || 512;
        src.connect(a);
        nodes.push(a);
        return a;
      },
      close() {
        if (shut) return;
        shut = true;
        try {
          src.disconnect();
        } catch (e) {}
        nodes.forEach((n) => {
          try {
            n.disconnect();
          } catch (e) {}
        });
        users = Math.max(0, users - 1);
        rest();
      },
      closed: () => shut,
    };
  }

  /* ----- the one frame clock ----- */
  const subs = new Set();
  let raf = 0;
  function tick(ts) {
    raf = 0;
    if (!subs.size) return;
    subs.forEach((f) => {
      try {
        f(ts);
      } catch (e) {}
    });
    if (subs.size) raf = requestAnimationFrame(tick);
  }
  // call fn(time) every frame until the function it returns is called
  function frame(fn) {
    subs.add(fn);
    if (!raf) raf = requestAnimationFrame(tick);
    return () => {
      subs.delete(fn);
      if (!subs.size && raf) {
        cancelAnimationFrame(raf);
        raf = 0;
      }
    };
  }

  return {
    ctx,
    wake,
    listen,
    rest,
    frame,
    state: () => ({ made, users, ctx: ac ? ac.state : null, frames: subs.size }),
  };
})();
