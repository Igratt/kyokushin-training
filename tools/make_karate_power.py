"""Writes src/data/programs/karate-power.json: a power program for karate only (no muscle building).

3 days, ~50 min with the warm-up: A lower body + kicks, B upper body + punches, C whole body + reaction.
Rules: few reps (2–6) at maximum speed, long rests so every rep is fast, stop the set when the speed drops.
Speed of punches and kicks with bands, reaction starts and footwork, jumps, throws and fast lifts.
The user's weaker side first on one-sided exercises (legs and arms: left, chest pushes: right) plus one extra
set for that side only, like the other programs.

Exercises taken over from the Kyokushin program keep their descriptions and pictures (renumbered copies via
tools/rebadge.py as P_<day><n>[v].webp when the corner number differs). New pictures: tools/draw_power.py.

Usage:  py tools/make_karate_power.py
"""
import copy
import json
import os
import re

from add_hips import warmup_for
from rebadge import rebadge

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MIX = os.path.join(ROOT, "src", "data", "programs", "kyokushin-mix.json")
OUT = os.path.join(ROOT, "src", "data", "programs", "karate-power.json")

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
BONUS_SETS = 1
copies = []


def picture(src_id, day, n, variant):
    src = by_id[src_id]["image"].replace(".png", ".webp")
    old_n = int(re.match(r"[A-Z](\d+)", src_id).group(1))
    if old_n == n:
        return src
    dst = f"assets/P_{day}{n}{'v' if variant else ''}.webp"
    copies.append((src, dst, n))
    return dst


def reuse(src_id, day, n, sets, reps, rest, variant=False, **extra):
    e = {k: copy.deepcopy(v) for k, v in by_id[src_id].items() if k in KEEP}
    e["image"] = picture(src_id, day, n, variant)
    e.update(sets=sets, reps=reps, restSeconds=rest, **extra)
    return {"id": f"P{day}{n}{'v' if variant else ''}", **e}


def new(day, n, name, sets, reps, rest, description, focus, **extra):
    return {"id": f"P{day}{n}", "name": name, "sets": sets, "reps": reps, "restSeconds": rest,
            "image": f"assets/P_{day}{n}.webp", "description": description, "focus": focus, **extra}


def newv(day, n, name, tag, sets, reps, rest, description, focus, **extra):
    return {"id": f"P{day}{n}v", "name": name, "tag": tag, "sets": sets, "reps": reps,
            "restSeconds": rest, "image": f"assets/P_{day}{n}v.webp", "description": description, "focus": focus, **extra}


def with_variants(e, *variants):
    e["variants"] = list(variants)
    return e


FAST = " Kiekvienas kartojimas maksimaliu greičiu; kai greitis krenta, setą baik."

A = [
    with_variants(new("A", 1, "Pogo Hops", 3, "15 s", 60,
        "Stovėk ant pirštų, keliai beveik tiesūs. Šokinėk vietoje greitai ir žemai, kulnai neliečia žemės, "
        "pėdos ant žemės kuo trumpiau. Rankos padeda ritmui.",
        "Kulkšnių spyruoklė: greitesnis atsispyrimas judant kovoje.", seconds=15),
                  newv("A", 1, "Lateral Pogo Hops", "į šonus", 3, "15 s", 60,
                       "Kojos kartu, ant pirštų. Šokinėk greitai ir žemai į šonus per liniją (kairė–dešinė), pėdos ant žemės kuo trumpiau, kulnai neliečia žemės.",
                       "Kulkšnių spyruoklė ir šoninis kojų greitis.", seconds=15)),
    with_variants(reuse("A1", "A", 2, 4, "3", 90, focus="Maksimalus aukštis, pilnas poilsis tarp šuolių."),
                  reuse("A1v", "A", 2, 4, "3", 90, True)),
    with_variants(new("A", 3, "Lateral Bound", 3, "4 / koja", 75,
        "Stovėk ant vienos kojos, pritūpk ir sprogstamai atsispirk į šoną. Nusileisk ant kitos kojos minkštai, "
        "kelis virš pėdos, ir sustok 1 s. Pradėk kaire koja (atsispiria kairė)." + FAST,
        "Šoninis sprogstamumas: greitas išėjimas iš linijos ir kampo keitimas.", startSide="left"),
                  newv("A", 3, "Lateral Hurdle Hops", "per kliūtį", 3, "6", 75,
                       "Žema kliūtis (kūgis, žemas suolelis ar susuktas rankšluostis) šone. Abiem kojom peršok į šoną ir iškart atgal, nusileisk minkštai ant pirštų ir kuo greičiau atšok." + FAST,
                       "Šoninis sprogstamumas abiem kojom: greitas kampo keitimas.")),
    new("A", 4, "Trap-Bar Jump", 4, "3", 120,
        "Lengva trap-bar štanga (apie 20–30 % tavo trap-bar mirties trauka). Pusiau pritūpk ir šok kuo aukščiau, "
        "nusileisk minkštai sulenktais keliais, sustok, tada kitas šuolis.",
        "Kojų galia su svoriu, bet be lėto kėlimo: greitis, ne masė."),
    with_variants(new("A", 5, "Banded Roundhouse Kick", 3, "6 / koja", 60,
        "Guma prie žemo stulpo ir ant kulkšnies. Kovinė stovėsena: greitas mawashi geri į pilvo aukštį ir iškart "
        "atgal į stovėseną. Svarbu greitis pirmyn ir atgal, ne aukštis." + FAST,
        "Spyrio greitis: klubas ir kelias greičiau išmetami ir grąžinami.", startSide="left"),
                  newv("A", 5, "Banded Front Kick", "mae geri su guma", 3, "6 / koja", 60,
                       "Guma prie žemo stulpo už nugaros ir ant kulkšnies. Kovinė stovėsena: kelį greitai aukštyn, spirk mae geri pirmyn pilvo aukštyje pėdos pagalvėle ir iškart atitrauk atgal." + FAST,
                       "Tiesaus spyrio greitis: kelias ir pėda greičiau pirmyn ir atgal.", startSide="left")),
    with_variants(reuse("A7", "A", 6, 3, "6", 60,
                        description="Kabėk ant skersinio. Kelk kojas sprogstamai aukštyn, nuleisk lėtai, be siūbavimo.",
                        focus="Greitas pilvas ir klubų lenkiamieji: aukštesni, greitesni spyriai."),
                  reuse("A7v", "A", 6, 3, "8", 60, True)),
]

