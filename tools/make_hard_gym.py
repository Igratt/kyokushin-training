"""Writes src/data/programs/hard-gym.json: the gym-only program for a break from karate.

4 days, upper / lower twice a week: heavy main lifts (4–6), accessories (8–15), one explosive exercise per day
to keep the speed, the whole-body warm-up before every workout (tools/add_hips.py) and the user's weaker side first
on one-sided exercises (legs: left, chest and back: right, arms: left).

Exercises taken over from the Kyokushin program keep their descriptions and pictures. A picture whose corner
number differs from the new position is copied with the right number (tools/rebadge.py) as G_<day><n>[v].webp.
New pictures come from tools/draw_gym.py.

Usage:  py tools/make_hard_gym.py
"""
import copy
import json
import os
import re

from add_hips import warmup_for
from rebadge import rebadge

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ASSETS = os.path.join(ROOT, "public", "assets")
MIX = os.path.join(ROOT, "src", "data", "programs", "kyokushin-mix.json")
OUT = os.path.join(ROOT, "src", "data", "programs", "hard-gym.json")

with open(MIX, encoding="utf-8") as f:
    mix = json.load(f)

by_id = {}
for d in mix["days"]:
    for e in d["exercises"]:
        by_id[e["id"]] = e
        for v in e.get("variants", []):
            by_id[v["id"]] = v
stretches_of = {d["id"]: d.get("stretches", []) for d in mix["days"]}

KEEP = ("name", "tag", "image", "description", "focus", "seconds", "sides", "startSide")
BONUS_SETS = 1  # extra set for the weaker side on every one-sided exercise
copies = []


def picture(src_id, day, n, variant):
    """Image path for the exercise at position n: the original if its number matches, else a renumbered copy."""
    src = by_id[src_id]["image"].replace(".png", ".webp")
    old_n = int(re.match(r"[A-Z](\d+)", src_id).group(1))
    if old_n == n:
        return src
    dst = f"assets/G_{day}{n}{'v' if variant else ''}.webp"
    copies.append((src, dst, n))
    return dst


def reuse(src_id, day, n, sets, reps, rest, variant=False, **extra):
    e = {k: copy.deepcopy(v) for k, v in by_id[src_id].items() if k in KEEP}
    e["image"] = picture(src_id, day, n, variant)
    e.update(sets=sets, reps=reps, restSeconds=rest, **extra)
    e = {"id": f"G{day}{n}{'v' if variant else ''}", **e}
    return e


def new(day, n, name, sets, reps, rest, description, focus, **extra):
    return {"id": f"G{day}{n}", "name": name, "sets": sets, "reps": reps, "restSeconds": rest,
            "image": f"assets/G_{day}{n}.webp", "description": description, "focus": focus, **extra}


def with_variants(e, *variants):
    e["variants"] = list(variants)
    return e


A = [
    with_variants(reuse("B6", "A", 1, 3, "5", 75), reuse("B6v", "A", 1, 3, "5", 75, True)),
    reuse("B2", "A", 2, 4, "4–6", 150),
    with_variants(reuse("B3", "A", 3, 4, "5–8", 120), reuse("B3v", "A", 3, 4, "8–10", 120, True)),
    new("A", 4, "Single-Arm Dumbbell Bench Press", 3, "8–10 / ranka", 90,
        "Gulk ant suolo, hantelis vienoje rankoje prie krūtinės, kita ranka ant klubo. Spausk tiesiai aukštyn ir lėtai nuleisk. Neleisk kūnui suktis į šoną.",
        "Krūtinė po vieną pusę: silpnesnė dešinė pasiveja kairę.", startSide="right"),
    new("A", 5, "Single-Arm Dumbbell Row", 3, "8–10 / ranka", 90,
        "Kelis ir ranka ant suolo, nugara tiesi ir lygiagreti grindims. Trauk hantelį alkūne aukštyn link klubo, viršuje suspausk mentę, lėtai nuleisk.",
        "Nugaros pusės po vieną: dešinė silpnesnė, todėl pirma.", startSide="right"),
    new("A", 6, "Lateral Raise", 3, "12–15", 60,
        "Stovėk tiesiai, hanteliai prie šonų, alkūnės šiek tiek sulenktos. Kelk rankas į šonus iki pečių aukščio ir lėtai nuleisk. Nesiūbuok kūnu.",
        "Platesni pečiai ir sveiki pečių sąnariai."),
    new("A", 7, "Dumbbell Curl", 3, "10–12 / ranka", 60,
        "Stovėk tiesiai, alkūnės prie šonų. Lenk ranką iki peties, viršuje suspausk ir lėtai nuleisk. Po vieną ranką.",
        "Bicepsas: silpnesnė kairė ranka pasiveja dešinę.", startSide="left"),
    with_variants(reuse("A7", "A", 8, 3, "10–15", 60), reuse("A7v", "A", 8, 3, "12–15", 60, True)),
]

B = [
    with_variants(reuse("A1", "B", 1, 3, "3", 75), reuse("A1v", "B", 1, 3, "3", 75, True)),
    reuse("A2", "B", 2, 4, "4–6", 180),
    with_variants(reuse("A3", "B", 3, 3, "6–8", 120), reuse("A3v", "B", 3, 3, "8 / koja", 90, True)),
    with_variants(reuse("A4", "B", 4, 3, "8 / koja", 90), reuse("A4v", "B", 4, 3, "8 / koja", 90, True)),
    with_variants(reuse("A10", "B", 5, 3, "20 s / pusė", 45), reuse("A10v", "B", 5, 3, "6 / pusė", 45, True)),
    with_variants(reuse("A6", "B", 6, 4, "10–12", 60), reuse("A6v", "B", 6, 3, "10–12 / koja", 60, True)),
    with_variants(reuse("C8", "B", 7, 3, "8–12", 60), reuse("C8v", "B", 7, 3, "8 / pusė", 60, True)),
]

