"""Poravnanje pet faza lokala na zajednicku geometriju (faza 4).

Parametri su dobijeni pretragom (skala + pomeraj) po ivicama fasade
koje se ne menjaju izmedju faza: oluk, gornji prozori, resetka, trotoar.
"""
import numpy as np
from PIL import Image

W, H, CX, CY = 480, 640, 240, 320

# raw -> referentni prostor: x' = sx*(x-CX)+CX+tx, y' = sy*(y-CY)+CY+ty
ALIGN = {
    1: (1.0000, 1.0150, -2, 3),
    2: (1.0025, 1.0400, -2, 1),
    3: (1.0075, 1.0000, -2, 0),
    4: (1.0000, 1.0000, 0, 0),
    5: (1.0075, 1.0275, 1, -1),
}


def affine_coeffs(sx, sy, tx, ty, pad=0):
    """PIL AFFINE koeficijenti: izlaz (x,y) uzima ulaz u (a*x+c, e*y+f)."""
    a = 1 / sx
    e = 1 / sy
    c = CX - (CX + tx) / sx + pad
    f = CY - (CY + ty) / sy + pad
    return (a, 0, c, 0, e, f)


def padded(img, pad):
    arr = np.asarray(img)
    arr = np.pad(arr, ((pad, pad), (pad, pad), (0, 0)), mode='edge')
    return Image.fromarray(arr)


def load_raw(base, n):
    return Image.open(f'{base}/faza_{n}.png').convert('RGB')


def load_aligned(base, n):
    pad = 32
    sx, sy, tx, ty = ALIGN[n]
    src = padded(load_raw(base, n), pad)
    return src.transform((W, H), Image.AFFINE, affine_coeffs(sx, sy, tx, ty, pad),
                         resample=Image.BICUBIC)


if __name__ == '__main__':
    import sys
    base, out = sys.argv[1], sys.argv[2]
    for n in ALIGN:
        load_aligned(base, n).save(f'{out}/a{n}.png')
