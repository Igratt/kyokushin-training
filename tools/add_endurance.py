"""Endurance finishers, 2026-11-18/19. Gratas: in karate the arms "burn" so much that holding the guard at the head
gets hard and the legs run out of energy. His fights: 3 min main time + up to three 2-min extensions (9 min at most).
A first version with light 30-60 s finishers was too easy for his karate volume, so every block is harder than a fight:
Tabata intervals for the legs, punch-outs and a heavy guard hold for the arms, and a fight simulation (main time, then
extensions after a 30 s pause like the judges' decision). The fight follows his own fights (2026-11-20): minute 1
mostly single strikes, minute 2 series of 3-4, minute 3 series of 5-6, the last 30 s non-stop at full power and
speed (an extension: 3-4, then 5-6, the last 30 s non-stop); after every minute 10 s of burpees at full
speed (his ask, same day), alternating knees in the variant; the app's timer runs these parts itself (field segments). Always after the speed/strength work, before the automatic
hip release; every finisher has a variant (alternates like the rest).

  karate-power   A legs Tabata 8 | B punch-outs 3 + heavy guard 2 | C fight 3 min + 3 x 2 min
  kyokushin-mix  A legs Tabata 6 | B punch-outs 2                  | C fight 3 min + 1 x 2 min
  hard-gym       A fight 3 min + 3 x 2 min | B punch-outs 3 (lower day, arms fresh) | C Tabata 8 (upper day, legs
                 fresh) | D none (long hip day)

Run LAST: add_variants.py -> add_hips.py -> make_hard_gym.py -> make_karate_power.py -> add_endurance.py (the others
rewrite the JSON and drop the finishers). Idempotent: removes its own exercises (by name) and appends them again; the
goal sentence starts with MARK and is replaced. Pictures: tools/draw_endurance.py, reused ones renumbered (rebadge.py).

Usage:  py tools/add_endurance.py
"""
import json
import os

import draw_endurance as de
from rebadge import rebadge

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PROGRAMS = os.path.join(ROOT, "src", "data", "programs")
ASSETS = os.path.join(ROOT, "public", "assets")
REST = 30
PAUSE = 25  # + the engine's 5 s prep = the 30 s pause before an extension
SHORT = 5  # + 5 s prep = 10 s between Tabata intervals
MARK = "Ištvermė pabaigoje"  # start of this script's goal sentence; a re-run replaces it

GUARD_TIP = "Tarp serijų rankos visada gynyboje, iškvėpk su kiekvienu smūgiu, pečiai atpalaiduoti."
EASE = ("Pradžioje tai žiauriai sunku – normalu. Jei krenta smūgių kokybė, pailgink poilsį prieš pratęsimus iki 60 s ir "
        "kas savaitę trumpink: 45 s, 30 s, vėliau 15 s.")
BURPEES, KNEES = "BURPIAI – max greitis!", "KELIAI – max greitis!"
LAST30 = "Be sustojimo – max jėga!"


def main_time(burst):
    """His fight (2026-11-20): minute 1 single strikes, 2 series of 3-4, 3 series of 5-6 with the last 30 s non-stop,
    and 10 s of burpees (or knees) after every minute, as he asked. The app's timer shows each part and beeps."""
    return [("1-a min: pavieniai smūgiai", 60), (burst, 10), ("2-a min: serijos po 3–4", 60), (burst, 10),
            ("3-ia min: serijos po 5–6", 30), (LAST30, 30), (burst, 10)]


def extension(burst):
    """A 2-min extension the same way (my assumption, told him): series of 3-4, then 5-6 with the last 30 s non-stop."""
    return [("1-a min: serijos po 3–4", 60), (burst, 10), ("2-a min: serijos po 5–6", 30), (LAST30, 30), (burst, 10)]


