# Kyokushin Training

Mobiliam telefonui skirta 3 dienų Kyokushin sporto salės programos programėlė (PWA): A/B/C dienos, pratimų nuotraukos, setų sekimas, poilsio timeris pagal laiko žymą (nesustoja užrakinus telefoną), svorių atsiminimas ir treniruočių istorija. Viskas saugoma telefone (localStorage), jokio serverio ar prisijungimo.

Programa paimta iš `src/data/workout_data.json` (šaltinis: `Kyokushin_sporto_sales_programa.pdf`). Nuotraukos: `public/assets/A_1.webp … C_8.webp`.

## Gyvas adresas

https://igratt.github.io/kyokushin-training/ (GitHub Pages, repo `Igratt/kyokushin-training`, šaka `gh-pages`). Atnaujinti po pakeitimų:

```bash
npm run deploy
```

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

`npm run build` patikrina TypeScript ir sudeda viską į `dist/` (su service worker ir manifestu). `npm run preview` paleidžia tą build'ą lokaliai, kad pamatytum, kaip veiks įdiegus.

## Įsidiegti telefone kaip programėlę

Programėlė turi būti pasiekiama per `https://` adresą (žr. „Deploy“ žemiau) arba per `localhost`.

- **Android (Chrome):** atidaryk adresą, pradžios ekrane spausk „Įdiegti programėlę į telefoną“ arba Chrome meniu (⋮) → „Įdiegti programą“ / „Pridėti prie pagrindinio ekrano“.
- **iPhone (Safari):** „Dalintis“ (kvadratas su rodykle) → „Į pradžios ekraną“.

Po pirmo atidarymo programėlė veikia ir be interneto.

## Deploy nemokamai

Vite build'as yra statinis `dist/` aplankas, tinka bet kuriam statiniam hostingui.

**Netlify**

1. `npm run build`
2. https://app.netlify.com/drop → nutempk `dist/` aplanką. Gauni `https://xxx.netlify.app` adresą.
   Arba prijunk GitHub repo: build command `npm run build`, publish directory `dist`.

**Vercel**

1. Įkelk repo į GitHub.
2. https://vercel.com/new → importuok repo. Framework: Vite, build `npm run build`, output `dist`.

**GitHub Pages**

Build naudoja santykinius kelius (`base: './'`), todėl veikia ir sub-kelyje kaip `https://vardas.github.io/repo/`. Įkelk `dist/` turinį į `gh-pages` šaką arba naudok GitHub Actions su `actions/deploy-pages`.

## Struktūra

```
src/
  data/workout_data.json   programa (source of truth)
  data/program.ts          tipizuoti duomenys, dienų spalvos
  workout/engine.ts        būsenų mašina: ACTIVE_SET → RESTING → … → FINISHED
  storage.ts               localStorage (aktyvi treniruotė, istorija, poilsio korekcijos, nustatymai)
  hooks.ts                 timeris pagal laiko žymą, Wake Lock, vibracija/garsas, install prompt, fullscreen
  screens/                 Home, Preview, Active (setas + poilsis), Complete, History
public/assets/             pratimų nuotraukos (WebP) ir titulinis paveikslėlis
public/icons/              PWA ikonos
```
