"""Hip work for src/data/programs/kyokushin-mix.json (idempotent: replaces what it added before).

- `warmup` of every day: a ~8 min guided whole-body warm-up, top down (pictures from tools/draw_hips.py);
  lower-body days get the extra hip drills, upper-body days the scapular push-ups.
- Exercise 10 of every day: one hip strength exercise (Copenhagen plank, kick hold, Cossack squat).
- `startSide` on one-sided exercises: the user's weaker side first (legs: left, chest: right).

warmup_for() is also used by tools/make_hard_gym.py.
"""
import json

PATH = r"D:\Kyokushin\src\data\programs\kyokushin-mix.json"

def _w(key, name, hold, sides, description, focus):
    return dict(id=f"W_{key}", name=name, hold=hold, sides=sides, image=f"assets/W_{key}.webp",
                description=description, focus=focus)


WARMUP_ITEMS = {
    "jacks": _w("jacks", "Jumping Jacks (šuoliukai)", 40, 1,
                "Šokinėk: kojos į šonus ir rankos virš galvos, tada atgal. Lengvai, ant pirštų, ritmingai. Tikslas – sušilti ir pakelti pulsą, ne pavargti.",
                "visas kūnas sušyla, širdis įsibėgėja prieš krūvį"),
    "arm_circles": _w("arm_circles", "Arm Circles (rankų sukimai)", 30, 1,
                      "Rankos tiesios į šonus. Suk didelius ratus: 15 s pirmyn, 15 s atgal, kaskart kiek didesnius. Pečiai žemyn, liemuo nejuda.",
                      "pečių sąnariai prieš spaudimą, traukimą ir smūgius"),
    "cat_cow": _w("cat_cow", "Cat-Cow (katė–karvė)", 30, 1,
                  "Keturpėsčias, rankos po pečiais, keliai po klubais. Iškvėpdamas apvalink nugarą ir nuleisk galvą, įkvėpdamas išlenk nugarą ir žiūrėk pirmyn. Lėtai, per visą stuburą.",
                  "stuburo mobilumas prieš pritūpimus ir kėlimus"),
    "tspine": _w("tspine", "T-Spine Rotation (krūtinės sukimas)", 25, 2,
                 "Keturpėsčias, vieną ranką dėk už galvos. Alkūnę vesk po kūnu link kitos rankos, tada suk ją į lubas, akys seka alkūnę. Klubai nejuda.",
                 "krūtinės stuburo sukimas: smūgiams, spyriams ir tiesiai nugarai po štanga"),
    "scap_pushup": _w("scap_pushup", "Scapular Push-Ups (menčių atsispaudimai)", 30, 1,
                      "Plankos padėtis ant tiesių rankų. Nelenkdamas alkūnių leisk krūtinę žemyn, kad mentės susiglaustų, tada stumk grindis nuo savęs, kol nugara tarp menčių apvali. Mažas judesys, lėtai.",
                      "mentės ir serratus prieš spaudimą"),
    "inchworm": _w("inchworm", "Inchworm (vikšras)", 40, 1,
                   "Stovėdamas pasilenk, delnus dėk ant grindų ir eik rankomis pirmyn iki plankos. Vienas atsispaudimas, tada smulkiais žingsniais eik pėdomis prie rankų, kojas laikydamas kuo tiesesnes. Kartok.",
                   "pakinkliai, pečiai ir presas vienu judesiu"),
    "hip_cars": _w("hip_cars", "Hip CARs (klubo sukimai)", 20, 2,
                   "Stovėk ant vienos kojos ir prisilaikyk. Kitą kelį pakelk ir lėtai brėžk kuo didesnį ratą: pirmyn, į šoną, atgal ir žemyn. Liemuo nejuda, juda tik klubas.",
                   "valdomas judesys per visą klubo amplitudę"),
    "leg_swings": _w("leg_swings", "Leg Swings (kojos mostai)", 20, 2,
                     "Prisilaikyk ir mosuok tiesia koja pirmyn ir atgal, po to į šonus priešais save. Kas kartą šiek tiek aukščiau, liemuo tiesus.",
                     "dinamiškas klubų apšilimas prieš sunkius pratimus ir spyrius"),
    "9090": _w("9090", "90/90 Hip Switch", 30, 1,
               "Sėsk ant grindų, abu keliai sulenkti 90°: viena koja priekyje, kita šone. Nekeldamas pėdų lėtai versk kelius į kitą pusę ir atgal. Nugara tiesi, rankomis gali atsiremti.",
               "klubo vidinė ir išorinė rotacija"),
    "cossack": _w("cossack", "Cossack Squat (savo svoris)", 30, 1,
                  "Plačiai išsižergk. Leiskis ant vienos kojos, kita lieka tiesi, pirštai į viršų. Pakaitomis į abi puses, kulnas prie žemės, kiek leidžia klubai.",
                  "pritraukiamieji raumenys ir šoninis mobilumas"),
    "wgs": _w("wgs", "World's Greatest Stretch", 20, 2,
              "Didelis įtūpstas, ranka į grindis prie priekinės pėdos, kita ranka sukasi į lubas. Judėk ritmingai: alkūnė link pėdos, sukimas į viršų.",
              "klubų lenkiamieji ir krūtinės pasukimas"),
    "deep_squat": _w("deep_squat", "Deep Squat Hold (gilus pritūpimas)", 30, 1,
                     "Leiskis į gilų pritūpimą, kulnai prie žemės. Alkūnėmis švelniai stumk kelius į šonus ir lėtai linguok iš kairės į dešinę.",
                     "klubų ir čiurnų mobilumas pritūpimui"),
}

