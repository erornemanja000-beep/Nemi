"""Scenario "Gradnja DON'S-a": lokal se sklapa deo po deo, kao Lego.

Sve koordinate su u poravnatom prostoru faze 4 (480x640, vidi align.py).
Pravougaonik je (x0, y0, x1, y1). Vremena su u sekundama od pocetka prelaza.

Animacije elemenata:
  drop    - pada odozgo i odskoci (bam)
  rise    - izlazi odozdo i odskoci
  slide_l - uleti zdesna (kretanje ka levo)
  swing   - vrata se otvore iz sarke (sirenje po x od leve ivice)
  pop     - iskoci iz nule sa malim prebacajem
  light   - sijalica se upali sa bljeskom
  flicker - neon zatreperi i upali se
  wipe_up - puni se odozdo nagore (sladoled u vitrini)
  vanish  - stari deo se skupi i rastopi u iskrice
"""

FPS = 30

# Globalni raspored (pocetak svakog dela u sekundama)
INTRO = 0.6
A_START, A_DUR = 0.6, 3.4
B_START, B_DUR = 4.35, 4.0
C_START, C_DUR = 8.70, 4.0
D_START, D_DUR = 13.00, 2.4
FINAL_START, FINAL_DUR = 15.40, 2.0
TOTAL = FINAL_START + FINAL_DUR

# Unutrasnjost faze 4 (tu se elementi pojavljuju "iza stakla")
C_INTERIOR = [
    (38, 219, 178, 247),   # staklo iznad vrata
    (96, 262, 174, 602),   # otvor vrata
    (194, 228, 388, 528),  # veliko staklo
]
MULLION_4 = (174, 214, 194, 602)