B = [
    with_variants(new("B", 1, "Shadow Speed Punches", 4, "10 s", 50,
        "Kovinė stovėsena, rankos gynyboje. 10 s tiesių smūgių (kairė, dešinė) kuo greičiau, kiekvienas smūgis "
        "grįžta į gynybą. Pečiai atsipalaidavę, kvėpuok trumpai.",
        "Smūgių greitis ir rankų grąžinimas.", seconds=10),
                  newv("B", 1, "Banded Speed Punches", "su guma", 4, "10 s", 50,
                       "Guma pritvirtinta už nugaros krūtinės aukštyje, kilpos rankose. Kovinė stovėsena: 10 s tiesių smūgių kuo greičiau prieš gumą, kiekvienas grįžta į gynybą.",
                       "Smūgių greitis prieš pasipriešinimą ir greitesnis rankos grąžinimas.", seconds=10)),
    with_variants(reuse("B1", "B", 2, 4, "4 / pusė", 90),
                  reuse("C6v", "B", 2, 4, "4 / pusė", 90, True)),
    with_variants(new("B", 3, "Medicine Ball Shot Put", 3, "4 / ranka", 75,
        "Kovinė stovėsena, kamuolys (3–5 kg) vienoje rankoje prie peties. Sukdamas galinę pėdą ir klubus "
        "stumk kamuolį į sieną ar partneriui kaip smūgį. Pradėk dešine (silpnesnė krūtinė)." + FAST,
        "Smūgio galia nuo pėdos per klubus į ranką.", startSide="right"),
                  newv("B", 3, "Medicine Ball Chest Pass", "abiem rankom", 4, "5", 75,
                       "Stovėk prieš sieną, kamuolys (3–5 kg) abiem rankom prie krūtinės. Sprogstamai stumk jį į sieną, pagauk atšokusį ir iškart vėl." + FAST,
                       "Krūtinės ir rankų sprogstamumas abiem pusėm vienodai.")),
    with_variants(reuse("B6", "B", 4, 4, "5", 90, focus="Kuo greičiau atsispirk, delnai atsiplėšia nuo žemės."),
                  reuse("B6v", "B", 4, 4, "5", 90, True)),
    with_variants(reuse("B4", "B", 5, 3, "4 / ranka", 90, name="Landmine Punch Press",
          description="Štangos galas prie peties, kovinė stovėsena. Sprogstamai išstumk į priekį–aukštyn sukdamas "
                      "galinę pėdą, kaip tiesų smūgį, ir kontroliuotai grąžink. Vidutinis svoris, greitis svarbiau."
                      + FAST,
          focus="Smūgio galia su svoriu: pėda, klubai, ranka viena grandine.", startSide="right"),
                  reuse("B4", "B", 5, 3, "6 / ranka", 90, True)),
    with_variants(reuse("B1v", "B", 6, 3, "8 / ranka", 60, startSide="left",
          focus="Smūgio greitis prieš gumą: kairė silpnesnė, todėl pirma."),
                  reuse("B8v", "B", 6, 3, "8 / pusė", 60, True)),
    with_variants(reuse("B3", "B", 7, 3, "4", 120, name="Explosive Pull-Ups",
                        description="Iš kabėjimo trauk sprogstamai, kuo greičiau smakras virš skersinio, "
                                    "nuleisk lėtai. Be svorio, greitis svarbiau.",
                        focus="Greita nugara: subalansuoja smūgius ir greičiau grąžina ranką."),
                  reuse("B3v", "B", 7, 3, "5", 120, True)),
]

