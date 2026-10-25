import {AbsoluteFill, Html5Audio, Img, interpolate, interpolateColors, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import podaci from './wuerfel-podaci.json';
import {blenderKadar, GlitchSlika, Iskace, Kocka3D, Lik, MONO, Mozaik, N, SANS} from './wuerfel/delovi';
import {Zvuk} from './ui';

// „Würfelwelt": 10 s za Reels i TikTok (1080 × 1920).
// MagicaVoxel: ostrvo (wuerfelwelt/diorama.vox) · Blender: gradnja, kamera i noć (wuerfelwelt/blender_scena.py)
// Pixelorama: lik Kocko (wuerfelwelt/lik_sheet.png) · Remotion: tekst, prelazi, ritam i zvuk.
export const WUERFELWELT_TRAJANJE = 300;

const BL_OD = 6; // Remotion kadar u kom se vidi Blender kadar 1
const BL_KRAJ = 225;
const blender = (f: number) => Math.min(BL_KRAJ, Math.max(1, f - BL_OD + 1));
const remotion = (b: number) => b + BL_OD - 1;

const MOZAIK_OD = 97;
const SVETLA = remotion(160);
const GLITCH_OD = 224;
const KARTICA_OD = 236;

const sleteli = podaci.slojevi.map((s) => ({kada: remotion(s.sleteo), kocke: s.kocke}));

const Brojac: React.FC = () => {
	const f = useCurrentFrame();
	const broj = sleteli.filter((s) => s.kada <= f).reduce((a, s) => a + s.kocke, 0);
	const vidljiv = interpolate(f, [10, 16, 92, 100], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	return (
		<div style={{position: 'absolute', left: 90, top: 1330, opacity: vidljiv, fontFamily: MONO, color: N.bone}}>
			<div style={{fontSize: 26, letterSpacing: '0.2em', opacity: 0.6}}>WÜRFEL</div>
			<div style={{fontSize: 96, fontWeight: 800, lineHeight: 1, fontVariantNumeric: 'tabular-nums'}}>
				{broj.toLocaleString('de-AT')}
			</div>
		</div>
	);
};

const Scena3D: React.FC = () => {
	const f = useCurrentFrame();
	const noc = interpolate(f, [remotion(150), remotion(178)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const sjaj = interpolateColors(noc, [0, 1], ['#3a1d12', '#16203a']);
	// mali udar kamere kad prva kocka sleti
	const udar = remotion(podaci.slojevi[0].sleteo);
	const s = f >= udar && f < udar + 6 ? (1 - (f - udar) / 6) * 14 : 0;
	const glitch = interpolate(f, [GLITCH_OD, GLITCH_OD + 4, KARTICA_OD], [0, 1, 0.6], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const tama = interpolate(f, [KARTICA_OD - 6, KARTICA_OD], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	return (
		<AbsoluteFill>
			<AbsoluteFill style={{background: `radial-gradient(ellipse 70% 45% at 50% 48%, ${sjaj} 0%, ${N.ink} 75%)`}} />
			<AbsoluteFill style={{transform: `translate(${Math.sin(f * 7) * s}px, ${Math.cos(f * 5) * s}px)`}}>
				{f >= BL_OD && glitch === 0 && <Img src={blenderKadar(blender(f))} style={{width: '100%', height: '100%'}} />}
				{glitch > 0 && <GlitchSlika src={blenderKadar(blender(f))} jacina={glitch} />}
			</AbsoluteFill>
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 50%, transparent 55%, rgba(0,0,0,0.55) 100%)'}} />
			<AbsoluteFill style={{background: N.ink, opacity: tama}} />
		</AbsoluteFill>
	);
};

// Kocko ulazi sleva, hoda (4 kadra, 7,5 kadrova u sekundi), stane i maše
const KockoHoda: React.FC = () => {
	const f = useCurrentFrame();
	const OD = 126;
	const STANE = 188;
	if (f < OD || f >= KARTICA_OD) return null;
	const x = interpolate(f, [OD, STANE], [-170, 300], {extrapolateRight: 'clamp'});
	const kadar = f < STANE ? Math.floor((f - OD) / 4) % 4 : Math.floor((f - STANE) / 5) % 2 === 0 ? 4 : 0;
	return <Lik kadar={kadar} x={x} y={1290} />;
};

const Kartica: React.FC = () => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	const k = spring({frame: f - KARTICA_OD - 2, fps, config: {damping: 10, stiffness: 160}});
	const kraj = interpolate(f, [WUERFELWELT_TRAJANJE - 8, WUERFELWELT_TRAJANJE], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	if (f < KARTICA_OD) return null;
	const kadar = Math.floor((f - KARTICA_OD) / 6) % 2 === 0 ? 4 : 0;
	return (
		<AbsoluteFill>
			<AbsoluteFill style={{background: `radial-gradient(ellipse 60% 40% at 50% 30%, #2a140c 0%, ${N.ink} 70%)`}} />
			<div style={{position: 'absolute', top: 280, left: 0, right: 70, display: 'flex', justifyContent: 'center', transform: `scale(${k})`}}>
				<Kocka3D velicina={210} rx={-24 + Math.sin(f / 14) * 6} ry={f * 2.6} />
			</div>
			<Iskace od={KARTICA_OD + 10} do={WUERFELWELT_TRAJANJE + 10} y={640} velicina={44} delovi={[{t: 'Gebaut'}, {t: 'mit'}]} />
			<Iskace od={KARTICA_OD + 14} do={WUERFELWELT_TRAJANJE + 10} y={720} velicina={96} delovi={[{t: 'MagicaVoxel'}]} />
			<Iskace od={KARTICA_OD + 20} do={WUERFELWELT_TRAJANJE + 10} y={830} velicina={96} delovi={[{t: 'Blender'}]} />
			<Iskace od={KARTICA_OD + 26} do={WUERFELWELT_TRAJANJE + 10} y={940} velicina={96} delovi={[{t: 'Pixelorama', istaknuto: true}]} />
			<Iskace od={KARTICA_OD + 36} do={WUERFELWELT_TRAJANJE + 10} y={1120} velicina={52} delovi={[{t: 'nemistudio.at'}]} />
			<Lik kadar={kadar} x={460} y={1250} />
			<div
				style={{
					position: 'absolute',
					top: 1190,
					left: 90,
					right: 160,
					textAlign: 'center',
					fontFamily: MONO,
					fontSize: 22,
					letterSpacing: '0.18em',
					color: N.bone,
					opacity: interpolate(f, [KARTICA_OD + 40, KARTICA_OD + 48], [0, 0.55], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
				}}
			>
				VOXEL · 3D · PIXEL
			</div>
			<AbsoluteFill style={{background: N.ink, opacity: kraj}} />
		</AbsoluteFill>
	);
};

export const Wuerfelwelt: React.FC = () => (
	<AbsoluteFill style={{background: N.ink, fontFamily: SANS}}>
		<Html5Audio src={staticFile('sfx/beat10.wav')} volume={0.4} />

		<Scena3D />
		<Brojac />

		<Iskace od={12} do={44} y={300} delovi={[{t: 'Ein'}, {t: 'Würfel.', istaknuto: true}]} />
		<Iskace od={46} do={74} y={300} delovi={[{t: 'Dann'}, {t: 'viele.', istaknuto: true}]} />
		<Iskace od={76} do={100} y={300} delovi={[{t: 'Bis'}, {t: 'es'}, {t: 'eine'}, {t: 'Welt', istaknuto: true}, {t: 'ist.'}]} />
		<Iskace od={122} do={154} y={260} delovi={[{t: 'Ein'}, {t: 'kleines'}, {t: 'Café.', istaknuto: true}]} />
		<Iskace od={SVETLA - 2} do={196} y={260} delovi={[{t: 'Licht'}, {t: 'an.', istaknuto: true}]} />
		<Iskace od={198} do={GLITCH_OD + 2} y={260} glitch delovi={[{t: 'Und'}, {t: 'Bewegung.', istaknuto: true}]} />

		<KockoHoda />

		<Sequence from={MOZAIK_OD} durationInFrames={20}>
			<Mozaik trajanje={20} />
		</Sequence>

		<Kartica />

		{/* zvuk za svaki pokret */}
		<Zvuk fajl="hit.wav" od={remotion(podaci.slojevi[0].sleteo)} jacina={0.9} />
		{sleteli.slice(1).map((s, i) => (
			<Zvuk key={i} fajl="tick.wav" od={s.kada} jacina={0.22} />
		))}
		{[12, 46, 76, 122, 198].map((k) => (
			<Zvuk key={k} fajl="pop.wav" od={k} jacina={0.6} />
		))}
		<Zvuk fajl="whoosh.wav" od={MOZAIK_OD - 3} />
		<Zvuk fajl="chime.wav" od={SVETLA} jacina={0.7} />
		<Zvuk fajl="tick.wav" od={SVETLA + 7} jacina={0.5} />
		<Zvuk fajl="glitch.wav" od={198} jacina={0.6} />
		<Zvuk fajl="glitch.wav" od={GLITCH_OD} jacina={0.9} />
		<Zvuk fajl="hit.wav" od={KARTICA_OD + 2} jacina={0.8} />
		{[14, 20, 26].map((k) => (
			<Zvuk key={k} fajl="pop.wav" od={KARTICA_OD + k} jacina={0.5} />
		))}
		<Zvuk fajl="hit.wav" od={KARTICA_OD + 36} jacina={0.6} />
	</AbsoluteFill>
);
