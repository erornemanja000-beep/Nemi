# Nemi Studio: novi sajt (nemistudio.at)

Pregled uživo: https://erornemanja000-beep.github.io/Nemi/nemistudio/

## Princip (isti kao referentni reelovi @w.wearebrand)
- Sticky WebGL platno preko celog ekrana; skrol bira kadar iz niza slika (WebP), dva susedna kadra se mešaju pa kretanje ostaje glatko.
- Prelazi između scena u shaderu: piksel-dither (Pear), gorenje sa užarenom ivicom (Zero), zum kroz scenu, svetlosni prelaz, trake.
- Svaka branša počinje „nema“ (crtež linijama na tamnoj podlozi) i puni se bojom dok skroluješ; mišem se boja otkriva oko kursora.
- Jedan dan u gradu: sat u uglu ide od 06:58 do 23:59, svetlo ide od jutra do noći (kao LITORALE).
- Uz svaku branšu iskoči koncept-sajt (mali prozor pregledača) sa izmišljenim brendom.
- Posle filma: manifest se „dekodira“ (LITORALE), pa mirni deo: Leistungen, Showroom (horizontalno), Ablauf, FAQ, Kontakt, footer.
- Stalno: meni, DE/EN, staklena pilula „Erstgespräch · 30 Min · kostenlos“ dole.

## Snimci (Mixkit, besplatna licenca, bez obaveznog navođenja)
curtain 22240 · city 5015 · cafe 41858 · craft 39500 · dent 33328 · law 23222 · fit 52088 · barber 43222 · food 47555 · hotel 4196 · night 49845
Isecanje u slike: `tools/frames.sh <folder-sa-mp4> public/seq` (desktop 1280×720 + uspravni isečak za telefon).

## Pokretanje
```
npm install
npm run dev
npm run build && python3 build_pages.py <gh-pages-folder>
```

## Uvod sa okom (gotovo)
- Oko (Mixkit 48017, obrnuto pa se zenica širi) → zenica se naglo raširi → kamera uleće → u zenici se pojavi prva epoha.
- 13 epoha u beskonačnom zumu kroz okrugle „prozore“: neandertalac (lobanja iz muzeja), otisci šaka, pećina, vatra, hijeroglifi, antika, 1450 štampa, 1492 brod, 1910 grad, 1925 radio, 1955 TV, 1990 računar, danas (sajt u naočarima, Mixkit 13189).
- Slike: Unsplash (besplatna licenca), u `public/intro/h/01..13.webp`; oko u `public/intro/eye/d|m`.
- Završni tekst: „Seit es Menschen gibt, wollen sie gesehen werden. Heute beginnt es mit deiner Website.“
- Pušta se jednom po poseti (sessionStorage), dugme „Intro überspringen“, isključen za `prefers-reduced-motion`.
- Parametri: `?intro=1` uvek pusti, `?intro=0` preskoči, `?reel=1` verzija za video sa završnom karticom (nemi · NEMISTUDIO.AT).
- Video za Instagram: `video/nemi_intro_9x16.mp4` i `video/nemi_intro_16x9.mp4` (renderovano kadar po kadar iz `?reel=1`).

## Otvoreno
- Impressum/Datenschutz: fale ime, adresa, UID i hosting (označeno narandžasto na stranicama).
- Formular otvara e-mail program (mailto); kad se zna hosting, može pravo slanje (npr. Netlify Forms).
- `noindex` je uključen dok je ovo pregled.
