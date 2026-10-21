// The film: a list of segments laid out along the scroll (lengths in vh).
// Each segment plays a slice of a frame sequence; transitions blend two segments at their boundary.
import { CHAPTERS } from '../content.js';

export const SEQ = {
  curtain: 83, city: 84, cafe: 82, craft: 83, dent: 81, law: 81, fit: 81, barber: 82, food: 83, hotel: 82, night: 84,
};

// sk: the scene starts as a silent line drawing and fills with colour
export const SEGS = [
  { id: 'intro', seq: 'curtain', len: 110, fr: [0, 0.04] },
  { id: 'curtain', seq: 'curtain', len: 190, fr: [0.04, 1] },
  { id: 'city', seq: 'city', len: 230, fr: [0, 1], sk: true },
  ...CHAPTERS.map((c, i) => ({ id: c.id, seq: c.seq, len: 175, fr: [0, 1], sk: true, ch: i })),
  { id: 'night', seq: 'night', len: 230, fr: [0, 1] },
  { id: 'manifest', seq: 'night', len: 170, fr: [1, 1], dark: true },
];

// transition into segment k (from k-1): type + width in vh
// 0 cross, 1 dither, 2 ink, 3 zoom, 4 light wipe, 5 slices, 6 to black
const INTO = {
  city: [3, 70], cafe: [1, 60], craft: [2, 60], dent: [4, 56], law: [5, 46], fit: [3, 56], barber: [1, 60],
  food: [2, 60], hotel: [4, 56], night: [3, 70], manifest: [6, 60],
};

let acc = 0;
for (const s of SEGS) { s.start = acc; acc += s.len; s.end = acc; const t = INTO[s.id]; s.tin = t ? { type: t[0], w: t[1] } : null; }
export const TOTAL = acc; // film length in vh (the stage adds one more viewport)

export const segById = Object.fromEntries(SEGS.map((s) => [s.id, s]));
export const segAt = (vh) => SEGS.find((s) => vh < s.end) || SEGS[SEGS.length - 1];

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
export const range = (v, a, b) => clamp01((v - a) / (b - a));
const smooth = (t) => t * t * (3 - 2 * t);

function frameOf(seg, local) {
  const n = SEQ[seg.seq];
  const f = (seg.fr[0] + (seg.fr[1] - seg.fr[0]) * clamp01(local)) * (n - 1);
  return f;
}
function sketchOf(seg, local) {
  return seg.sk ? 1 - smooth(range(local, 0.1, 0.5)) : 0;
}
function layer(seg, vh) {
  const local = (vh - seg.start) / seg.len;
  return { seq: seg.seq, f: frameOf(seg, local), sk: sketchOf(seg, local), zoom: 1.0 + 0.06 * clamp01(local), dark: !!seg.dark };
}

// what the GL renderer should draw at a film position (vh)
export function frameState(vh) {
  const i = SEGS.indexOf(segAt(vh));
  const seg = SEGS[i];
  const next = SEGS[i + 1];
  const st = { a: layer(seg, vh), b: null, t: 0, type: 0 };
  if (next && next.tin && vh > next.start - next.tin.w / 2) {
    st.a = layer(seg, vh);
    st.b = layer(next, vh);
    st.t = range(vh, next.start - next.tin.w / 2, next.start + next.tin.w / 2);
    st.type = next.tin.type;
  } else if (seg.tin && vh < seg.start + seg.tin.w / 2 && i > 0) {
    st.a = layer(SEGS[i - 1], vh);
    st.b = layer(seg, vh);
    st.t = range(vh, seg.start - seg.tin.w / 2, seg.start + seg.tin.w / 2);
    st.type = seg.tin.type;
  }
  return st;
}

// local progress of a segment (may be <0 or >1)
export const localOf = (id, vh) => { const s = segById[id]; return (vh - s.start) / s.len; };

// the clock in the corner: a day from 06:58 to 23:59
const CLOCK = [
  [segById.city.start, 6 * 60 + 40],
  [segById.city.start + segById.city.len * 0.62, 6 * 60 + 58],
  ...CHAPTERS.map((c) => {
    const s = segById[c.id];
    const [h, m] = c.time.split(':').map(Number);
    return [s.start + s.len * 0.45, h * 60 + m];
  }),
  [segById.night.start + segById.night.len * 0.3, 23 * 60 + 59],
];
export function clockAt(vh) {
  if (vh <= CLOCK[0][0]) return '00:00';
  for (let k = 1; k < CLOCK.length; k++) {
    if (vh <= CLOCK[k][0]) {
      const [x0, y0] = CLOCK[k - 1];
      const [x1, y1] = CLOCK[k];
      const m = Math.round(y0 + (y1 - y0) * ((vh - x0) / (x1 - x0)));
      return String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0');
    }
  }
  return '23:59';
}

// where to scroll for "show chapter i" (its calm moment, text and card on screen)
export const chapterHoldVh = (i) => { const s = segById[CHAPTERS[i].id]; return s.start + s.len * 0.62; };