# kind -> (main, variant). draw = pose in draw_endurance, copy = existing picture renumbered.
KINDS = {
    "tabata": (
        dict(name="Jump Squat Intervals", reps="20 s", seconds=20, rest=SHORT, noWeight=True, copy="P_C2.webp",
             description="Intervalai: 20 s kuo daugiau pritūpimų su šuoliu, tada 10 s poilsio (5 s poilsis ir 5 s "
                         "pasiruošimas), ir taip visus setus. Šuolis nebūtinai aukščiausias: svarbu išlaikyti tempą "
                         "iki galo. Nusileisk minkštai ant pirštų, keliai neina į vidų. Skaičiuok pakartojimus ir kas "
                         "savaitę per 20 s padaryk bent vienu daugiau.",
             focus="Ištvermė: kojos neapsunksta per kovą ir pratęsimus."),
        dict(name="Kick Intervals", tag="spyriai", reps="20 s", seconds=20, rest=SHORT, noWeight=True,
             copy="P_A5.webp",
             description="Intervalai su spyriais: 20 s kuo greičiau pakaitomis žemi ir vidutiniai mawashi geri kaire ir "
                         "dešine, 10 s poilsio, ir taip visus setus. Rankos gynyboje, atraminė koja ant pirštų, po "
                         "kiekvieno spyrio koja grįžta į stovėseną. Guma nebūtina, su ja sunkiau.",
             focus="Ištvermė: spyriai išlieka greiti ir pratęsimuose."),
    ),
    "punchout": (
        dict(name="Punch-Outs (hanteliai)", reps="90 s", seconds=90, draw="punch_out",
             description="Kovinė stovėsena, lengvi hanteliai (1–1,5 kg). Kol laikmatis rodo daugiau nei 30 s – greiti "
                         "tiesūs smūgiai pakaitomis be sustojimo, didžiausiu tempu, kurį išlaikai. Paskutinės 30 s – "
                         "gynyba su tais pačiais hanteliais, kumščiai prie skruostų. Alkūnės iki galo netiesink, pečiai "
                         "žemyn, iškvėpk su kiekvienu smūgiu. Kai lengva – sunkesni hanteliai (iki 2 kg) arba +15 s.",
             focus="Ištvermė: rankos ištveria kovos tempą ir po to dar laiko gynybą."),
        dict(name="Banded Punch-Outs", tag="su guma", reps="90 s", seconds=90, noWeight=True, copy="P_B1v.webp",
             description="Guma pritvirtinta už nugaros krūtinės aukštyje, kilpos rankose. Kol laikmatis rodo daugiau "
                         "nei 30 s – greiti tiesūs smūgiai prieš gumą be sustojimo, paskutinės 30 s – gynyba, guma "
                         "įtempta. Pečiai žemyn, iškvėpk su kiekvienu smūgiu.",
             focus="Ištvermė: smūgiai nesilpnėja kovos gale, gynyba nekrenta."),
    ),
    "guard": (
        dict(name="Guard Hold (sunkus)", reps="60 s", seconds=60, draw="guard",
             description="Kovinė stovėsena, kiekvienoje rankoje 2,5–5 kg hantelis. Kumščiai prie skruostų, alkūnės "
                         "žemyn ir arti šonų, pečiai nuleisti. Išlaikyk 60 s; jei gali ilgiau, spausk +15 s ir laikyk, "
                         "kol dar išlaikai teisingą gynybą. Kai dega, atpalaiduok pečius ir lėtai iškvėpk, bet rankų "
                         "nenuleisk. Kai 90 s lengva – sunkesni hanteliai.",
             focus="Ištvermė: rankos išsilaiko gynyboje prie galvos visą kovą."),
        dict(name="Dumbbell Guard Punches", tag="su smūgiais", reps="60 s", seconds=60, draw="guard_punch",
             description="Kovinė stovėsena, hanteliai 2–3 kg. 60 s pakaitomis lėti, kontroliuojami tiesūs smūgiai "
                         "pečių aukštyje: ranka kaskart grįžta į gynybą, kita lieka prie veido. Alkūnės iki galo "
                         "netiesink, iškvėpk su kiekvienu smūgiu.",
             focus="Ištvermė: rankos nekrenta net po ilgų smūgių serijų."),
    ),
    "fight": (
        dict(name="Kova: pagrindinis laikas", reps="3 min + burpiai", seconds=210, segments=main_time(BURPEES),
             rest=PAUSE, noWeight=True, draw="fight",
             description="Kovos simuliacija pagal tavo kovos eigą (jei yra maišas – ant maišo). Laikmatis pats rodo, ką "
                         "daryti, ir pypteli, kai keičiasi: 1-a minutė – pavieniai smūgiai, 10 s burpių max greičiu, "
                         "2-a minutė – serijos po 3–4, vėl 10 s burpių, 3-ia minutė – serijos po 5–6, paskutinės 30 s – "
                         "be sustojimo, max jėga ir greitis, ir dar 10 s burpių. Po burpio iškart atgal į stovėseną. "
                         + GUARD_TIP + " Po pagrindinio laiko – pratęsimai, kaip tavo kovose.",
             focus="Ištvermė: kovos tempas, net kai kvėpavimas jau dažnas."),
        dict(name="Kova su kelių smūgiais", tag="keliai", reps="3 min + keliai", seconds=210,
             segments=main_time(KNEES), rest=PAUSE, noWeight=True, draw="fight_kick",
             description="Ta pati kovos eiga, bet vietoj burpių – 10 s kelių smūgių pakaitomis max greičiu, rankos "
                         "gynyboje. Tarp serijų nuolat judi ant pirštų, kad kovos tempą išlaikytų ir kojos. " + GUARD_TIP,
             focus="Ištvermė: kojos neapsunksta per kovą."),
    ),
    "ext": (
        dict(name="Kova: pratęsimai", reps="2 min + burpiai", seconds=140, segments=extension(BURPEES), rest=PAUSE,
             noWeight=True, draw="fight_ext",
             description="Iškart po pagrindinio laiko: pratęsimai po 2 min, prieš kiekvieną 30 s pauzė, kaip laukiant "
                         "teisėjų sprendimo. Laikmatis rodo eigą: 1-a minutė – serijos po 3–4, 10 s burpių, 2-a "
                         "minutė – serijos po 5–6, paskutinės 30 s – be sustojimo, ir dar 10 s burpių. " + GUARD_TIP
                         + " Ilgiausia kova: 3 + 2 + 2 + 2 = 9 min. " + EASE,
             focus="Ištvermė: jėgų užtenka ir pratęsimams, iki 9 min."),
        dict(name="Pratęsimai su kelių smūgiais", tag="keliai", reps="2 min + keliai", seconds=140,
             segments=extension(KNEES), rest=PAUSE, noWeight=True, draw="fight_kick",
             description="Pratęsimai po 2 min su 30 s pauze, ta pati eiga, bet vietoj burpių – 10 s kelių smūgių "
                         "pakaitomis max greičiu. Tarp serijų nuolat judi ant pirštų. " + EASE,
             focus="Ištvermė: jėgų užtenka ir pratęsimams, iki 9 min."),
    ),
}

