"""Kalibracija kamere za dve fotografije zida (pinhole model).

Svet (cm): X duz zida (0 = levi kraj belog zida, 265 = ivica kod ulaza),
Y nagore (0 = trotoar uz zid), Z od zida ka ulici (0 = ravan zida).
Kamera: x desno, y dole, z napred. Piksel = f * (x/z, y/z) + (cx, cy).
"""
import numpy as np
from scipy.optimize import least_squares

ZID = 265.0       # sirina belog zida (cm)
TROTOAR = 300.0   # od zida do ivice trotoara (cm)
F_IPHONE = 1502.0  # zizna daljina u px za duzu stranu 2000 px (26 mm ekv.)


def rodrigues(r):
    th = np.linalg.norm(r)
    if th < 1e-12:
        return np.eye(3)
    k = r / th
    Kx = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * Kx + (1 - np.cos(th)) * Kx @ Kx


def rot_to_vec(R):
    th = np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))
    if th < 1e-12:
        return np.zeros(3)
    v = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    return v / (2 * np.sin(th)) * th


class Kamera:
    def __init__(self, f, cx, cy, R, C):
        self.f, self.cx, self.cy = f, cx, cy
        self.R, self.C = np.asarray(R, float), np.asarray(C, float)

    def u_kameru(self, P):
        return (np.asarray(P, float) - self.C) @ self.R.T

    def projektuj(self, P):
        Pc = self.u_kameru(P)
        z = Pc[..., 2]
        return np.stack([self.f * Pc[..., 0] / z + self.cx,
                         self.f * Pc[..., 1] / z + self.cy], -1), z

    def zrak(self, px):
        """Smer zraka (u svetu) kroz piksel."""
        px = np.asarray(px, float)
        d = np.stack([(px[..., 0] - self.cx) / self.f,
                      (px[..., 1] - self.cy) / self.f,
                      np.ones(px.shape[:-1])], -1)
        d = d @ self.R
        return d / np.linalg.norm(d, axis=-1, keepdims=True)


def pocetna_rotacija(napred, gore):
    napred = np.asarray(napred, float); napred /= np.linalg.norm(napred)
    desno = np.cross(napred, gore); desno /= np.linalg.norm(desno)
    dole = np.cross(napred, desno)
    return np.stack([desno, dole, napred])


def dist_od_linije(kam, A, D, tacke):
    """Rastojanje (px) posmatranih tacaka od slike 3D prave A + t*D."""
    p, _ = kam.projektuj(np.array([A, np.asarray(A) + 50.0 * np.asarray(D)]))
    a, b = p[0], p[1]
    n = np.array([-(b - a)[1], (b - a)[0]])
    n /= np.linalg.norm(n)
    return (np.asarray(tacke, float) - a) @ n


def fituj(posmatranja, f, cx, cy, R0, C0, n_extra, extra0, fit_f=False):
    """posmatranja: lista (funkcija(extra) -> (A, D), tacke)."""
    r0 = rot_to_vec(R0)
    x0 = np.concatenate([r0, C0, extra0, [f] if fit_f else []])

    def res(x):
        R = rodrigues(x[:3]); C = x[3:6]; ex = x[6:6 + n_extra]
        ff = x[-1] if fit_f else f
        kam = Kamera(ff, cx, cy, R, C)
        out = []
        for fn, tacke in posmatranja:
            A, D = fn(ex)
            out.append(dist_od_linije(kam, A, D, tacke))
        return np.concatenate(out)

    sol = least_squares(res, x0, loss='soft_l1', f_scale=2.0)
    x = sol.x
    kam = Kamera(x[-1] if fit_f else f, cx, cy, rodrigues(x[:3]), x[3:6])
    return kam, x[6:6 + n_extra], res(x)


# ---------------------------------------------------------------- slika 1
# Frontalni pogled na beli zid. Tacke izmerene detekcijom ivica (px).
S1_LEVA = [(182, 0), (185, 80), (188, 160), (191, 240), (195, 320), (201, 400),
           (208, 480), (213, 560), (218, 640), (224, 720), (230, 800), (234, 880),
           (237, 960), (241, 1040), (245, 1120), (249, 1200)]
S1_DESNA = [(1768, 320), (1762, 400), (1755, 480), (1749, 560), (1741, 640),
            (1735, 720), (1728, 800), (1722, 880), (1717, 960), (1711, 1040),
            (1704, 1120), (1699, 1200)]
S1_TLO = [(410, 1308), (480, 1308), (550, 1311), (620, 1312), (690, 1315),
          (760, 1315), (830, 1312), (900, 1310), (970, 1314), (1040, 1314),
          (1110, 1313), (1180, 1307), (1320, 1312), (1390, 1317), (1530, 1315),
          (1600, 1316)]
S1_SOKL = [(260, 1237), (360, 1238), (460, 1238), (560, 1238), (660, 1238),
           (760, 1238), (860, 1237), (960, 1238), (1060, 1239), (1160, 1240),
           (1260, 1241), (1360, 1241), (1460, 1241), (1560, 1243), (1660, 1240)]