C = [
    with_variants(reuse("B1", "C", 1, 3, "4 / pusė", 60), reuse("B1v", "C", 1, 3, "6 / pusė", 60, True)),
    new("C", 2, "Incline Dumbbell Press", 4, "8–10", 120,
        "Suolas pakeltas 30–45°. Hanteliai prie krūtinės viršaus, alkūnės apie 45° nuo kūno. Spausk aukštyn, kol rankos tiesios, ir lėtai nuleisk.",
        "Viršutinė krūtinė ir pečiai."),
    with_variants(reuse("B3v", "C", 3, 4, "8–12", 90), reuse("C5v", "C", 3, 4, "6–10", 90, True)),
    with_variants(reuse("B4", "C", 4, 3, "8 / ranka", 90), reuse("B4v", "C", 4, 3, "8 / ranka", 90, True)),
    with_variants(reuse("B5", "C", 5, 3, "10–12", 90), reuse("B5v", "C", 5, 3, "10–12", 90, True)),
    with_variants(reuse("B7", "C", 6, 3, "12–15", 60), reuse("B7v", "C", 6, 3, "15–20", 45, True)),
    new("C", 7, "Cable Triceps Pushdown", 3, "10–15", 60,
        "Stovėk prie lyno, alkūnės prispaustos prie šonų. Spausk rankeną žemyn, kol rankos visiškai ištiestos, ir lėtai grąžink iki krūtinės. Alkūnės nejuda.",
        "Tricepsas: stipresnis spaudimas ir smūgio užbaigimas."),
    with_variants(reuse("B9", "C", 8, 3, "45–60 s", 45), reuse("B9v", "C", 8, 3, "30–45 s / pusė", 45, True)),
]

D = [
    with_variants(reuse("C1", "D", 1, 3, "3", 75), reuse("C1v", "D", 1, 3, "3", 75, True)),
    reuse("C2", "D", 2, 4, "5", 150),
    new("D", 3, "Barbell Hip Thrust", 4, "8–10", 90,
        "Viršutinė nugara ant suolo krašto, pėdos ant žemės, štanga per klubus (su minkšta apsauga). Kelk klubus, kol kūnas tiesus nuo pečių iki kelių, viršuje 1 s suspausk sėdmenis.",
        "Sėdmenys ir dubens jėga."),
    with_variants(reuse("C4", "D", 4, 3, "10 / koja", 90), reuse("C4v", "D", 4, 3, "8 / koja", 90, True)),
    with_variants(reuse("C10", "D", 5, 3, "6 / pusė", 60), reuse("C10v", "D", 5, 3, "45 s", 45, True)),
    with_variants(reuse("A3v", "D", 6, 3, "8 / koja", 75), reuse("B10v", "D", 6, 3, "5 / koja", 45, True)),
    with_variants(reuse("C7", "D", 7, 3, "30–40 m", 75), reuse("C7v", "D", 7, 3, "30 m / ranka", 75, True)),
    with_variants(reuse("A8", "D", 8, 3, "10 / pusė", 50), reuse("A8v", "D", 8, 3, "10 / pusė", 50, True)),
]

UPPER, LOWER = stretches_of["B"], stretches_of["A"]
program = {
    "id": "hard-gym",
    "programName": "Hard Gym: jėga + masė",
    "focus": "Sporto salė: jėga + masė",
    "goal": "Karatė pertraukai: 4 dienos, viršus ir apačia po du kartus. Sunkūs pagrindiniai kėlimai po 4–6 kartus, "
            "pagalbiniai po 8–15 ir po vieną sprogstamą pratimą, kad neprarastum greičio. Prieš kiekvieną treniruotę "
            "viso kūno apšilimas, vienpusiai pratimai pradedami silpnesne puse ir gauna papildomą setą tik jai.",
    "days": [
        {"id": "A", "name": "A DIENA", "subtitle": "Viršus · jėga", "warmup": warmup_for("upper"), "exercises": A, "stretches": UPPER},
        {"id": "B", "name": "B DIENA", "subtitle": "Apačia · jėga", "warmup": warmup_for("lower"), "exercises": B, "stretches": LOWER},
        {"id": "C", "name": "C DIENA", "subtitle": "Viršus · masė", "warmup": warmup_for("upper"), "exercises": C, "stretches": UPPER},
        {"id": "D", "name": "D DIENA", "subtitle": "Apačia · masė + dubuo", "warmup": warmup_for("lower"), "exercises": D, "stretches": LOWER},
    ],
}


def main():
    for day in program["days"]:
        for e in day["exercises"]:
            for v in [e] + e.get("variants", []):
                if v.get("startSide") and not v.get("bonusSets"):
                    v["sets"] = v["sets"] + BONUS_SETS
                    v["bonusSets"] = BONUS_SETS
    for src, dst, n in copies:
        rebadge(os.path.join(ROOT, "public", src), os.path.join(ROOT, "public", dst), n)
        print("copied", src, "->", dst, "#", n)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(program, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
