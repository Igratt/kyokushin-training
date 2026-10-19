# Kyokushin Training

Mobiliam telefonui skirta Kyokushin sporto salės programos programėlė: dienų pasirinkimas, pratimų nuotraukos, setų sekimas, poilsio timeris pagal laiko žymą (nesustoja užrakinus telefoną), svorio klausimas po kiekvieno pratimo ir treniruočių istorija. Viskas saugoma telefone, jokio serverio ar prisijungimo.

Kiekvienas atliktas setas iš karto įrašomas į istoriją, todėl treniruotė neprarandama uždarius programą, nepaspaudus „išsaugoti“ ar pradėjus kitą dieną.

## Gyvas adresas

https://igratt.github.io/kyokushin-training/ (GitHub Pages, repo `Igratt/kyokushin-training`, šaka `gh-pages`). Atnaujinti po pakeitimų:

```bash
npm run deploy
```

## Android programa

APK: https://github.com/Igratt/kyokushin-training/releases/latest/download/Kyokushin.apk (renka GitHub Actions iš `android/`, pasirašo tuo pačiu raktu kaip Trenkės).

- Programa krauna gyvą svetainės versiją (`capacitor.config.json` → `server.url`) ir ją saugo darbui be interneto, todėl `npm run deploy` atnaujina ir programą kitą kartą ją atidarius. Naują APK reikia tik keičiant native dalį (`android/`, Capacitor įskiepiai).
- Duomenys laikomi ir programos saugykloje (Capacitor Preferences); paleidžiant jie sujungiami su WebView kopija (`storage.ts` → `hydrate`).
- Poilsio timeris (`android/app/src/main/java/lt/igratt/kyokushin/RestTimer*.java`): poilsio metu pranešimas su atgaliniu laikmačiu, pabaigoje tikslus žadintuvas groja `res/raw/rest_end.wav` ir vibruoja, net kai programa paslėpta. Garso failą perkuria `py tools/make_beep.py`.

## Programos

Kiekvienas JSON failas aplanke `src/data/programs/` yra programa, rodoma Nustatymai → Programa. Naują programą pridėti:

1. Įdėk naują `.json` failą į `src/data/programs/` (formatas toks pat kaip `kyokushin-mix.json`).
2. `npm run deploy` — programa atsiras telefone kitą kartą atidarius.

Programą galima įkelti ir telefone iš failo (Nustatymai → „Įkelti programą iš failo“); tokia programa lieka tik tame telefone.

Formatas:

```json
{
  "id": "sprogstamumas",
  "programName": "Sprogstamumo programa",
  "focus": "Sprogstamumas ir greitis",
  "goal": "Trumpas aprašymas",
  "days": [
    {
      "id": "A",
      "name": "A DIENA",
      "subtitle": "Kojos",
      "exercises": [
        {
          "name": "Box Jump", "sets": 4, "reps": "3", "restSeconds": 90, "image": "assets/A_1.png", "description": "…", "focus": "…",
          "variants": [
            { "name": "Broad Jump", "tag": "į tolį", "sets": 4, "reps": "3", "restSeconds": 75, "image": "assets/A_1v.webp", "description": "…" }
          ]
        }
      ]
    }
  ]
}
```

`stretches` (nebūtina, prie dienos, iki 15): tempimas po treniruotės. Kiekvienas: `name`, `hold` (sekundės vienai pusei, 5–300), `sides` (1 arba 2), `image`, `description`, `focus`. Pvz. `{ "name": "Pigeon Stretch", "hold": 45, "sides": 2, "image": "assets/S_pigeon.webp", "description": "…", "focus": "mawashi geri" }`. Po treniruotės suvestinėje atsiranda „Pradėti tempimą“: 5 s pasiruošimas, laikymas, trumpas signalas, kita pusė ar kitas pratimas. Piešinius piešia `py tools/draw_stretches.py`, programos tempimą įrašo `py tools/add_stretches.py`.

