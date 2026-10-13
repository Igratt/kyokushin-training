"""Generates android/app/src/main/res/raw/rest_end.wav: the end-of-rest beep played by the Android app.

Same pattern and level as the in-app Web Audio beep (src/hooks.ts, LEVEL 0.55): three short beeps and a
long one, played twice. Band-limited square wave so it is bright but not harsh.
"""
import math
import os
import struct
import wave

RATE = 32000
LEVEL = 0.55
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "android", "app", "src", "main", "res", "raw", "rest_end.wav")


def tone(freq, dur):
    n = int(RATE * dur)
    attack, release = int(RATE * 0.015), int(RATE * 0.04)
    harmonics = [k for k in range(1, 40, 2) if k * freq < RATE * 0.45]
    out = []
    for i in range(n):
        t = i / RATE
        v = sum(math.sin(2 * math.pi * k * freq * t) / k for k in harmonics) * 4 / math.pi
        env = min(1.0, i / attack) if i < attack else (max(0.0, (n - i) / release) if i > n - release else 1.0)
        out.append(v * env)
    return out


def render(path, total, level, events):
    """events: (start seconds, samples). Normalises the mix to `level` and writes a 16-bit mono WAV."""
    buf = [0.0] * int(RATE * total)
    for start, samples in events:
        s = int(RATE * start)
        for i, v in enumerate(samples):
            if s + i < len(buf):
                buf[s + i] += v
    peak = max(abs(v) for v in buf) or 1.0
    scale = level / peak
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v * scale)) * 32767)) for v in buf))
    print("wrote", os.path.normpath(path), os.path.getsize(path), "bytes")


def main():
    short, long_ = tone(1046, 0.24), tone(1318, 0.7)
    events = []
    for base in (0.0, 2.0):
        for o in (0.0, 0.32, 0.64):
            events.append((base + o, short))
        events.append((base + 1.0, long_))
    render(OUT, 3.8, LEVEL, events)
    # end of a stretch hold: a quick double beep, same as the in-app 'short' beep (src/hooks.ts)
    blip = tone(1318, 0.13)
    render(os.path.join(os.path.dirname(OUT), "stretch_end.wav"), 0.45, 0.5, [(0.0, blip), (0.2, blip)])


if __name__ == "__main__":
    main()
