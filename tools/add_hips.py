"""Hip work for src/data/programs/kyokushin-mix.json (idempotent: replaces what it added before).

- `warmup` of every day: a 6 min guided hip mobility warm-up (pictures from tools/draw_hips.py).
- Exercise 10 of every day: one hip strength exercise (Copenhagen plank, kick hold, Cossack squat).
- `startSide` on one-sided exercises: the user's weaker side first (legs: left, chest: right).

The warm-up list is also imported by tools/make_hard_gym.py.
"""
import json

PATH = r"D:\Kyokushin\src\data\programs\kyokushin-mix.json"

WARMUP = [
    dict(id="W_hip_cars", name="Hip CARs (klubo sukimai)", hold=30, sides=2, image="assets/W_hip_cars.webp",
         description="Stovėk ant vienos kojos ir prisilaikyk. Kitą kelį pakelk ir lėtai brėžk kuo didesnį ratą: pirmyn, į šoną, atgal ir žemyn. Liemuo nejuda, juda tik klubas.",
         focus="valdomas judesys per visą klubo amplitudę"),
    dict(id="W_leg_swings", name="Leg Swings (kojos mostai)", hold=30, sides=2, image="assets/W_leg_swings.webp",
         description="Prisilaikyk ir mosuok tiesia koja pirmyn ir atgal, po to į šonus priešais save. Kas kartą šiek tiek aukščiau, liemuo tiesus.",
         focus="dinamiškas klubų apšilimas prieš sunkius pratimus ir spyrius"),
    dict(id="W_9090", name="90/90 Hip Switch", hold=45, sides=1, image="assets/W_9090.webp",
         description="Sėsk ant grindų, abu keliai sulenkti 90°: viena koja priekyje, kita šone. Nekeldamas pėdų lėtai versk kelius į kitą pusę ir atgal. Nugara tiesi, rankomis gali atsiremti.",
         focus="klubo vidinė ir išorinė rotacija"),
    dict(id="W_cossack", name="Cossack Squat (savo svoris)", hold=45, sides=1, image="assets/W_cossack.webp",
         description="Plačiai išsižergk. Leiskis ant vienos kojos, kita lieka tiesi, pirštai į viršų. Pakaitomis į abi puses, kulnas prie žemės, kiek leidžia klubai.",
         focus="pritraukiamieji raumenys ir šoninis mobilumas"),
    dict(id="W_wgs", name="World's Greatest Stretch", hold=30, sides=2, image="assets/W_wgs.webp",
         description="Didelis įtūpstas, ranka į grindis prie priekinės pėdos, kita ranka sukasi į lubas. Judėk ritmingai: alkūnė link pėdos, sukimas į viršų.",
         focus="klubų lenkiamieji ir krūtinės pasukimas"),
    dict(id="W_deep_squat", name="Deep Squat Hold (gilus pritūpimas)", hold=45, sides=1, image="assets/W_deep_squat.webp",
         description="Leiskis į gilų pritūpimą, kulnai prie žemės. Alkūnėmis švelniai stumk kelius į šonus ir lėtai linguok iš kairės į dešinę.",
         focus="klubų ir čiurnų mobilumas pritūpimui"),
]

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
        day["warmup"] = [dict(w) for w in WARMUP]
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
