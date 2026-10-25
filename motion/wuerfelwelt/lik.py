"""Pikselni lik „Kocko" (16 × 18 px): 4 kadra hoda i 1 kadar mahanja.

Izlaz: public/wuerfel/lik_0.png … lik_4.png (za Remotion) i wuerfelwelt/lik_sheet.png
(svih 5 kadrova u redu, za uvoz u Pixelorama: Open → Spritesheet, 5 kolona, 1 red).
Pokretanje: python3 motion/wuerfelwelt/lik.py
"""
import os

from PIL import Image

W, H = 16, 18
BOJE = {
    "O": (255, 90, 36),  # narandžasta (signal)
    "o": (200, 68, 28),  # senka glave
    "h": (255, 140, 96),  # odsjaj
    "W": (239, 234, 226),  # krem
    "w": (196, 188, 176),  # senka majice
    "K": (11, 11, 12),  # oči i usta
    "G": (92, 94, 104),  # noge
}

GLAVA = [
    "..hhhhhhhhhhhh..",
    "..OOOOOOOOOOOo..",
    "..OOWWOOOOWWOo..",
    "..OOWKOOOOWKOo..",
    "..OOOOOOOOOOOo..",
    "..OOOOOKKOOOOo..",
    "..OOOOOOOOOOOo..",
    "..oooooooooooo..",
]


def kadar(i):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()

    def tacka(x, y, c):
        if 0 <= x < W and 0 <= y < H:
            px[x, y] = (*BOJE[c], 255)

    hoda = i < 4
    skok = 1 if hoda and i % 2 == 1 else 0  # u kadrovima 1 i 3 telo se spusti za piksel
    for y, red in enumerate(GLAVA):
        for x, c in enumerate(red):
            if c != ".":
                tacka(x, y + skok, c)
    # majica
    for y in range(8, 13):
        for x in range(5, 11):
            tacka(x, y + skok, "w" if x == 10 else "W")
    # ruke: u hodu se smenjuju gore i dole, u kadru 4 desna maše
    levo_dole = 1 if i == 0 else 0
    desno_dole = 1 if i == 2 else 0
    for y in range(9, 12):
        tacka(4, y + skok + levo_dole, "O")
        if i != 4:
            tacka(11, y + skok + desno_dole, "O")
    if i == 4:
        for x, y in ((11, 9), (12, 9), (13, 8), (14, 7), (14, 6), (14, 5), (14, 4)):
            tacka(x, y, "O")
        tacka(15, 3, "h")
        tacka(15, 4, "h")
    # noge: podignuta noga je kraća
    leva = 2 if i == 2 else 3
    desna = 2 if i == 0 else 3
    for y in range(13, 13 + leva):
        tacka(5, y, "G")
        tacka(6, y, "G")
    for y in range(13, 13 + desna):
        tacka(9, y, "G")
        tacka(10, y, "G")
    return img


if __name__ == "__main__":
    ovde = os.path.dirname(os.path.abspath(__file__))
    javno = os.path.join(ovde, "..", "public", "wuerfel")
    os.makedirs(javno, exist_ok=True)
    kadrovi = [kadar(i) for i in range(5)]
    for i, k in enumerate(kadrovi):
        k.save(os.path.join(javno, f"lik_{i}.png"))
    sheet = Image.new("RGBA", (W * 5, H), (0, 0, 0, 0))
    for i, k in enumerate(kadrovi):
        sheet.paste(k, (i * W, 0))
    sheet.save(os.path.join(ovde, "lik_sheet.png"))
    print("gotovo:", len(kadrovi), "kadrova")
