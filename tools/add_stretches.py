"""Adds the cool-down stretches to src/data/programs/kyokushin-mix.json (idempotent: replaces existing ones).

A day: hips, hamstrings, adductors, calves (kicks, stances, after squats and jumps).
B day: chest, shoulders, triceps, thoracic rotation, wrists (punches, after presses and pulls).
C day: whole body.
"""
import json

PATH = r"D:\Kyokushin\src\data\programs\kyokushin-mix.json"

S = {
    "hip_flexor": dict(name="Kneeling Hip Flexor Stretch", sides=2,
                       description="Atsiklaupk ant vieno kelio, kita koja priekyje. Įtempk sėdmenį ir stumk klubus pirmyn, kol pajusi tempimą galinės kojos šlaunies priekyje. Tos pusės ranką kelk aukštyn.",
                       focus="aukštiems spyriams ir gilesnei stovėsenai, po pritūpimų"),
    "pigeon": dict(name="Pigeon Stretch", sides=2,
                   description="Priekinė koja sulenkta priešais tave, galinė ištiesta atgal. Klubai lygiai, lėtai leiskis žemyn ir kvėpuok į sėdmenį.",
                   focus="klubų sukimui: mawashi geri ir ura mawashi"),
    "hamstring": dict(name="Seated Hamstring Stretch", sides=1,
                      description="Sėdėk tiesiomis kojomis, pirštai į viršų. Lenkis pirmyn per klubus tiesia nugara ir siek pėdų, kol pajusi tempimą šlaunies gale.",
                      focus="mae geri ir kakato geri, po RDL"),
    "butterfly": dict(name="Butterfly Stretch", sides=1,
                      description="Sėdėk tiesia nugara, padus suglausk ir pritrauk pėdas arčiau savęs. Alkūnėmis švelniai spausk kelius žemyn.",
                      focus="yoko geri ir kiba dachi"),
    "straddle": dict(name="Straddle Stretch", sides=1,
                     description="Sėdėk kojas išskėtęs kuo plačiau, keliai į viršų. Lenkis pirmyn tiesia nugara, rankas slinkdamas grindimis.",
                     focus="šoniniam špagatui ir aukštiems spyriams"),
    "calf": dict(name="Wall Calf Stretch", sides=2,
                 description="Rankomis atsiremk į sieną, galinė koja tiesi, kulnas prie grindų. Lėtai stumk klubus link sienos.",
                 focus="blauzdoms ir Achilui po šuolių, judėjimui ant pirštų"),
    "doorway": dict(name="Doorway Chest Stretch", sides=1,
                    description="Dilbius padėk ant durų staktos, alkūnės pečių aukštyje. Ženk žingsnį pirmyn, kol pajusi tempimą krūtinėje.",
                    focus="krūtinei po spaudimų, laisvesniam smūgiui"),
    "cross_body": dict(name="Cross-Body Shoulder Stretch", sides=2,
                       description="Ištiestą ranką trauk per krūtinę, kita ranka prispausk ją ties alkūne. Petys žemai, ne prie ausies.",
                       focus="pečiams ir galinei deltai po traukimų"),
    "triceps": dict(name="Overhead Triceps Stretch", sides=2,
                    description="Pakelk ranką, sulenk alkūnę ir delną nuleisk už galvos. Kita ranka švelniai trauk alkūnę žemyn.",
                    focus="tricepsui po spaudimų ir smūgių"),
    "thread": dict(name="Thread the Needle", sides=2,
                   description="Atsiremk keturiomis. Vieną ranką pakišk po kūnu į kitą pusę ir nuleisk petį bei skruostą ant grindų, kita ranka siek lubų.",
                   focus="krūtinės ląstos sukimui: smūgiams ir blokams"),
    "child": dict(name="Child's Pose", sides=1,
                  description="Atsisėsk ant kulnų, kelius praskėsk ir ištiesk rankas toli pirmyn. Pasistumk rankomis į vieną, paskui į kitą šoną.",
                  focus="nugaros plačiausiesiems ir juosmeniui"),
    "wrist": dict(name="Kneeling Wrist Stretch", sides=1,
                  description="Atsiremk keturiomis, delnai ant grindų, pirštai atgal į kelius. Lėtai sėskis atgal, kol pajusi tempimą dilbiuose.",
                  focus="riešams ir dilbiams: smūgiams ir atsispaudimams ant kumščių"),
    "wgs": dict(name="World's Greatest Stretch", sides=2,
                description="Gilus įtūpstas, galinė koja tiesi. Ranką padėk prie priekinės pėdos, kitą kelk į lubas ir sukis krūtine į tą pusę.",
                focus="klubams ir krūtinės ląstai, visam kūnui"),
    "cobra": dict(name="Cobra Stretch", sides=1,
                  description="Gulėk ant pilvo, delnai po pečiais. Stumk krūtinę aukštyn, klubai lieka ant grindų, pečiai žemyn nuo ausų.",
                  focus="presui ir klubų lenkiamiesiems po pilvo pratimų"),
}

DAYS = {
    "A": [("hip_flexor", 45), ("pigeon", 45), ("hamstring", 45), ("butterfly", 45), ("straddle", 45), ("calf", 30)],
    "B": [("doorway", 45), ("cross_body", 30), ("triceps", 30), ("thread", 30), ("child", 45), ("wrist", 30)],
    "C": [("wgs", 30), ("hip_flexor", 30), ("pigeon", 30), ("hamstring", 45), ("cobra", 30), ("child", 45), ("straddle", 45)],
}

data = json.load(open(PATH, encoding="utf-8"))
for day in data["days"]:
    plan = DAYS.get(day["id"], [])
    day["stretches"] = [
        {"id": f"S_{key}", "name": S[key]["name"], "hold": hold, "sides": S[key]["sides"], "image": f"assets/S_{key}.webp",
         "description": S[key]["description"], "focus": S[key]["focus"]}
        for key, hold in plan
    ]
    secs = sum((st["hold"] + 5) * st["sides"] for st in day["stretches"])
    print(day["id"], len(day["stretches"]), "stretches,", round(secs / 60, 1), "min")
json.dump(data, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("unique stretches:", len(S))
