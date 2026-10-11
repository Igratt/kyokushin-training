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
        { "name": "Box Jump", "sets": 4, "reps": "3", "restSeconds": 90, "image": "assets/A_1.png", "description": "…", "focus": "…" }
      ]
    }
  ]
}
```

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
