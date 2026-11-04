"""Q43 · Audio: Recorded Piano and Soft Tone: make the 17 piano notes for audio/piano/.

Source: https://github.com/Leethring/piano-sound-samples (MIT, Liam Lee 2020; made with MuseScore).
Usage:  git clone --depth 1 https://github.com/Leethring/piano-sound-samples.git /tmp/pss
        python3 tools/make_piano_samples.py /tmp/pss/sound_keyboard_staff audio/piano
        cp /tmp/pss/LICENSE audio/piano/LICENSE.txt
Needs ffmpeg (with libmp3lame) and numpy.

The same steps made the sound test prototype's v3 set (1.4 MB), which Ivan approved on 4 Nov 2026:
- One note every three semitones from C2 to C6 (17 files). The repo's names follow its own scheme
  (X_2 octave 0, X_1 octave 1, capitals octave 2, doubled lower case octave 3, x1 to x4 octaves 4 to 7);
  the map below was checked by measuring each file's pitch.
- Kept in STEREO: the two channels differ a lot (correlation -0.08 to 0.8), and mixing to mono made it hollow.
- Trimmed to the note's start (4 ms before), cut to 4.8 s with a 1.2 s cosine fade, levelled to the same
  loudness over the first 0.6 s (RMS 0.18), peaks kept under 0.95, encoded once as MP3 VBR V0.
"""
import pathlib
import subprocess
import sys

import numpy as np

NAMES = {36: 'C', 39: 'Ds', 42: 'Fs', 45: 'A', 48: 'cc', 51: 'dds', 54: 'ffs', 57: 'aa', 60: 'c1',
         63: 'd1s', 66: 'f1s', 69: 'a1', 72: 'c2', 75: 'd2s', 78: 'f2s', 81: 'a2', 84: 'c3'}
NOTE = ['C', 'Cs', 'D', 'Ds', 'E', 'F', 'Fs', 'G', 'Gs', 'A', 'As', 'B']
SR = 44100


def main(src, out):
    src, out = pathlib.Path(src), pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for m, n in NAMES.items():
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(src / (n + '.mp3')), '-ar', str(SR), '-f', 'f32le', '-'],
                             capture_output=True, check=True).stdout
        x = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()
        a = np.abs(x).max(1)
        on = int(np.argmax(a > 0.02 * a.max()))
        x = x[max(0, on - int(0.004 * SR)):][:int(4.8 * SR)]
        f = int(1.2 * SR)
        x[-f:] *= (np.cos(np.linspace(0, np.pi / 2, f)) ** 2)[:, None]
        x *= 0.18 / np.sqrt(np.mean(x[:int(0.6 * SR)] ** 2))
        x *= min(1, 0.95 / np.abs(x).max())
        name = NOTE[m % 12] + str(m // 12 - 1)  # e.g. C4, Fs3
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                        '-c:a', 'libmp3lame', '-q:a', '0', str(out / (name + '.mp3'))],
                       input=x.astype(np.float32).tobytes(), check=True)
        print(m, name, 'from', n)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
