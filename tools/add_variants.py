"""Adds the exercise variants to src/data/programs/kyokushin-mix.json (idempotent: replaces existing variants).

Main lifts (Back Squat, Bench Press, Trap-Bar Deadlift, Push Press) keep no variants on purpose,
so their weights stay comparable from week to week.
"""
import json

PATH = r"D:\Kyokushin\src\data\programs\kyokushin-mix.json"

V = {
    "A1": dict(name="Broad Jump", tag="į tolį", sets=4, reps="3", restSeconds=75,
               description="Stovėk pėdų plotyje, mostelk rankomis atgal ir sprogstamai šok kuo toliau į priekį. Nusileisk minkštai ant abiejų kojų sulenktais keliais ir sustok 1–2 s.",
               focus="Maksimalus atstumas, minkštas nusileidimas."),
    "A3": dict(name="Single-Leg RDL (kettlebell)", tag="viena koja", sets=3, reps="8 / koja", restSeconds=90,
               description="Kettlebell laikyk priešingoje rankoje nei atraminė koja. Lenkis per klubą ir laisvą koją kelk atgal, kol liemuo beveik lygiagretus grindims, tada grįžk spausdamas sėdmenį.",
               focus="Tiesi nugara, klubai lygiai, pusiausvyra."),
    "A4": dict(name="Goblet Reverse Lunge", tag="kettlebell, atgal", sets=3, reps="8 / koja", restSeconds=90,
               description="Kettlebell laikyk prie krūtinės. Ženk viena koja atgal ir leiskis, kol galinis kelis beveik paliečia grindis, tada stumkis priekine koja į pradinę padėtį.",
               focus="Liemuo vertikalus, priekinis kelis stabilus."),
    "A5": dict(name="Split Squat Jump", tag="šuoliai", sets=3, reps="5 / koja", restSeconds=75,
               description="Įtūpstas, priekinis kelis virš pėdos. Sprogstamai šok aukštyn, ore sukeisk kojas ir nusileisk į įtūpstą su kita koja priekyje.",
               focus="Greitis ir minkštas nusileidimas."),
    "A6": dict(name="Single-Leg Calf Raise", tag="viena koja", sets=3, reps="10–12 / koja", restSeconds=60,
               description="Stovėk viena koja ant pakylos krašto, hantelį laikyk toje pačioje pusėje, kita ranka prisilaikyk. Lėtai nusileisk žemyn ir stipriai kilk ant pirštų.",
               focus="Pilna amplitudė, pauzė viršuje."),
    "A7": dict(name="Reverse Crunch (ant suolo)", tag="ant suolo", sets=3, reps="12–15", restSeconds=60,
               description="Gulėk ant suolo ir rankomis laikykis už jo galo virš galvos. Sulenktus kelius trauk link krūtinės, kol dubuo atsikelia nuo suolo, ir lėtai nuleisk.",
               focus="Judesį daro presas, ne inercija."),
    "A8": dict(name="Half-Kneeling Pallof Press (guma)", tag="su guma, klūpint", sets=3, reps="10 / pusė", restSeconds=50,
               description="Klūpėk ant vieno kelio šonu į gumos tvirtinimą. Spausk rankas tiesiai priešais save, sulaikyk 2 s ir neleisk liemeniui pasisukti.",
               focus="Anti-rotation, dubuo stabilus."),
    "A9": dict(name="Weighted Crunch", tag="su svoriu", sets=3, reps="12–15", restSeconds=45,
               description="Kaip įprastas crunch, tik ant krūtinės laikyk svorio diską ar hantelį. Kelk pečius kontroliuotai ir lėtai leiskis.",
               focus="Trumpa amplitudė, kontrolė."),
    "B1": dict(name="Banded Rotational Punch", tag="su guma", sets=4, reps="5 / pusė", restSeconds=75,
               description="Gumą pritvirtink už nugaros peties aukštyje. Kovinė stovėsena: sprogstamai smūgiuok į priekį sukdamas galinę pėdą ir klubus, tada kontroliuotai grįžk.",
               focus="Jėga iš pėdos ir klubų, greitas smūgis."),
    "B3": dict(name="Lat Pulldown", tag="trosu", sets=4, reps="6–8", restSeconds=90,
               description="Sėsk prie troso ir suimk rankeną plačiau nei pečiai. Trauk iki viršutinės krūtinės, alkūnes vesdamas žemyn, ir lėtai grąžink.",
               focus="Nesisiūbuok, mentės žemyn."),
    "B4": dict(name="Half-Kneeling Kettlebell Press", tag="kettlebell, klūpint", sets=3, reps="6–8 / ranka", restSeconds=90,
               description="Klūpėk ant vieno kelio, kettlebell laikyk prie peties tos pusės, kur kelis ant žemės. Spausk tiesiai virš galvos, liemuo nekliba.",
               focus="Įtemptas presas ir sėdmuo."),
    "B5": dict(name="Seated Cable Row", tag="trosu", sets=3, reps="8–10", restSeconds=90,
               description="Sėsk prie troso, pėdos į atramą. Trauk rankeną link pilvo, gale suspausk mentes ir lėtai ištiesk rankas.",
               focus="Viršutinė nugara, liemuo nejuda."),
    "B6": dict(name="Banded Explosive Push-Ups", tag="su guma", sets=3, reps="5", restSeconds=75,
               description="Gumą permesk per nugarą ir prispausk delnais prie grindų. Leiskis kontroliuotai ir sprogstamai stumkis aukštyn prieš gumos pasipriešinimą.",
               focus="Greitas stūmimas, ne iki failure."),
    "B7": dict(name="Band Pull-Apart", tag="su guma", sets=3, reps="15–20", restSeconds=60,
               description="Ištiestomis rankomis laikyk gumą priešais krūtinę. Tempk ją į šonus, kol guma paliečia krūtinę, suspausk mentes ir lėtai grąžink.",
               focus="Galinė delta ir mentės."),
    "B8": dict(name="Low-to-High Woodchopper", tag="iš apačios į viršų", sets=3, reps="10 / pusė", restSeconds=60,
               description="Troso rankeną ar gumą pritvirtink žemai. Trauk ją įstrižai nuo klubo aukštyn per kūną, sukdamas liemenį ir klubus, ir kontroliuotai grąžink.",
               focus="Kontroliuota rotacija."),
    "B9": dict(name="Side Plank", tag="šoninė", sets=3, reps="30–45 s / pusė", restSeconds=45,
               description="Atsiremk į dilbį ir pėdos šoną, kūnas tiesus nuo galvos iki kulnų. Klubai aukštai, neleisk jiems nukristi.",
               focus="Tiesi linija, įtemptas šonas."),
    "C1": dict(name="Dumbbell Jump Squat", tag="su hanteliais", sets=4, reps="3", restSeconds=75,
               description="Laikyk lengvus hantelius šonuose. Pritūpk negiliai, sprogstamai šok aukštyn ir nusileisk minkštai.",
               focus="Lengvas svoris, maksimalus greitis."),
    "C4": dict(name="Lateral Lunge", tag="į šoną", sets=3, reps="8 / koja", restSeconds=90,
               description="Kettlebell laikyk prie krūtinės. Ženk plačiai į šoną ir leiskis ant tos kojos, kita lieka tiesi, tada stumkis atgal.",
               focus="Visa pėda ant žemės, nugara tiesi."),
    "C5": dict(name="Neutral-Grip Pull-Ups", tag="lygiagretus suėmimas", sets=3, reps="6–10", restSeconds=90,
               description="Suimk lygiagrečias rankenas delnais vienas į kitą. Prisitrauk, kol smakras virš rankenų, ir pilnai nusileisk.",
               focus="Pilna amplitudė, be siūbavimo."),
    "C6": dict(name="Rotational Med Ball Slam", tag="į šoną", sets=4, reps="5 / pusė", restSeconds=60,
               description="Pakelk kamuolį virš galvos ir sukdamas liemenį trenk jį įstrižai į grindis šalia pėdos. Keisk puses.",
               focus="Sprogstamai, jėga iš liemens."),
    "C7": dict(name="Suitcase Carry", tag="viena ranka", sets=3, reps="30–40 m / ranka", restSeconds=75,
               description="Sunkų hantelį ar kettlebell neškis vienoje rankoje. Eik tiesiai, nesilenk į šoną, pečiai lygūs.",
               focus="Šoninis presas, laikysena."),
    "C8": dict(name="Dead Bug", tag="ant nugaros", sets=3, reps="8 / pusė", restSeconds=60,
               description="Gulėk ant nugaros, rankos į viršų, keliai virš klubų. Lėtai tiesk priešingą ranką ir koją link grindų, juosmuo prispaustas, ir grįžk.",
               focus="Juosmuo prispaustas prie grindų."),
    "C9": dict(name="Russian Twist", tag="su kamuoliu", sets=3, reps="12 / pusė", restSeconds=45,
               description="Sėdėk atsilošęs, kojos pakeltos arba ant grindų. Kamuolį sukdamas liemenį lietink prie grindų tai vienoje, tai kitoje pusėje.",
               focus="Sukimas iš liemens, nugara tiesi."),
}

data = json.load(open(PATH, encoding="utf-8"))
added = 0
for day in data["days"]:
    for ex in day["exercises"]:
        ex.pop("variants", None)
        v = V.get(ex["id"])
        if not v:
            continue
        n = ex["id"][1:]
        variant = {"id": ex["id"] + "v", "name": v["name"], "tag": v["tag"], "sets": v["sets"], "reps": v["reps"],
                   "restSeconds": v["restSeconds"], "image": f"assets/{day['id']}_{n}v.webp",
                   "description": v["description"], "focus": v["focus"]}
        ex["variants"] = [variant]
        added += 1
json.dump(data, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("variants added:", added)
print("without variants:", [e["name"] for d in data["days"] for e in d["exercises"] if "variants" not in e])