`warmup` (nebūtina, prie dienos, iki 15): vedamas apšilimas prieš treniruotę, tokio pat formato kaip `stretches`. Pirmo pratimo ekrane, kol neatliktas nė vienas setas, rodoma kortelė „Apšilimas · ~6 min“ su mygtuku „Pradėti apšilimą“; eiga tokia pati kaip tempimo, o pabaigoje grįžtama į treniruotę. Dabartinis apšilimas skirtas dubeniui ir klubams (Hip CARs, kojos mostai, 90/90, Cossack, World's Greatest Stretch, gilus pritūpimas). Piešinius piešia `py tools/draw_hips.py`, į programą įrašo `py tools/add_hips.py` (kartu su dubens jėgos pratimu kiekvienos dienos pabaigoje).

`startSide` (nebūtina, `"left"` arba `"right"`): vienpusis pratimas, kurį reikia pradėti silpnesne puse. Ekrane rodoma „Pradėk kaire puse (silpnesnė), dešine – tiek pat kartojimų“, o pratimų su laiku (`sides: 2`) laikmatis pradeda nuo tos pusės.

`seconds` (nebūtina): pratimas su laiku, pvz. Plank, kiek sekundžių laikyti vieną setą (5–900). Tokiam pratimui laikmatį paleidžia pati programa: pasibaigus poilsiui 5 s pasiruošimas, laikymas, trumpas signalas, ir setas užskaitomas be jokio paspaudimo. Pirmam setui (ar atėjus prie pratimo ranka) yra mygtukas „Pradėti laikmatį“. `sides: 2` reiškia, kad laikoma kairė, o po 5 s pertraukos dešinė pusė (Side Plank). Telefone laikymas rodomas ir pranešimų juostoje, signalas skamba ir užrakinus ekraną.

`variants` (nebūtina, iki 5): kiti to paties pratimo atlikimo būdai. Programa juos keičia pakaitomis: kiekvieną kartą darant tą pačią dieną imamas kitas variantas (pagal tai, kiek kartų diena jau buvo daryta), o prieš treniruotę ar iki pirmo seto variantą galima pakeisti ranka. Pagrindiniai kėlimai (Back Squat, Bench Press, Trap-Bar Deadlift, Push Press) variantų neturi, kad svoriai būtų palyginami. Variantų piešinius piešia `py tools/draw_variants.py`.

Privaloma: `days`, kiekvienos dienos `exercises`, kiekvieno pratimo `name`, `sets` (1–20), `reps`. `restSeconds` numatytai 90. `image` gali rodyti į esamas nuotraukas (`assets/A_1.png` … `assets/C_9.png`) arba būti praleistas — tada rodoma kortelė su pavadinimu. Paskutinis svoris atsimenamas pagal pratimo pavadinimą, todėl tas pats pratimas kitoje programoje gauna tą patį „praeitą kartą“.

## Paleisti lokaliai

Reikia Node.js 18+ (naudota 20).

```bash
npm install
npm run dev
```

Atsidaro adresas `http://localhost:5173/kyokushin-training/` (programa gyvena sub-kelyje `/kyokushin-training/`, kaip ir GitHub Pages). Telefone tame pačiame Wi-Fi: `npm run dev -- --host` ir atidaryk rodomą `http://192.168.x.x:5173/kyokushin-training/` adresą.

## Production build

```bash
npm run build
npm run preview
```

`npm run build` patikrina TypeScript ir sudeda viską į `dist/` (su service worker ir manifestu). `npm run preview` paleidžia tą build'ą lokaliai.

## Struktūra

```
src/
  data/programs/*.json     programos (source of truth); kyokushin-mix.json = pagrindinė
  data/programs.ts         programų tikrinimas, dienų spalvos, pagalbinės funkcijos
  workout/engine.ts        būsenų mašina: ACTIVE_SET → RESTING → … → FINISHED, svorio klausimas, istorijos įrašas
  storage.ts               localStorage + programos saugykla (aktyvi treniruotė, istorija, programos, nustatymai)
  native.ts                Android: saugykla, poilsio timerio įskiepis, failų dalinimas
  hooks.ts                 timeris pagal laiko žymą, Wake Lock, garsas naršyklėje, install prompt, fullscreen
  screens/                 Home, Preview, Active (setas + poilsis), WeightDialog, Complete, History, Settings
public/assets/             pratimų nuotraukos (WebP); A_9, B_7, B_9, C_9 piešia tools/draw_exercises.py
android/                   Capacitor Android projektas (RestTimer įskiepis, garso failas, ikonos)
```
