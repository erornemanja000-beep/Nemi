# Dijagnoza: zašto prvi Blender renderi izgledaju kao CG (recenzent, 23.10.2026)

Ocena prvih proba: **4/10**. Geometrija i proporcije su uglavnom tačne. Utisak skice dolazi od četiri stvari:
- ravna svetla okolina i tri ogromna area svetla sa globalnom ekspozicijom −1/−1,9 skidaju sve tamne tonove i odsjaje;
- nema dubinske oštrine;
- fali mikro-reljef veći od piksela;
- nema površine na kojoj predmeti stoje.

Napomena: referenca je AI video ekrana snimljenog kamerom. Deo „fotografskog" utiska dolazi od mekoće AI-ja i kompresije, a naši renderi su na sajtu sirovi i oštri, pa se svaka CG greška vidi jače.

## 10 ispravki po odnosu efekat/trud

1. **„Foto-studio" umesto `studio_lights()`.**
   - okolina 0,05–0,15;
   - jedno key area svetlo 0,6×0,9 m, oko 1,3 m levo, gore i napred;
   - odnos key:fill 4–8:1;
   - dve uske svetle trake 0,12×1,0 m pozadi i crne zastave za tamne trake na metalu;
   - ekspozicija 0.
2. **DOF:** f/4 za POUR i GRIND, f/5.6–8 za SIP, sa fokusom na prednji obod drippera ili na šolju.
3. **Ton:** AgX „Medium High Contrast", `blur_glossy` 0,2, `sample_clamp_indirect` 15.
4. **Kompozicija:**
   - kuvalo bliže kameri i odsečeno ivicom kadra;
   - SIP kamera na 22–28° odozgo;
   - male asimetrije.
5. **CSS umesto rendera** (bez treperenja i težih fajlova):
   - svetlosni gradijent pozadine iz smera key svetla;
   - traka stola sa horizontom;
   - zrno filma 3–5 % (`mix-blend-mode: overlay`).
6. **Zrna:**
   - tamna (median oko `#3A2216`–`#5A3A28` posle novog svetla);
   - svetla ljuspica u urezu;
   - 10–12 oblika;
   - motion blur (shutter 0,3–0,5).
7. **Staklo, voda i kafa:**
   - `film_transparent_glass=False` i „karta" u boji sekcije iza predmeta (vidljiva samo kroz staklo);
   - Volume Absorption za kafu, mlaz kafe 3,5–4 mm, kapi kondenzacije 1,5–4 mm.
8. **Para:** snimak prave pare na crnom sa `mix-blend-mode: screen`. Ako ostaje 3D: maska ivica ravni, alfa najviše 0,35, Principled Volume.
9. **Kuvalo:**
   - kovane fasete preko Voronoi-ja;
   - brušeni inox sa tangentom;
   - roughness mapa otisaka;
   - šupalj izliv bez crnog diska.
10. **Mikro-reljef iznad jednog piksela:**
    - šolja: tragovi kola 0,25–0,4 mm, rupice 0,08–0,12 mm, nepravilne kapi glazure;
    - filter: pravi konus, nabori, krep;
    - bevel 0,3–0,5 mm na svim tvrdim ivicama.

**CPU budžet:** nepomični delovi kadra renderuju se jednom kao „ploča" (1600 px, 512–1024 uzoraka). Po kadru ide samo region koji se menja (mlaz, bokal, zrna): oko 20 % kadra, 1200 px i 128 uzoraka, otprilike 4 min po kadru. Po potrebi 60 umesto 120 kadrova.

## Može li Blender na CPU-u do nivoa reference

| Predmet | Ocena | Bolje rešenje ako ga ima |
|---|---|---|
| mlin | da | — |
| kuvalo | da (ruka ne; rešava se rezom kadra) | — |
| V60 + bokal | skoro | studijska fotografija ako sekcija ima neprovidnu pozadinu |
| mlaz vode / kafe | skoro | slow-mo snimak na crnom (teško ga je spojiti sa CG kuvalom) |
| para | ne u ovom budžetu | **snimak prave pare na crnom + `screen`** |
| šolja | da | pravi predmet snimljen na okretnom postolju |
| zrna | da | — |

## Šta je dobro (zadržati)

- **Proporcije:** konus V60 od 60° sa rebrima, bokal kao Hario server, gooseneck kriva, šolja visoka 9,8 cm.
- **Glazura:** dobra tonska logika.
- **Senka stakla:** trik `shadow_light`.
- **Mlaz:** balistička putanja.
- **Zajednički dogovor scena** (metri, 85 mm), zbog neprekinutog prelaza zrna GRIND → POUR.
- **Metal i zrna:** `mat_brushed` sa RADIAL tangentom i `random_tint` na zrnima.

## Šta 3D radi bolje od AI reference

- geometrija je ista od kadra do kadra;
- čiste alfa ivice za sajt;
- prava sinhronizacija sa skrolom.
