import {AbsoluteFill, continueRender, delayRender, Html5Audio, Img, interpolate, random, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

// AUREL: izmišljen luksuzni sat, 10 s za Reels i TikTok (1080 × 1920).
// 0–3 s POV vrteška (Blender, pravo zamućenje pokreta) → match cut u makro brojčanika
// → match cut-ovi boja na udarac (5,6–6,4 s) → odmicanje do celog sata → logo.
export const AUREL_TRAJANJE = 300;

const ZLATO = '#d6b77a';
const KREM = '#f4efe6';
const SERIF = "'Instrument Serif', serif";
const SANS = "'Inter', sans-serif";
const MONO = "'JetBrains Mono', monospace";

const cekaj = delayRender('AUREL fontovi');
Promise.all(
	[
		new FontFace('Instrument Serif', `url(${staticFile('fonts/instrument-serif.woff2')})`),
		new FontFace('Instrument Serif', `url(${staticFile('fonts/instrument-serif-italic.woff2')})`, {style: 'italic'}),
	].map((f) => f.load().then((ff) => document.fonts.add(ff))),
)
	.then(() => continueRender(cekaj))
	.catch(() => continueRender(cekaj));

const kadar = (f: number) => staticFile(`aurel/kadrovi/${String(Math.min(Math.max(f, 1), AUREL_TRAJANJE)).padStart(4, '0')}.png`);

type Rec = {t: string; kurziv?: boolean};

// reči ulaze jedna po jedna iz 3D (rotateX) sa oprugom, a izlaze kroz zamućenje
const Red: React.FC<{reci: Rec[]; od: number; do: number; y: number; vel: number; boja?: string}> = ({reci, od, do: kraj, y, vel, boja = KREM}) => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	if (f < od || f > kraj) return null;
	const izlaz = interpolate(f, [kraj - 7, kraj], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	return (
		<div
			style={{
				position: 'absolute',
				top: y,
				left: 80,
				right: 140,
				display: 'flex',
				flexWrap: 'wrap',
				justifyContent: 'center',
				alignItems: 'baseline',
				columnGap: vel * 0.24,
				perspective: 900,
				opacity: 1 - izlaz,
				filter: `blur(${izlaz * 10}px)`,
				translate: `0px ${-izlaz * 30}px`,
			}}
		>
			{reci.map((r, i) => {
				const p = spring({frame: f - od - i * 4, fps, config: {damping: 14, stiffness: 160, mass: 0.7}});
				return (
					<span
						key={i}
						style={{
							display: 'inline-block',
							fontFamily: r.kurziv ? SERIF : SANS,
							fontStyle: r.kurziv ? 'italic' : 'normal',
							fontWeight: r.kurziv ? 400 : 300,
							fontSize: r.kurziv ? vel * 1.15 : vel,
							letterSpacing: r.kurziv ? '0' : '-0.01em',
							color: r.kurziv ? ZLATO : boja,
							opacity: Math.min(1, p * 1.6),
							rotate: `x ${(1 - p) * 80}deg`,
							scale: String(1 + (1 - p) * 0.35),
							filter: `blur(${(1 - p) * 8}px)`,
							textShadow: '0 8px 40px rgba(0,0,0,0.6)',
						}}
					>
						{r.t}
					</span>
				);
			})}
		</div>
	);
};

const BOJE = ['SCHWARZ', 'GRÜN', 'BLAU', 'CHAMPAGNER', 'SCHWARZ'];

const OznakaBoje: React.FC = () => {
	const f = useCurrentFrame();
	if (f < 168 || f >= 193) return null;
	const i = Math.floor((f - 168) / 5);
	const lok = (f - 168) % 5;
	return (
		<div style={{position: 'absolute', left: 0, right: 0, top: 1380, textAlign: 'center', fontFamily: MONO, fontSize: 34, letterSpacing: '0.4em', color: KREM, opacity: lok === 0 ? 0.5 : 1}}>
			{BOJE[i]}
		</div>
	);
};

const Logo: React.FC = () => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	const OD = 238;
	if (f < OD) return null;
	const p = spring({frame: f - OD, fps, config: {damping: 200}, durationInFrames: 28});
	const rastojanje = interpolate(f, [OD, 300], [0.9, 0.42], {extrapolateRight: 'clamp'});
	const linija = interpolate(f, [OD + 10, OD + 30], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const podnaslov = interpolate(f, [OD + 22, OD + 34], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const sitno = interpolate(f, [OD + 34, OD + 46], [0, 0.7], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	return (
		<AbsoluteFill style={{alignItems: 'center'}}>
			<AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0) 38%, rgba(0,0,0,0) 62%, rgba(0,0,0,0.7) 100%)', opacity: p}} />
			<div style={{position: 'absolute', top: 260, fontFamily: SERIF, fontSize: 150, color: KREM, letterSpacing: `${rastojanje}em`, opacity: p, filter: `blur(${(1 - p) * 14}px)`, paddingLeft: `${rastojanje}em`}}>
				AUREL
			</div>
			<div style={{position: 'absolute', top: 455, width: 360 * linija, height: 1.5, background: ZLATO}} />
			<div style={{position: 'absolute', top: 490, fontFamily: SERIF, fontStyle: 'italic', fontSize: 64, color: ZLATO, opacity: podnaslov, translate: `0px ${(1 - podnaslov) * 20}px`}}>
				Die Zeit gehört dir.
			</div>
			<div style={{position: 'absolute', top: 1390, fontFamily: MONO, fontSize: 24, letterSpacing: '0.35em', color: KREM, opacity: sitno}}>AUTOMATIK · 40 MM · 200 M</div>
			<div style={{position: 'absolute', top: 1450, fontFamily: SANS, fontSize: 20, color: KREM, opacity: sitno * 0.6}}>Konzept · Nemi Studio</div>
		</AbsoluteFill>
	);
};

export const Aurel: React.FC = () => {
	const f = useCurrentFrame();
	// mali „udar" kamere na svaki match cut boje
	const udar = f >= 168 && f < 193 && (f - 168) % 5 === 0 ? 1.035 : 1;
	const vinjeta = 'radial-gradient(ellipse 80% 60% at 50% 48%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)';
	return (
		<AbsoluteFill style={{background: '#050505'}}>
			<Html5Audio src={staticFile('sfx/aurel_podloga.wav')} volume={0.8} />
			<AbsoluteFill style={{scale: String(udar)}}>
				<Img src={kadar(f + 1)} style={{width: '100%', height: '100%'}} />
			</AbsoluteFill>
			<AbsoluteFill style={{background: vinjeta}} />
			{/* zrno filma */}
			<AbsoluteFill style={{opacity: 0.06, backgroundImage: `radial-gradient(circle at ${random(`x${f}`) * 100}% ${random(`y${f}`) * 100}%, #fff 0.5px, transparent 1px)`, backgroundSize: '3px 3px'}} />

			<Red od={6} do={40} y={300} vel={92} reci={[{t: 'Alles'}, {t: 'dreht sich', kurziv: true}]} />
			<Red od={42} do={86} y={300} vel={92} reci={[{t: 'um'}, {t: 'einen'}, {t: 'Moment.', kurziv: true}]} />
			<Red od={100} do={140} y={250} vel={104} reci={[{t: 'Präzision,', kurziv: true}]} />
			<Red od={140} do={166} y={250} vel={84} reci={[{t: 'Sekunde'}, {t: 'für'}, {t: 'Sekunde.', kurziv: true}]} />
			<OznakaBoje />
			<Red od={198} do={236} y={270} vel={84} reci={[{t: 'Gebaut'}, {t: 'für'}, {t: 'die'}, {t: 'Tiefe.', kurziv: true}]} />
			<Logo />

			<Sequence from={0} durationInFrames={80} layout="none">
				<Html5Audio src={staticFile('sfx/aurel_vrtnja.wav')} volume={0.9} />
			</Sequence>
			{[90, 150, 153, 156, 159, 162].map((k) => (
				<Sequence key={k} from={k} durationInFrames={6} layout="none">
					<Html5Audio src={staticFile('sfx/aurel_klik.wav')} volume={k === 90 ? 1 : 0.6} />
				</Sequence>
			))}
			{Array.from({length: 18}, (_, i) => 92 + i * 4).map((k) => (
				<Sequence key={`t${k}`} from={k} durationInFrames={3} layout="none">
					<Html5Audio src={staticFile('sfx/aurel_tik.wav')} volume={0.5} />
				</Sequence>
			))}
			{[168, 173, 178, 183, 188].map((k) => (
				<Sequence key={`b${k}`} from={k} durationInFrames={20} layout="none">
					<Html5Audio src={staticFile('sfx/hit.wav')} volume={0.55} />
				</Sequence>
			))}
			<Sequence from={238} durationInFrames={62} layout="none">
				<Html5Audio src={staticFile('sfx/aurel_udar.wav')} volume={1} />
			</Sequence>
		</AbsoluteFill>
	);
};