# Order of the whole-body warm-up, top down. Some drills only on upper- or lower-body days; a full-body day gets both.
WARMUP_ORDER = [
    ("jacks", "upper lower full"), ("arm_circles", "upper lower full"), ("cat_cow", "upper lower full"),
    ("tspine", "upper lower full"), ("scap_pushup", "upper full"), ("inchworm", "upper lower full"),
    ("hip_cars", "upper lower full"), ("leg_swings", "upper lower full"), ("9090", "lower"),
    ("cossack", "lower full"), ("wgs", "upper lower full"), ("deep_squat", "upper lower full"),
]

# What each Kyokushin day mostly trains (A legs, B upper body, C both).
DAY_KIND = {"A": "lower", "B": "upper", "C": "full"}


def warmup_for(kind):
    """The warm-up list of an 'upper', 'lower' or 'full' (both) day, as fresh dicts."""
    return [dict(WARMUP_ITEMS[key]) for key, kinds in WARMUP_ORDER if kind in kinds.split()]

# Every hip slot has a weighted/strength version and a bodyweight mobility-strength variant; the app alternates them.
HIP_VARIANT = {
    "A": dict(id="A10v", name="90/90 Hip Lift", tag="kūno svoris", sets=3, reps="6 / pusė", restSeconds=45, startSide="left",
              image="assets/A_10v.webp",
              description="Sėsk ant grindų, abu keliai sulenkti 90°: viena koja priekyje, kita šone. Įtempk sėdmenis ir kelk užpakalį nuo žemės, keliai lieka ant grindų. Pauzė viršuje, lėtai žemyn. Jei nepavyksta pakelti: atsiremk rankomis už nugaros ir kelk tiek, kiek gali, arba tik įtempk sėdmenį 5 s.",
              focus="Klubo rotacija su jėga: sėdmenys ir pritraukiamieji amplitudės gale."),
    "B": dict(id="B10v", name="Hip Airplane", tag="kūno svoris", sets=3, reps="5 / koja", restSeconds=45, startSide="left",
              image="assets/B_10v.webp",
              description="Stovėk ant vienos kojos, pasilenk kaip vienos kojos RDL, kita koja tiesi atgal, rankos į šonus. Lėtai suk klubus į išorę (laisvos kojos pusė kyla), tada į vidų, kol dubuo lygus. Kelis nejuda.",
              focus="Klubo rotacija ir pusiausvyra: sėdmuo valdo kelį."),
    "C": dict(id="C10v", name="Kiba Dachi Hold", tag="kūno svoris", sets=3, reps="45 s", seconds=45, restSeconds=45,
              image="assets/C_10v.webp",
              description="Plati stovėsena, pėdos lygiagrečios, šlaunys beveik lygiagrečios žemei. Keliai stumiami į išorę virš pėdų, kumščiai prie klubų, nugara tiesi. Laikyk ir ramiai kvėpuok.",
              focus="Karatė stovėsena: klubų ir šlaunų jėga be svorio."),
}