# desna tabla (Eisbecher) je postavljena ravno - njene ivice su vertikale
S1_TABLA_L = [(1218, 250), (1216, 310), (1214, 370), (1213, 430), (1211, 490),
              (1209, 550), (1208, 610), (1206, 670), (1204, 730)]
S1_TABLA_D = [(1615, 310), (1610, 370), (1606, 430), (1602, 490), (1598, 550),
              (1594, 610), (1590, 670), (1586, 730)]


def kalibrisi_sliku1():
    X, Y, Z = np.eye(3)
    obs = [
        (lambda e: ((0, 0, 0), Y), S1_LEVA),
        (lambda e: ((ZID, 0, 0), Y), S1_DESNA),
        (lambda e: ((0, 0, 0), X), S1_TLO),
        (lambda e: ((0, e[0], 0), X), S1_SOKL),
        (lambda e: ((e[1], 0, 1.5), Y), S1_TABLA_L),
        (lambda e: ((e[2], 0, 1.5), Y), S1_TABLA_D),
    ]
    R0 = pocetna_rotacija((0, -0.12, -1), (0, 1, 0))
    C0 = np.array([140.0, 145.0, 290.0])
    kam, ex, r = fituj(obs, F_IPHONE, 1000, 750, R0, C0, 3, [13, 180, 245])
    return kam, ex, r


# ---------------------------------------------------------------- slika 4
# Pogled duz trotoara, zid desno, ivicnjak levo.
S4_TLO = [(1100, 1130), (1115, 1155), (1130, 1180), (1144, 1205), (1159, 1230),
          (1174, 1255), (1190, 1280), (1207, 1305), (1219, 1330), (1238, 1355),
          (1255, 1380), (1271, 1405), (1306, 1455)]
S4_SOKL = [(1105, 1080), (1122, 1105), (1138, 1130), (1155, 1155), (1171, 1180),
           (1187, 1205), (1204, 1230), (1221, 1255), (1237, 1280), (1255, 1305),
           (1272, 1330), (1289, 1355), (1307, 1380), (1324, 1405), (1340, 1430)]
S4_IVICNJAK = [(0, 1282), (40, 1251), (80, 1219), (120, 1187), (160, 1155),
               (400, 966), (480, 902), (520, 873), (560, 842), (600, 808)]
S4_UGAO_BLIZU = [(1423, 900), (1418, 960), (1414, 1020), (1409, 1080), (1404, 1140),
                 (1400, 1200), (1396, 1260), (1390, 1320), (1387, 1380), (1384, 1440)]
S4_UGAO_DALEKO = [(1099, 250), (1098, 300), (1097, 350), (1095, 400), (1094, 450),
                  (1093, 500), (1091, 600), (1091, 650), (1090, 700), (1089, 750),
                  (1088, 800), (1086, 850), (1084, 900), (1084, 950), (1082, 1000)]
S4_TABLA_BLIZU = [(1418, 240), (1414, 300), (1411, 360), (1406, 420), (1402, 480),
                  (1397, 540), (1393, 600), (1388, 660), (1384, 720), (1380, 780)]


def kalibrisi_sliku4(sokl=None, tabla_d=None, fit_f=False):
    X, Y, Z = np.eye(3)
    obs = [
        (lambda e: ((0, 0, 0), X), S4_TLO),
        (lambda e: ((0, e[0], 0), X), S4_SOKL),
        (lambda e: ((0, e[1], TROTOAR), X), S4_IVICNJAK),
        (lambda e: ((ZID, 0, 0), Y), S4_UGAO_BLIZU),
        (lambda e: ((0, 0, 0), Y), S4_UGAO_DALEKO),
    ]
    if tabla_d is not None:
        obs.append((lambda e: ((tabla_d, 0, 1.5), Y), S4_TABLA_BLIZU))
    # kamera kod ulaza, gleda ka -X, nagnuta nadole
    R0 = pocetna_rotacija((-1, -0.25, 0.25), (0, 1, 0))
    C0 = np.array([400.0, 150.0, 120.0])
    kam, ex, r = fituj(obs, F_IPHONE, 750, 1000, R0, C0, 2, [13, -3], fit_f=fit_f)
    return kam, ex, r


if __name__ == '__main__':
    np.set_printoptions(precision=3, suppress=True)
    k1, e1, r1 = kalibrisi_sliku1()
    print('SLIKA 1: C =', k1.C, 'sokl =', e1[0], 'tabla X =', e1[1:], 'rms px =',
          np.sqrt(np.mean(r1 ** 2)))
    print('  napred =', k1.R[2], ' max res', np.abs(r1).max())
    for fit_f in (False, True):
        k4, e4, r4 = kalibrisi_sliku4(fit_f=fit_f)
        print('SLIKA 4 fit_f=%s: f=%.0f C =' % (fit_f, k4.f), k4.C, 'sokl =', e4[0],
              'ivicnjak Y =', e4[1], 'rms px =', np.sqrt(np.mean(r4 ** 2)))
        print('  napred =', k4.R[2], ' max res', np.abs(r4).max())
