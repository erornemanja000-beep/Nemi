// Statični režim ('static': prefers-reduced-motion, bez WebGL-a, probni FPS < 20).
// Umesto canvas-a svako poglavlje dobija svoj kadar kao <picture> (16:9 za širok ekran,
// 9:16 za telefon). Kadrovi se ubacuju tek kad je mod statičan, pa ih 3D posetilac ne preuzima.
// Bez skrol pokreta: sat i poglavlja i dalje idu na običan skrol (scroll.js → bus 'chapter').
//
// Pokretanje: init(bus). Za sada ga zove ui/chapters.js (main.js još ne uvozi src/static/);
// drugi poziv ne radi ništa, pa main.js sme kasnije da ga pozove i sam.

import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { telefon } from '../ui/util.js';

// Kadrovi iz Blendera (studio/pekara/blender/kadrovi.py), 16:10 i 9:16.
const FOLDER = 'frames/';
const SIRINA = { wide: [1600, 1000], hoch: [900, 1600] };

// cilj: selektor kontejnera u koji ide kadar (prvo dete); alt iz tekstovi.md (Statische Bilder).
// Poglavlje 7 (forma) ima dnevni kadar 7, a večernji 7b ide u futer.
const KADROVI = [
  { cilj: '[data-pogl="1"] > .pogl__in', ime: 'kadar-1', prvi: true,
    alt: 'Nachtmodell eines Wiener Häuserblocks auf einem Holzbrett. Alles ist dunkel, nur ein Fenster im Erdgeschoß des Eckhauses leuchtet orange, aus dem Rauchfang steigt Rauch.' },
  { cilj: '[data-pogl="2"] > .pogl__in', ime: 'kadar-2',
    alt: 'Blick über Mansardendächer und Rauchfänge. Unten auf der Straße brennen die Laternen, die Auslage der Bäckerei leuchtet warm.' },
  { cilj: '[data-pogl="3"] > .pogl__in', ime: 'kadar-3',
    alt: 'Die Fassade des Eckhauses ist wie eine Scheibe Brot nach vorn gezogen. Im Schnitt sieht man Ziegel und Krume, dahinter die warm beleuchtete Backstube.' },
  { cilj: '[data-pogl="4"] > .pogl__in', ime: 'kadar-4',
    alt: 'In der Backstube steht die Ofentür offen, oranges Licht fällt über Teig und Gärkörbe.' },
  { cilj: '[data-pogl="5"] > .pogl__in', ime: 'kadar-5',
    alt: 'Auf der Budel liegen Kaisersemmel, Mohnwecken, Laugenbrezel und Roggenlaib, dahinter Regale mit Gärkörben.' },
  { cilj: '[data-pogl="6"] > .pogl__in', ime: 'kadar-6',
    alt: 'Das ganze Grätzl im Morgenlicht. In fast allen Fenstern brennt Licht, die Laternen sind aus, kleine Figuren mit Papiersackerln gehen zur Bäckerei.' },
  { cilj: '[data-pogl="7"] > .pogl__in', ime: 'kadar-7',
    alt: 'Der Häuserblock in ruhigem Tageslicht, vor der Bäckerei steht niemand mehr an.' },
  { cilj: '.futer', ime: 'kadar-7b',
    alt: 'Abend über dem Grätzl. Alle Fenster sind dunkel, nur eines im Eckhaus leuchtet noch.' },
];

let pokrenut = false;
let ubaceno = false;

const putanja = (ime, oblik) => `${import.meta.env.BASE_URL}${FOLDER}${ime}-${oblik}.webp`;

function kadar({ ime, alt, prvi }) {
  const pic = document.createElement('picture');
  pic.className = 'kadar';
  pic.dataset.kadar = ime;
  const src = document.createElement('source');
  src.media = telefon.media; // isti prelom kao CSS (max-width: 700px)
  src.srcset = putanja(ime, 'hoch');
  src.width = SIRINA.hoch[0];
  src.height = SIRINA.hoch[1];
  const img = document.createElement('img');
  img.src = putanja(ime, 'wide');
  [img.width, img.height] = SIRINA.wide;
  img.alt = alt;
  img.decoding = 'async';
  if (prvi) img.fetchPriority = 'high';
  else img.loading = 'lazy';
  pic.append(src, img);
  return pic;
}

function ubaci() {
  if (ubaceno) return;
  ubaceno = true;
  for (const k of KADROVI) {
    const el = document.querySelector(k.cilj);
    if (el && !el.querySelector(':scope > .kadar')) el.prepend(kadar(k));
  }
}

export function init(bus) {
  if (pokrenut) return;
  pokrenut = true;
  // Pretpostavka iz <head> (reduced motion → statično) važi dok main.js ne odluči.
  const staticno = (m) => m === 'static' || (m === undefined && document.documentElement.classList.contains('mode-static'));
  if (staticno(bus.get('mode'))) ubaci();
  bus.on('mode', (m) => {
    if (!staticno(m)) return;
    ubaci();
    // Prelaz 3d → static menja visine sekcija (180svh → prirodna visina), a scroll.js meri
    // pozicije samo na ScrollTrigger refresh. Bez ovoga sat i poglavlja kasne za skrolom.
    // PRIVREMENO dok scroll.js sam ne osveži mere na 'mode' (zahtev animatoru).
    requestAnimationFrame(() => ScrollTrigger.refresh());
  });
}
