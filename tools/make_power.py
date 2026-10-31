"""Writes src/data/programs/karate-power.json: the karate power program (explosiveness and speed only, no muscle building).

3 days: A legs (jumps, kick speed), B upper body (punch power, hand speed), C whole body (hip snap, starts, footwork).
Everything is ballistic: jumps, throws, speed sets of punches and kicks, light loads, few reps, full rests;
no heavy or high-rep lifting. The whole-body warm-up (tools/add_hips.py) opens every workout, cool-downs come from
the Kyokushin program, one-sided exercises start with the weaker side and get an extra set for it.

Pictures: new drawings from tools/draw_power.py (P_<day><n>[v].webp); exercises taken over from the other programs
keep their pictures, copied with the right corner number by tools/rebadge.py when the position differs.

Usage:  py tools/make_power.py
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

KEEP = ("name", "tag", "image", "description", "focus", "seconds", "sides", "fast", "startSide")
BONUS_SETS = 1  # extra set for the weaker side on every one-sided exercise
copies = []


def badge_of(image):
    """The corner number a picture carries: A_5v.webp → 5, P_B4v.webp → 4."""
    return int(re.search(r"_[A-Z]?(\d+)v?\.webp$", image).group(1))


def picture(src, day, n, variant):
    """Image path for a reused picture at position n: the original if its number matches, else a renumbered copy."""
    src = src.replace(".png", ".webp")
    if badge_of(src) == n:
        return src
    dst = f"assets/P_{day}{n}{'v' if variant else ''}.webp"
    copies.append((src, dst, n))
    return dst


def ex(day, n, name, sets, reps, rest, description, focus, variant=False, image=None, **extra):
    """A new exercise; its picture is P_<day><n>[v].webp unless `image` names a reused one."""
    pid = f"P{day}{n}{'v' if variant else ''}"
    img = picture(image, day, n, variant) if image else f"assets/P_{day}{n}{'v' if variant else ''}.webp"
    return {"id": pid, "name": name, "sets": sets, "reps": reps, "restSeconds": rest, "image": img,
            "description": description, "focus": focus, **extra}


def reuse(src_id, day, n, sets, reps, rest, variant=False, **extra):
    """An exercise taken over from the Kyokushin program (texts and picture), with new sets, reps and rest."""
    e = {k: copy.deepcopy(v) for k, v in by_id[src_id].items() if k in KEEP}
    e["image"] = picture(by_id[src_id]["image"], day, n, variant)
    e.update(sets=sets, reps=reps, restSeconds=rest, **extra)
    return {"id": f"P{day}{n}{'v' if variant else ''}", **e}


def with_variants(e, *variants):
    e["variants"] = list(variants)
    return e


SPEED = dict(seconds=10, sides=2, fast=True)  # 10 s of fast kicks / punches per side

MAE = ("Speed Mae Geri (greiti spyriai)",
       "Kovinė stovėsena, į maišą arba orą. Per 10 s kuo daugiau pilnų mae geri ta pačia koja: kelis aukštai, spyris, "
       "greitas atitraukimas ir pėda atgal į stovėseną. Greitis svarbiau už jėgą; jei technika byra – truputį lėčiau.",
       "Spyrio greitis ir atitraukimas: aštrumas, ne jėga.")
MAWASHI = ("Speed Mawashi Geri (greiti spyriai)",
           "Kovinė stovėsena, į maišą arba orą. Per 10 s kuo daugiau mawashi geri ta pačia koja: kelis aukštai į šoną, "
           "klubas pasisuka, atraminė pėda sukasi, spyris ratu ir greitai atgal į stovėseną.",
           "Klubo sukimo greitis: mawashi geri.")
LATERAL = ("Lateral Bound (šoniniai šuoliai)",
           "Pritūpk ant vienos kojos ir atsispirk į šoną kuo toliau. Nusileisk ant kitos kojos sulenktu keliu ir sustok "
           "1 s (įsitvirtink, kelis virš pėdos). 4 atsispyrimai viena koja, tada kita.",
           "Šoninis atsispyrimas ir stabdymas: tai sabaki, išėjimas iš linijos.")
SHADOW = ("Shadow Speed Punches (šešėlio smūgiai)",
          "20 s šešėlio kova maksimaliu greičiu: tiesūs smūgiai pakaitomis, pilna amplitudė, kumštis iš karto atgal "
          "prie smakro, iškvėpimas su kiekvienu smūgiu. Kojos lengvos, ant pirštų.",
          "Greitis be pasipriešinimo: rankos dirba, pečiai laisvi.")
LANDMINE_ROT = ("Landmine Rotation (landmine sukimai)",
                "Štangos galas abiem rankom, rankos tiesios prieš krūtinę, plati stovėsena. Greitai suk klubus ir perkelk "
                "štangą lanku į vieną šoną iki klubo aukščio, tada sprogstamai į kitą. Rankos tiesios, sukasi klubai ir "
                "pėdos, ne pečiai. Svoris lengvas.",
                "Klubų sukimo greitis: mawashi geri, uraken ir gyaku-zuki.")

A = [
    with_variants(
        ex("A", 1, "Depth Jump (nušokimas ir atšokimas)", 4, "3", 120,
           "Dėžė 30–45 cm. Nulipk (ne nušok) žemyn, nusileisk abiem kojomis ir tą pačią akimirką atšok kuo aukščiau. "
           "Kontaktas su žeme kuo trumpesnis, kulnai žemės neliečia. Jei kontaktas ilgėja ar šuolis žemėja – setas baigtas.",
           "Reaktyvi jėga: trumpas kontaktas = greitesnis startas ir spyris."),
        reuse("A1", "A", 1, 4, "3", 90, True, tag="ant dėžės")),
    with_variants(
        ex("A", 2, "Hurdle Hops (šuoliai per kliūtis)", 4, "4", 90,
           "4 žemos kliūtys (ar linijos) iš eilės, 60–80 cm viena nuo kitos. Šok per visas abiem kojomis be sustojimo: "
           "žemė tik atspirtis, rankos padeda. Aukštis toks, kad kontaktas liktų trumpas ir tylus.",
           "Serijinis sprogstamumas: kombinacijos ir šuoliai spyriams."),
        reuse("A1v", "A", 2, 4, "3", 90, True, name="Continuous Broad Jumps (šuoliai į tolį)", tag="į tolį",
              description="3 šuoliai į tolį iš eilės: nusileidęs iš karto šok vėl, be pauzės. Rankų mostas, minkštas nusileidimas, "
                          "paskutinį sustabdyk 1 s.",
              focus="Horizontalus sprogstamumas: įėjimas į distanciją.")),
    with_variants(
        ex("A", 3, "Trap-Bar Jump (šuolis su trap štanga)", 4, "3", 120,
           "Trap štanga tuščia arba iki 20–30 % savo svorio. Pritūpk, suimk rankenas, nugara tiesi, ir sprogstamai šok "
           "aukštyn – štanga lieka rankose, rankos tiesios. Nusileisk minkštai, persistatyk, kartok. Šuolis žemėja – mažink svorį.",
           "Jėgos greitis klubams: spyrio, žingsnio ir metimo variklis."),
        reuse("C1", "A", 3, 4, "4", 90, True, tag="be svorio")),
    with_variants(
        ex("A", 4, "Banded Knee Drive (kelio kėlimas su guma)", 4, "6 / koja", 75,
           "Guma už čiurnos, pritvirtinta žemai už nugaros. Stovėk ant vienos kojos, rankos sargyboje, ir sprogstamai mesk "
           "kelį aukštyn kaip hiza geri. Grįžimą kontroliuok, liemuo nesilenkia atgal. Guma lengva – greitis svarbiau už pasipriešinimą.",
           "Klubo lenkiamųjų greitis: mae geri ir hiza geri startas.", startSide="left"),
        reuse("A5", "A", 4, 4, "5 / koja", 75, True, tag="ant dėžės", startSide="left")),
    with_variants(
        ex("A", 5, LATERAL[0], 4, "4 / pusė", 90, LATERAL[1], LATERAL[2], startSide="left"),
        reuse("A5v", "A", 5, 3, "4 / koja", 90, True, tag="kojų keitimas")),
    with_variants(
        ex("A", 6, MAE[0], 4, "10 s / koja", 60, MAE[1], MAE[2], startSide="left", **SPEED),
        ex("A", 6, MAWASHI[0], 4, "10 s / koja", 60, MAWASHI[1], MAWASHI[2], True, image="assets/P_C5.webp",
           tag="mawashi", startSide="left", **SPEED)),
    ex("A", 7, "Pogo Jumps (šuoliukai ant pirštų)", 3, "15", 60,
       "Kojos beveik tiesios, šokinėk vietoje tik čiurnomis: kulnai neliečia žemės, kontaktas kuo trumpesnis, aukštis "
       "vidutinis. Kaip spyruoklė, ritmingai.",
       "Čiurnos standumas: greitesnis žingsnis ir atsispyrimas."),
]

B = [
    with_variants(
        ex("B", 1, "Medicine Ball Chest Pass (metimas į sieną)", 4, "5", 90,
           "Kamuolys 3–5 kg, stovėk 1,5–2 m nuo sienos, viena koja priekyje. Žingsnis pirmyn ir sprogstamai mesk kamuolį nuo "
           "krūtinės į sieną abiem rankomis, pagauk atšokusį ir kartok. Jėga iš kojų per liemenį į rankas, ne vien rankomis.",
           "Tsuki galia: kojos, klubai ir rankos vienu metu."),
        reuse("B6", "B", 1, 4, "5", 90, True, name="Clap Push-Ups (su plojimu)", tag="su plojimu",
              description="Atsispaudimo padėtis. Leiskis kontroliuojamai ir sprogstamai stumk, kad delnai atsiplėštų nuo žemės ir "
                          "spėtum suploti. Nusileisk minkštai ant sulenktų rankų. Jei plojimas nepavyksta – tiesiog atsiplėšk nuo žemės.",
              focus="Rankų ir krūtinės sprogstamumas: smūgio startas.")),
    with_variants(reuse("B1", "B", 2, 4, "4 / pusė", 90), reuse("B1v", "B", 2, 4, "6 / pusė", 75, True)),
    with_variants(
        ex("B", 3, "Landmine Punch Press (sprogstamas spaudimas)", 4, "4 / ranka", 90,
           "Štangos galas prie peties, priešinga koja priekyje kaip kovinėje stovėsenoje. Sukdamas klubus ir užpakalinę pėdą "
           "sprogstamai „smūgiuok“ štangą pirmyn-aukštyn, kol ranka tiesi. Lėtai grąžink prie peties. Svoris lengvas "
           "(tuščia štanga arba +5–10 kg), greitis maksimalus.",
           "Gyaku-zuki: klubo sukimas ir rankos ištiesimas vienu judesiu.", startSide="right"),
        reuse("C3", "B", 3, 4, "3", 120, True, tag="abiem rankom")),
    with_variants(
        reuse("B1v", "B", 4, 4, "10 s / ranka", 60, name="Band Speed Punches (greiti smūgiai su guma)",
              description="Lengva guma už nugaros per petį arba pritvirtinta už tavęs. Per 10 s kuo daugiau gyaku-zuki ta pačia "
                          "ranka: pilnas klubo sukimas, ranka iki galo ir greitas atitraukimas (hikite). Guma lengva – greitis "
                          "svarbiau nei pasipriešinimas.",
              focus="Rankos greitis ir atitraukimas: aštrus smūgis.", startSide="right", **SPEED),
        ex("B", 4, SHADOW[0], 3, "20 s", 60, SHADOW[1], SHADOW[2], True, tag="be gumos", seconds=20, fast=True)),
    with_variants(reuse("C6", "B", 5, 4, "5", 75), reuse("C6v", "B", 5, 3, "5 / pusė", 75, True)),
    ex("B", 6, LANDMINE_ROT[0], 3, "6 / pusė", 75, LANDMINE_ROT[1], LANDMINE_ROT[2]),
    with_variants(
        reuse("B3", "B", 7, 4, "3", 90, name="Explosive Pull-Ups (sprogstami prisitraukimai)",
              description="Iš pilno kabėjimo trauk kuo greičiau, kad krūtinė kiltų link skersinio, viršuje rankos gali net "
                          "atsiplėšti. Leiskis kontroliuojamai, apačioje pilnas ištiesimas. Jei greitis krenta – setas baigtas.",
              focus="Hikite ir traukimo galia: atitraukianti ranka greitina smūgį."),
        reuse("B3v", "B", 7, 4, "5", 90, True, name="Band-Assisted Explosive Pull-Ups", tag="su guma",
              description="Pėda gumoje. Kiekvienas prisitraukimas kuo greičiau aukštyn, krūtinė link skersinio, kontroliuojamai "
                          "žemyn. Guma leidžia išlaikyti greitį iki paskutinio kartojimo.",
              focus="Hikite ir traukimo galia: greitis, ne kartojimų skaičius.")),
]

C = [
    with_variants(
        ex("C", 1, "Kettlebell Swing (svyravimas)", 5, "8", 75,
           "Kettlebell tarp kojų, klubai atgal, nugara tiesi. Sprogstamai ištiesk klubus – svoris skrieja iki krūtinės "
           "aukščio, rankos tik laiko, ne kelia. Viršuje sėdmenys įtempti, apačioje klubai atgal (ne pritūpimas). "
           "Kiekvienas mostas maksimaliai staigus.",
           "Klubų ištiesimo greitis: kiekvieno smūgio ir spyrio pradžia."),
        ex("C", 1, "Medicine Ball Scoop Toss (metimas atgal)", 4, "4", 90,
           "Kamuolys 3–5 kg tarp kojų, pritūpk. Vienu judesiu ištiesk kojas, klubus ir rankas ir mesk kamuolį per galvą "
           "atgal kuo toliau (arba į sieną už nugaros). Visas kūnas sprogsta aukštyn.",
           "Viso kūno ištiesimas: jėga iš kojų į viršų.", True, tag="metimas atgal")),
    with_variants(
        ex("C", 2, "Shuttle Sprint (greitėjimai 10 m)", 5, "2 × 10 m", 75,
           "Iš kovinės stovėsenos sprogstamai startuok 10 m pirmyn, paliesk liniją ranka, apsisuk ir sprintu atgal. "
           "Pirmi 3 žingsniai – viskas. Poilsis pilnas, kad kiekvienas startas būtų maksimalus.",
           "Startas iš vietos ir krypties keitimas: įėjimas į distanciją ir išėjimas."),
        ex("C", 2, "Fast Feet (greitos pėdos)", 4, "10 s", 60,
           "Žema kovinė stovėsena ant pirštų. Per 10 s kuo greičiau tapsėk pėdomis vietoje, keliai minkšti, rankos "
           "sargyboje. Pėdos kyla vos nuo žemės.",
           "Pėdų dažnis: greitesnis kojų darbas ir atsitraukimas.", True, tag="vietoje", seconds=10, fast=True)),
    with_variants(
        ex("C", 3, "Tuck Jump (šuolis pritraukiant kelius)", 4, "4", 90,
           "Iš lengvo pritūpimo šok kuo aukščiau ir viršuje greitai trauk kelius prie krūtinės. Nusileisk minkštai ant "
           "pirštų, persistatyk ir kartok. Kiekvienas šuolis maksimalus.",
           "Kelių greitis aukštyn: hiza geri ir šuoliniai spyriai (tobi geri)."),
        reuse("A1", "C", 3, 4, "3", 90, True, tag="ant dėžės")),
    with_variants(
        reuse("A5v", "C", 4, 3, "4 / koja", 90),
        ex("C", 4, LATERAL[0], 4, "4 / pusė", 90, LATERAL[1], LATERAL[2], True, image="assets/P_A5.webp",
           tag="į šoną", startSide="left")),
    with_variants(
        ex("C", 5, MAWASHI[0], 4, "10 s / koja", 60, MAWASHI[1], MAWASHI[2], startSide="left", **SPEED),
        ex("C", 5, MAE[0], 4, "10 s / koja", 60, MAE[1], MAE[2], True, image="assets/P_A6.webp", tag="mae geri",
           startSide="left", **SPEED)),
    with_variants(
        reuse("C6v", "C", 6, 3, "5 / pusė", 75),
        ex("C", 6, LANDMINE_ROT[0], 3, "6 / pusė", 75, LANDMINE_ROT[1], LANDMINE_ROT[2], True, image="assets/P_B6.webp",
           tag="landmine")),
    ex("C", 7, "Shadow Speed Combos (šešėlio kombinacijos)", 3, "20 s", 60,
       "20 s kuo greičiau: du smūgiai + spyris, keisk puses. Pilna amplitudė, greitas grįžimas į sargybą, iškvėpimas su "
       "kiekvienu smūgiu. Paskutinis pratimas: perkelk greitį į techniką.",
       "Greitis kombinacijose: be pauzių tarp technikų.", image="assets/P_B4v.webp", seconds=20, fast=True),
]

LOWER, UPPER, FULL = stretches_of["A"], stretches_of["B"], stretches_of["C"]
program = {
    "id": "karate-power",
    "programName": "Karatė: sprogstamumas ir greitis",
    "focus": "Sprogstamumas, greitis, aštrumas",
    "goal": "Grynai karatė: šuoliai, metimai, sprogstami smūgiai ir spyriai, jokio masės auginimo. Mažai kartojimų "
            "(3–6 arba 10 s greičio), svoriai lengvi arba jokių, pilnas poilsis tarp setų ir kiekvienas kartojimas "
            "maksimaliu greičiu. Setą baik, kai greitis krenta – nuovargis čia ne tikslas. Prieš kiekvieną treniruotę "
            "viso kūno apšilimas, vienpusiai pratimai pradedami silpnesne puse ir gauna papildomą setą tik jai.",
    "days": [
        {"id": "A", "name": "A DIENA", "subtitle": "Kojos · šuoliai ir spyrių greitis", "warmup": warmup_for("lower"), "exercises": A, "stretches": LOWER},
        {"id": "B", "name": "B DIENA", "subtitle": "Viršus · smūgio galia ir rankų greitis", "warmup": warmup_for("upper"), "exercises": B, "stretches": UPPER},
        {"id": "C", "name": "C DIENA", "subtitle": "Visas kūnas · reakcija ir kojų darbas", "warmup": warmup_for("full"), "exercises": C, "stretches": FULL},
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
