import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import PORTALS from '../portals.json';
import { reduced, vhPx } from '../scroll.js';

// "Site in a site": a photo of a device whose screen shows the next website (the real hero,
// live). Scrolling flies the camera into the screen until the screen is the viewport, then the
// hero simply scrolls on as the top of that website.
//
// The hero is laid out at viewport size and mapped into the screen with a homography (H0).
// The whole stage then gets a second homography G(p) that carries the screen corners to the
// viewport corners, so at p = 1 G·H0 is the identity and the hero is pixel-exact and flat.

const ZOOM = 1.6; // scroll length of the dive, in viewport heights

// 3x3 homography mapping 4 points src -> dst (row-major, h22 = 1)
function homography(src, dst) {
  const A = [];
  const b = [];
  for (let i = 0; i < 4; i++) {
    const [x, y] = src[i];
    const [u, v] = dst[i];
    A.push([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.push(u);
    A.push([0, 0, 0, x, y, 1, -v * x, -v * y]); b.push(v);
  }
  // gaussian elimination with partial pivoting
  for (let c = 0; c < 8; c++) {
    let p = c;
    for (let r = c + 1; r < 8; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r;
    [A[c], A[p]] = [A[p], A[c]];
    [b[c], b[p]] = [b[p], b[c]];
    for (let r = c + 1; r < 8; r++) {
      const f = A[r][c] / A[c][c];
      for (let k = c; k < 8; k++) A[r][k] -= f * A[c][k];
      b[r] -= f * b[c];
    }
  }
  const h = new Array(8);
  for (let r = 7; r >= 0; r--) {
    let s = b[r];
    for (let k = r + 1; k < 8; k++) s -= A[r][k] * h[k];
    h[r] = s / A[r][r];
  }
  return [...h, 1];
}

const css = (h) =>
  `matrix3d(${h[0]},${h[3]},0,${h[6]},${h[1]},${h[4]},0,${h[7]},0,0,1,0,${h[2]},${h[5]},0,${h[8]})`;

const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

// geometry of one portal for a viewport: photo placement and the screen quad in viewport px
function layout(name, W, H) {
  const P = PORTALS[name];
  const q = P.quad;
  const xs = q.map((p) => p[0]);
  const ys = q.map((p) => p[1]);
  const qw = Math.max(...xs) - Math.min(...xs);
  const qh = Math.max(...ys) - Math.min(...ys);
  // cover the viewport, but never let the screen grow past ~78% of it
  let s = Math.max(W / P.w, H / P.h);
  s = Math.min(s, (0.78 * W) / qw, (0.66 * H) / qh);
  const pw = P.w * s;
  const ph = P.h * s;
  const cx = (Math.min(...xs) + qw / 2) * s;
  const cy = (Math.min(...ys) + qh / 2) * s;
  // aim at the screen, keep the photo covering the viewport where it can
  const clamp = (v, size, view) => (size >= view ? Math.min(0, Math.max(view - size, v)) : (view - size) / 2);
  const ox = clamp(W / 2 - cx, pw, W);
  const oy = clamp(H * 0.48 - cy, ph, H);
  const quad = q.map(([x, y]) => [x * s + ox, y * s + oy]);
  return { s, pw, ph, ox, oy, quad, covers: pw >= W - 1 && ph >= H - 1 };
}

export default function Portal({ id, device, label, children, caption, dim = false, film = 0, progress = null }) {
  const sec = useRef();
  const stage = useRef();
  const screen = useRef();
  const shade = useRef();
  const cap = useRef();
  const veil = useRef();
  const [vp, setVp] = useState({ W: 1440, H: 900 });
  const portrait = vp.W / vp.H < 0.9;
  const name = (portrait ? 'm-' : '') + device;
  const L = layout(name, vp.W, vp.H);
  const rect = [[0, 0], [vp.W, 0], [vp.W, vp.H], [0, vp.H]];
  const H0 = homography(rect, L.quad);

  useLayoutEffect(() => {
    const measure = () => setVp({ W: document.documentElement.clientWidth, H: Math.round(vhPx() * 100) });
    measure();
    let w = innerWidth;
    const on = () => { if (innerWidth !== w) { w = innerWidth; measure(); } };
    addEventListener('resize', on);
    return () => removeEventListener('resize', on);
  }, []);

  useEffect(() => {
    const { W, H } = vp;
    const Q = L.quad;
    const area = (pts) => Math.abs(pts.reduce((a, p, i) => { const n = pts[(i + 1) % 4]; return a + p[0] * n[1] - n[0] * p[1]; }, 0)) / 2;
    const S = Math.sqrt((W * H) / area(Q));
    const cQ = Q.reduce((a, p) => [a[0] + p[0] / 4, a[1] + p[1] / 4], [0, 0]);
    const cR = [W / 2, H / 2];
    let last = -1;
    let raf;
    const frame = () => {
      raf = requestAnimationFrame(frame);
      const r = sec.current.getBoundingClientRect();
      const dist = ZOOM * H;
      const p = reduced ? (r.top < -dist / 2 ? 1 : 0) : Math.min(1, Math.max(0, -r.top / dist));
      // after the dive the screen plays its own scroll film
      if (progress) {
        progress.current.q = film ? Math.min(1, Math.max(0, (-r.top - dist) / (film * H))) : 0;
        progress.current.p = p;
        progress.current.visible = r.bottom > 0 && r.top < H;
      }
      if (Math.abs(p - last) < 1e-4) return;
      last = p;
      const st = stage.current;
      if (p >= 0.999) {
        // flat: drop the transforms so text is rendered crisp and the hero is a normal block
        st.style.transform = 'none';
        screen.current.style.transform = 'none';
        st.classList.add('flat');
      } else {
        st.classList.remove('flat');
        screen.current.style.transform = css(H0);
        const e = ease(p);
        const k = Math.pow(S, e); // exponential zoom reads as a constant camera speed
        const t = (k - 1) / (S - 1);
        const c = [cQ[0] + (cR[0] - cQ[0]) * t, cQ[1] + (cR[1] - cQ[1]) * t];
        const dst = Q.map((q, i) => [
          c[0] + k * ((1 - t) * (q[0] - cQ[0]) + (t * (rect[i][0] - cR[0])) / S),
          c[1] + k * ((1 - t) * (q[1] - cQ[1]) + (t * (rect[i][1] - cR[1])) / S),
        ]);
        st.style.transform = css(homography(Q, dst));
      }
      st.style.setProperty('--p', p.toFixed(4));
      if (shade.current) shade.current.style.opacity = String(Math.max(0, 1 - p * 2.2));
      if (cap.current) {
        cap.current.style.opacity = String(Math.max(0, 1 - p * (dim ? 6 : 4)));
        cap.current.style.transform = `translateY(${-p * 60}px)`;
      }
      // the opening rests in the dark under its headline, then the room lights up
      if (veil.current) {
        // and the lens pulls focus from the headline to the screen
        const k = Math.max(0, 1 - p / 0.2);
        veil.current.style.opacity = String(0.62 * k);
        st.style.filter = k > 0.01 ? `blur(${(k * 7).toFixed(2)}px)` : 'none';
      }
    };
    raf = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(raf);
  }, [vp, name]);

  const base = import.meta.env.BASE_URL;
  const img = `${base}portals/${name}.webp`;
  return (
    <section id={id} className="portal" ref={sec} style={{ height: vp.H * (1 + ZOOM + film) }} aria-label={label}>
      <div className="portal-sticky" style={{ height: vp.H }}>
        {!L.covers && <div className="portal-back" ref={shade} style={{ backgroundImage: `url(${img})` }} />}
        <div className="portal-stage" ref={stage} style={{ width: vp.W, height: vp.H }}>
          <div className="portal-screen" ref={screen} style={{ width: vp.W, height: vp.H, transform: css(H0) }}>
            {children}
            <div className="portal-glare" aria-hidden="true" />
          </div>
          <img className="portal-photo" src={img} alt="" fetchpriority="high" style={{ left: L.ox, top: L.oy, width: L.pw, height: L.ph }} />
        </div>
        {dim && <div className="portal-veil" ref={veil} />}
        {caption && <div className="portal-cap" ref={cap}>{caption}</div>}
      </div>
    </section>
  );
}
