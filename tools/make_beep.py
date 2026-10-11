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


def main():
    total = 3.8
    buf = [0.0] * int(RATE * total)

    def put(start, samples):
        s = int(RATE * start)
        for i, v in enumerate(samples):
            if s + i < len(buf):
                buf[s + i] += v

    short, long_ = tone(1046, 0.24), tone(1318, 0.7)
    for base in (0.0, 2.0):
        for o in (0.0, 0.32, 0.64):
            put(base + o, short)
        put(base + 1.0, long_)
    peak = max(abs(v) for v in buf) or 1.0
    scale = LEVEL / peak
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with wave.open(OUT, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v * scale)) * 32767)) for v in buf))
    print("wrote", os.path.normpath(OUT), os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