# program -> (id prefix, picture name, {day: [(kind, sets), ...]}, (old, new) in the goal or None, goal sentence)
PLAN = {
    "karate-power": ("P", "P_{day}{n}{v}.webp",
                     {"A": [("tabata", 8)], "B": [("punchout", 3), ("guard", 2)], "C": [("fight", 1), ("ext", 3)]},
                     ("3 dienos po ~50 min", "3 dienos po ~60 min"),
                     MARK + ": A – šuolių intervalai, B – smūgiai su hanteliais ir sunki gynyba, C – kovos simuliacija "
                     "3 + 2 + 2 + 2 min. Visada po greičio darbo, kad kovoje rankos ir kojos neužsirūgštų."),
    "kyokushin-mix": ("", "{day}_{n}{v}.webp",
                      {"A": [("tabata", 6)], "B": [("punchout", 2)], "C": [("fight", 1), ("ext", 1)]},
                      None,
                      MARK + ": A – šuolių intervalai, B – smūgiai su hanteliais, C – kova 3 + 2 min."),
    "hard-gym": ("G", "G_{day}{n}{v}.webp",
                 {"A": [("fight", 1), ("ext", 3)], "B": [("punchout", 3)], "C": [("tabata", 8)]},
                 None,
                 MARK + ", kad per pertrauką nedingtų karatė kondicija: A – kovos simuliacija 3 + 2 + 2 + 2 min, "
                 "B – smūgiai su hanteliais, C – šuolių intervalai."),
}