HIP_EXERCISE = {
    "A": dict(id="A10", name="Copenhagen Plank", sets=3, reps="20 s / pusė", seconds=20, sides=2, restSeconds=45,
              image="assets/A_10.webp",
              description="Šoninė planka ant dilbio: viršutinės kojos vidinė pusė ant suolo, apatinė koja laisva po suolu. Pakelk klubus, kad kūnas būtų tiesus, ir išlaikyk. Per sunku: dėk ant suolo kelį, ne pėdą.",
              focus="Pritraukiamieji raumenys: stabilesnis dubuo, mažiau kirkšnies traumų.", variants=[HIP_VARIANT["A"]]),
    "B": dict(id="B10", name="Standing Kick Hold", sets=3, reps="15 s / koja", seconds=15, sides=2, restSeconds=45,
              startSide="left", image="assets/B_10.webp",
              description="Stovėk tiesiai, rankos sargyboje. Pakelk tiesią koją priešais save kuo aukščiau, nesilenkdamas atgal, ir išlaikyk. Pradžioje gali prisilaikyti sienos.",
              focus="Aktyvus lankstumas: klubo lenkiamųjų jėga aukštiems spyriams.", variants=[HIP_VARIANT["B"]]),
    "C": dict(id="C10", name="Cossack Squat (kettlebell)", sets=3, reps="6 / pusė", restSeconds=60, startSide="left",
              image="assets/C_10.webp",
              description="Kettlebell prie krūtinės, plačiai išsižergk. Leiskis ant vienos kojos kuo žemiau, kita tiesi, pirštai į viršų. Kulnas prie žemės, krūtinė pakelta.",
              focus="Dubens mobilumas su svoriu: jėga amplitudės gale.", variants=[HIP_VARIANT["C"]]),
}

# Weak-side-only extra sets: every one-sided exercise with startSide gets one more set for the weaker side.
BONUS_SETS = 1

# The user's weaker sides: left leg, right chest, right side of the back, left arm.
START_SIDE = {
    "A3v": "left",   # Single-Leg RDL
    "A4": "left", "A4v": "left",   # Bulgarian Split Squat, Goblet Reverse Lunge
    "A5": "left",    # Explosive Step-Up
    "A6v": "left",   # Single-Leg Calf Raise
    "B4": "right", "B4v": "right",   # Landmine Press, Half-Kneeling Kettlebell Press (chest)
    "C4": "left", "C4v": "left",   # Walking Lunges, Lateral Lunge
}


def main():
    with open(PATH, encoding="utf-8") as f:
        prog = json.load(f)
    for day in prog["days"]:
        day["warmup"] = warmup_for(DAY_KIND[day["id"]])
        # keep key order: warmup before stretches
        stretches = day.pop("stretches", None)
        if stretches is not None:
            day["stretches"] = stretches
        ex = HIP_EXERCISE[day["id"]]
        day["exercises"] = [e for e in day["exercises"] if e["id"] != ex["id"]] + [json.loads(json.dumps(ex))]
        for e in day["exercises"]:
            for v in [e] + e.get("variants", []):
                if v["id"] in START_SIDE:
                    v["startSide"] = START_SIDE[v["id"]]
                if v.get("startSide") and not v.get("bonusSets"):
                    v["sets"] = v["sets"] + BONUS_SETS
                    v["bonusSets"] = BONUS_SETS
    with open(PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(prog, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("updated", PATH)


if __name__ == "__main__":
    main()
