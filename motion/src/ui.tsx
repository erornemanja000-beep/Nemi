import {AbsoluteFill, Html5Audio, Sequence, staticFile} from 'remotion';
import {C, FONT} from './theme';

export const Pozadina: React.FC = () => (
	<AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 45%, ${C.bg2} 0%, ${C.bg} 70%)`}} />
);

// Mali natpis u uglu: koja tehnika se trenutno vidi.
export const Oznaka: React.FC<{tekst: string}> = ({tekst}) => (
	<div
		style={{
			position: 'absolute',
			top: 56,
			left: 72,
			fontFamily: FONT.mono,
			fontSize: 26,
			letterSpacing: '0.12em',
			color: C.teal,
			opacity: 0.85,
		}}
	>
		{tekst}
	</div>
);

// Zvučni efekat koji krene na zadatom kadru.
export const Zvuk: React.FC<{fajl: string; od: number; jacina?: number}> = ({fajl, od, jacina = 1}) => (
	<Sequence from={od} durationInFrames={30} layout="none">
		<Html5Audio src={staticFile(`sfx/${fajl}`)} volume={jacina} />
	</Sequence>
);
