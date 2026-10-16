"""Pravi sve za Magistrat: ciste i kotirane fotomontaze, planove i jedan PDF.

Pokretanje:  python3 scripts/magistrat/napravi_sve.py
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kamera import kalibrisi_sliku1, kalibrisi_sliku4  # noqa: E402
from montaza import FOTO, IZLAZ, STEPENIK_S1, maska_poligona, renderuj, sklopi, stepenik_s2  # noqa: E402
from oznake import (oznake_fasada, oznake_trotoar, podloga_trotoar, sa_natpisom,  # noqa: E402
                    legenda_boje, izbocina)
from plan import list_grundriss, list_ansicht_schnitt  # noqa: E402

A4 = (3508, 2480)   # 300 dpi, polozeno


def na_a4(img, uspravno=False, margina=110):
    W, H = (A4[1], A4[0]) if uspravno else A4
    s = min((W - 2 * margina) / img.width, (H - 2 * margina) / img.height)
    m = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
    str_ = Image.new('RGB', (W, H), (255, 255, 255))
    str_.paste(m, ((W - m.width) // 2, (H - m.height) // 2))
    return str_


def main():
    os.makedirs(IZLAZ, exist_ok=True)
    e = izbocina()
    slobodno = ('%.2f' % ((300 - e) / 100)).replace('.', ',')

    # ---- fotografija 1: frontalno
    k1, _, _ = kalibrisi_sliku1()
    lin, sloj = renderuj(os.path.join(FOTO, 'zid_frontalno.jpg'), k1, [192, 186, 181],
                         bez_senke=maska_poligona(2000, 1500, STEPENIK_S1))
    cista1 = sklopi(lin, sloj)
    cista1.save(os.path.join(IZLAZ, 'montaza_1_zid_frontalno.jpg'), quality=93)
    kote1 = sa_natpisom(
        oznake_fasada(cista1.copy(), k1),
        'Fotomontage 1 – Ansicht der Hauswand (maßstabsgetreu)',
        ['2 Wandtische Ø 50 cm (Höhe 75 cm) · 4 Hocker (Sitzhöhe 46 cm) · 2 Pflanztröge 75 × 20 × 60 cm (Sandbraun)',
         'Anordnung: Pflanztrog – Tisch mit Hocker davor – Hocker – Hocker – Tisch mit Hocker davor – Pflanztrog',
         'Wandabschnitt 2,65 m · größte Ausladung ab Hauswand ca. %d cm · freier Gehsteig ca. %s m'
         % (round(e), slobodno)])
    kote1.save(os.path.join(IZLAZ, 'montaza_1_zid_frontalno_kote.jpg'), quality=93)

    # ---- fotografija 2: duz trotoara
    k4, _, _ = kalibrisi_sliku4()
    lin, sloj = renderuj(os.path.join(FOTO, 'trotoar.jpg'), k4, [212, 201, 195], **stepenik_s2())
    cista2 = sklopi(lin, sloj)
    cista2.save(os.path.join(IZLAZ, 'montaza_2_trotoar.jpg'), quality=93)
    nar, zel = legenda_boje()
    kote2 = sa_natpisom(
        oznake_trotoar(sklopi(lin, sloj, podloga=podloga_trotoar(bez=stepenik_s2()['zaklon']), kam=k4), k4),
        'Fotomontage 2 – Blick entlang des Gehsteigs',
        ['Gehsteig Hauswand – Randstein: 3,00 m · Möblierung inkl. Pflanztröge',
         'max. %d cm ab Hauswand · verbleibende freie Gehsteigbreite ca. %s m.' % (round(e), slobodno)],
        legenda=[(nar, 'Möblierungszone'), (zel, 'freier Gehsteig')])
    kote2.save(os.path.join(IZLAZ, 'montaza_2_trotoar_kote.jpg'), quality=93)

    # ---- planovi
    p1 = list_grundriss(); p1.save(os.path.join(IZLAZ, 'plan_1_grundriss.png'))
    p2 = list_ansicht_schnitt(); p2.save(os.path.join(IZLAZ, 'plan_2_ansicht_schnitt.png'))

    # ---- PDF (A4, 300 dpi)
    strane = [na_a4(kote1), na_a4(kote2, uspravno=True), p1, p2]
    pdf = os.path.join(IZLAZ, 'Magistrat_Moeblierung_Fassade.pdf')
    strane[0].save(pdf, save_all=True, append_images=strane[1:], resolution=300.0)
    print('gotovo:', IZLAZ)


if __name__ == '__main__':
    main()