TRANSITIONS = {
    # 1 -> 2: zazidan prozor se raspadne u cigle, pa se sklapa prozor
    'A': dict(
        src=1, dst=2, start=A_START, dur=A_DUR,
        bricks=dict(rect=(32, 212, 402, 568), cols=6, rows=10, order='center',
                    t0=0.18, spread=0.50, seams=(0.0, 0.22)),
        fade=(0.20, 0.95),
        elements=[
            dict(name='donji okvir', rect=(38, 526, 400, 556), anim='rise', t=1.00, d=0.32, kind='facade'),
            dict(name='levi okvir', rect=(38, 214, 62, 556), anim='drop', t=1.20, d=0.32, kind='facade'),
            dict(name='desni okvir', rect=(368, 214, 400, 556), anim='drop', t=1.38, d=0.32, kind='facade'),
            dict(name='gornji okvir', rect=(38, 212, 400, 250), anim='drop', t=1.56, d=0.32, kind='facade'),
            dict(name='srednja stativa', rect=(176, 226, 203, 550), anim='drop', t=1.74, d=0.32, kind='facade'),
            dict(name='krilo gore', rect=(198, 246, 372, 266), anim='drop', t=1.92, d=0.28, kind='facade'),
            dict(name='krilo dole', rect=(198, 504, 372, 530), anim='rise', t=2.06, d=0.28, kind='facade'),
        ],
        glints=[((62, 250, 176, 526), 2.35, 0.40), ((203, 266, 368, 504), 2.50, 0.40)],
        glow=((62, 250, 368, 526), 2.45, 0.65),
    ),
    # 2 -> 3: stari prozor i zid ispod padnu, sklapa se izlog, vrata i vitrina
    'B': dict(
        src=2, dst=3, start=B_START, dur=B_DUR,
        bricks=dict(rect=(30, 212, 418, 592), cols=7, rows=11, order='top',
                    t0=0.15, spread=0.45, seams=(0.0, 0.15)),
        fade=(0.20, 0.95),
        elements=[
            dict(name='okvir vrata', rect=(36, 218, 56, 584), anim='drop', t=1.05, d=0.32, kind='facade'),
            dict(name='desni okvir', rect=(394, 218, 416, 562), anim='drop', t=1.23, d=0.32, kind='facade'),
            dict(name='gornja greda', rect=(36, 216, 416, 236), anim='drop', t=1.41, d=0.32, kind='facade'),
            dict(name='stub 1', rect=(175, 224, 199, 562), anim='drop', t=1.59, d=0.32, kind='facade'),
            dict(name='stub 2', rect=(314, 224, 336, 560), anim='drop', t=1.77, d=0.32, kind='facade'),
            dict(name='prag', rect=(168, 542, 454, 578), anim='rise', t=1.95, d=0.32, kind='facade'),
            dict(name='vrata', rect=(54, 270, 100, 582), anim='swing', t=2.30, d=0.40, kind='facade'),
            dict(name='vitrina', rect=(112, 444, 380, 544), anim='drop', t=2.70, d=0.36, kind='interior',
                 holes=[(175, 224, 199, 562), (314, 224, 336, 560)], clip=[(56, 236, 394, 584)], heavy=True),
            dict(name='staklo vitrine', rect=(112, 382, 380, 446), anim='drop', t=2.95, d=0.32, kind='interior',
                 holes=[(175, 224, 199, 562), (314, 224, 336, 560)], clip=[(56, 236, 394, 584)]),
        ],
        glints=[((199, 236, 314, 540), 2.25, 0.40), ((336, 236, 394, 540), 2.35, 0.40)],
        glow=((56, 236, 394, 584), 3.25, 0.50),
    ),
    # 3 -> 4: unutrasnjost se puni: svetla, meniji, sank, frizider, vitrina, logo
    'C': dict(
        src=3, dst=4, start=C_START, dur=C_DUR,
        remove=[dict(name='stari stub', rect=(314, 224, 336, 560), anim='vanish', t=0.05, d=0.40)],
        fade=(0.0, 0.55), wipe=(0.15, 0.75), interior=C_INTERIOR, settle=(3.55, 3.95),
        # prazna prostorija = faza 3 prefarbana u boje faze 4 (uzorci zida i poda)
        grade=[(100, 268, 134, 324), (100, 560, 170, 598)],
        elements=[
            dict(name='greda nad vratima', rect=(30, 247, 184, 265), anim='drop', t=0.10, d=0.30, kind='facade'),
            dict(name='svetlo 1', rect=(159, 232, 175, 244), anim='light', t=0.70, d=0.30, kind='interior'),
            dict(name='svetlo 2', rect=(199, 240, 215, 251), anim='light', t=0.78, d=0.30, kind='interior'),
            dict(name='svetlo 3', rect=(216, 244, 232, 255), anim='light', t=0.86, d=0.30, kind='interior'),
            dict(name='svetlo 4', rect=(264, 232, 280, 244), anim='light', t=0.94, d=0.30, kind='interior'),
            dict(name='meni 1', rect=(136, 268, 174, 324), anim='drop', t=1.00, d=0.32, kind='interior', clip=C_INTERIOR, bg='src'),
            dict(name='meni 2', rect=(203, 270, 268, 323), anim='drop', t=1.14, d=0.32, kind='interior', clip=C_INTERIOR, bg='src'),
            dict(name='meni 3', rect=(268, 270, 336, 323), anim='drop', t=1.28, d=0.32, kind='interior', clip=C_INTERIOR, bg='src'),
            dict(name='sank', rect=(194, 322, 348, 392), anim='rise', t=1.50, d=0.35, kind='interior', clip=C_INTERIOR, bg='src'),
            dict(name='levi pult', rect=(96, 326, 174, 426), anim='rise', t=1.62, d=0.35, kind='interior', clip=C_INTERIOR, bg='src'),
            dict(name='coffee time', rect=(279, 340, 321, 380), anim='flicker', t=1.95, d=0.30, kind='interior'),
            dict(name='frizider', rect=(346, 314, 389, 526), anim='slide_l', t=2.00, d=0.35, kind='interior', clip=C_INTERIOR, bg='src'),
            dict(name='vitrina', rect=(116, 376, 365, 542), anim='drop', t=2.35, d=0.40, kind='interior',
                 holes=[MULLION_4], clip=C_INTERIOR, heavy=True, bg='src'),
            dict(name='sladoled', rect=(123, 406, 361, 446), anim='wipe_up', t=2.80, d=0.25, kind='interior',
                 holes=[MULLION_4]),
            dict(name='logo', rect=(185, 450, 299, 506), anim='pop', t=3.05, d=0.30, kind='interior'),
            dict(name='nalepnica', rect=(187, 379, 225, 441), anim='pop', t=3.25, d=0.25, kind='interior'),
            dict(name='maskota', rect=(322, 358, 354, 400), anim='pop', t=3.35, d=0.25, kind='interior'),
        ],
        glints=[((38, 219, 178, 247), 0.45, 0.35)],
        glow=((96, 228, 388, 602), 3.55, 0.45),
    ),
    # 4 -> 5: slova DON'S padaju jedno po jedno
    'D': dict(
        src=4, dst=5, start=D_START, dur=D_DUR,
        sign=dict(rect=(118, 100, 392, 204),
                  spans=[('D', 118, 184), ('O', 184, 247), ('N', 247, 300), ("'", 300, 325), ('S', 325, 392)],
                  t0=0.25, step=0.17, d=0.36),
        fade=(0.0, 0.40),
    ),
}

# Zavrsnica: odsjaj preko slova i stakla, iskrice
FINAL = dict(sweep=(0.10, 0.70), glass=((194, 228, 388, 528), 0.55, 0.45))
