# Kyokushin Training

Grato (GitHub `Igratt`) treniruočių trenerio PWA. Pastabos Claude sesijoms:

- Atsakyk lietuviškai, trumpai, pabaigoje aiški išvada: kas pasikeitė ir ką Gratui daryti.
- Taupyk tokenus: neskaityk didelių failų ir paveikslėlių be reikalo.
- Prieš didelius ar neaiškius pakeitimus išsiaiškink klausimais, mažus sprendimus priimk pats.
- Nieko neskelbk gyvai be aiškaus Grato prašymo: `npm run deploy` ir PR suliejimas yra jo sprendimas.

## Techninis minimumas

- React + Vite + TypeScript, lietuviška sąsaja, duomenys naršyklėje (localStorage), be backend'o.
- `npm run build` (tsc + vite). `npm run deploy` (deploy.mjs) stumia `dist` į `gh-pages`; gyva: https://igratt.github.io/kyokushin-training/
- Android: Capacitor (`android/`), APK renkamas GitHub Actions ir atnaujinamas per gyvą svetainę (OTA); `npm run sync:android` tik kai keičiasi native dalis.
- Programos (pratimai, variantai, apšilimas, tempimas): `src/data/programs/*.json`, generuojami ir keičiami `tools/*.py` skriptais; piešiniai `tools/draw_*.py` (Pillow) į `public/assets/`.
- Būsenos mašina `src/workout/engine.ts`, ekranai `src/screens/`, duomenų validacija `src/data/programs.ts`. Daugiau: README.md.

## Kontekstas ir istorija

Projekto istorija, sprendimai ir Grato pageidavimai yra privačioje repozitorijoje `Igratt/claude-brain`
(`memory/project_kyokushin_app.md`, `PROJEKTAI.md`, `pokalbiai/`). Jei iš šios sesijos ji pasiekiama
(`gh repo clone Igratt/claude-brain --depth 1`), perskaityk tą atminties failą prieš darbą; jei ne, paprašyk Grato įklijuoti.