def build(spec, ex_id, sets, image):
    out = {"id": ex_id, "name": spec["name"]}
    if "tag" in spec:
        out["tag"] = spec["tag"]
    out.update(sets=sets, reps=spec["reps"], restSeconds=spec.get("rest", REST), image="assets/" + image,
               description=spec["description"], focus=spec["focus"], seconds=spec["seconds"])
    if spec.get("noWeight"):
        out["noWeight"] = True
    if "segments" in spec:
        out["segments"] = [dict(label=label, seconds=sec) for label, sec in spec["segments"]]
    return out


def picture(spec, day, n, image):
    if "draw" in spec:
        de.POSES[spec["draw"]](day, n, image)
    else:
        rebadge(os.path.join(ASSETS, spec["copy"]), os.path.join(ASSETS, image), n)


def check(prog):
    """The limits src/data/programs.ts enforces, so a broken program never reaches the phone."""
    ids = set()
    for day in prog["days"]:
        assert len(day["exercises"]) <= 19, day["id"]  # + the automatic hip release, at most 20
        for ex in day["exercises"]:
            for e in [ex] + ex.get("variants", []):
                assert e["id"] not in ids, ("duplicate id", e["id"])
                ids.add(e["id"])
                assert 1 <= e["sets"] <= 20 and 0 <= e["restSeconds"] <= 900, e["id"]
                assert "seconds" not in e or 5 <= e["seconds"] <= 900, e["id"]
                assert "segments" not in e or sum(p["seconds"] for p in e["segments"]) == e["seconds"], e["id"]
                assert e.get("sides", 1) in (1, 2), e["id"]
                if e.get("bonusSets"):
                    assert e["bonusSets"] < e["sets"] and e.get("startSide") in ("left", "right"), e["id"]
            assert len(ex.get("variants", [])) <= 5, ex["id"]


def main():
    names = {pair[0]["name"] for pair in KINDS.values()}
    for prog_id, (prefix, pattern, days, swap, sentence) in PLAN.items():
        path = os.path.normpath(os.path.join(PROGRAMS, prog_id + ".json"))
        with open(path, encoding="utf-8") as f:
            prog = json.load(f)
        added = []
        for day in prog["days"]:
            exercises = [e for e in day["exercises"] if e["name"] not in names]
            for kind, sets in days.get(day["id"], []):
                n = len(exercises) + 1
                ex_id = f"{prefix}{day['id']}{n}"
                main_spec, var_spec = KINDS[kind]
                image, image_v = (pattern.format(day=day["id"], n=n, v=v) for v in ("", "v"))
                picture(main_spec, day["id"], n, image)
                picture(var_spec, day["id"], n, image_v)
                ex = build(main_spec, ex_id, sets, image)
                ex["variants"] = [build(var_spec, ex_id + "v", sets, image_v)]
                exercises.append(ex)
                added.append(f"{ex_id} {main_spec['name']} {sets}x{main_spec['reps']}")
            day["exercises"] = exercises
        goal = prog.get("goal", "").split(" " + MARK)[0].rstrip()
        if swap:
            goal = goal.replace(*swap)
        prog["goal"] = goal.rstrip(".") + ". " + sentence
        check(prog)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(prog, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("wrote", path, "|", "; ".join(added))


if __name__ == "__main__":
    main()