C = [
    with_variants(new("C", 1, "Reaction Start Sprint", 6, "5 m", 45,
        "Kovinė stovėsena. Partneris ploja arba numeta daiktą, tu startuoji 5 m sprintu kuo greičiau. "
        "Vienas: pradėk, kai išgirsti bet kokį garsą salėje, arba keisk kryptį (pirmyn, į šonus).",
        "Reakcija ir pirmas žingsnis: greičiau įeini į atstumą ir išeini iš jo."),
                  newv("C", 1, "Falling Start Sprint", "kritimo startas", 6, "5 m", 45,
                       "Stovėk tiesiai, pėdos kartu. Lenkis visu kūnu į priekį, kol pradedi kristi, ir tą akimirką pagauk kritimą sprogstamu 5 m sprintu.",
                       "Pirmas žingsnis ir pagreitis iš vietos.")),
    with_variants(reuse("C1", "C", 2, 4, "3", 90, focus="Maksimalus aukštis, minkštas nusileidimas."),
                  reuse("C1v", "C", 2, 4, "3", 90, True)),
    with_variants(new("C", 3, "Kettlebell Swing", 4, "8", 90,
        "Gira tarp kojų, nugara tiesi, klubai atgal. Sprogstamai stumk klubus pirmyn, gira kyla iki krūtinės "
        "aukščio iš klubų jėgos, ne rankomis. Viršuje įtempk sėdmenis ir pilvą.",
        "Klubų sprogstamumas: tas pats judesys kaip spyrio ir smūgio jėga."),
                  newv("C", 3, "Single-Arm Kettlebell Swing", "viena ranka", 3, "6 / ranka", 90,
                       "Kaip įprastas swing, bet gira vienoje rankoje, kita ranka laisvai juda šone. Klubai atgal, tada sprogstamai pirmyn, gira iki krūtinės. Neleisk liemeniui suktis į giros pusę." + FAST,
                       "Klubų sprogstamumas ir pilvas prieš sukimąsi.", startSide="left")),
    reuse("C3", "C", 4, 4, "3", 120, focus="Greitas kojų ir rankų perdavimas, ne sunkus spaudimas."),
    with_variants(reuse("C6", "C", 5, 3, "5", 60), reuse("C6v", "C", 5, 3, "4 / pusė", 60, True)),
    with_variants(new("C", 6, "Banded Knee Strike", 3, "8 / koja", 60,
        "Guma prie žemo stulpo už nugaros ir ant kelio. Kovinė stovėsena: galinės kojos kelį sprogstamai kelk "
        "aukštyn ir pirmyn (hiza geri), rankos traukia žemyn, tada greitai atgal." + FAST,
        "Kelio smūgio greitis ir klubų lenkiamųjų galia.", startSide="left"),
                  reuse("A5", "C", 6, 3, "4 / koja", 60, True, startSide="left",
                        focus="Kelio pakėlimas su pasipriešinimu: galingesnis hiza geri.")),
    with_variants(reuse("A8", "C", 7, 3, "8 / pusė", 45), reuse("A8v", "C", 7, 3, "8 / pusė", 45, True)),
]

program = {
    "id": "karate-power",
    "programName": "Karatė: sprogstamumas",
    "focus": "Greitis, sprogstamumas, reakcija",
    "goal": "Tik karatė naudai, ne raumenų masei: 3 dienos po ~50 min. Mažai kartojimų maksimaliu greičiu ir "
            "ilgas poilsis, kad kiekvienas kartojimas būtų greitas. Smūgių ir spyrių greitis su guma, reakcijos "
            "startai, šuoliai, metimai ir greiti kėlimai. Kai greitis krenta, setą baik. Silpnesnė pusė pirma ir "
            "gauna papildomą setą.",
    "days": [
        {"id": "A", "name": "A DIENA", "subtitle": "Apačia · spyriai", "warmup": warmup_for("lower"), "exercises": A,
         "stretches": stretches_of["A"]},
        {"id": "B", "name": "B DIENA", "subtitle": "Viršus · smūgiai", "warmup": warmup_for("upper"), "exercises": B,
         "stretches": stretches_of["B"]},
        {"id": "C", "name": "C DIENA", "subtitle": "Visas kūnas · reakcija", "warmup": warmup_for("full"),
         "exercises": C, "stretches": stretches_of["C"]},
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
