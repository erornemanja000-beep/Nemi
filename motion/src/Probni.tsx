import {AbsoluteFill, Html5Audio, Sequence, staticFile} from 'remotion';
import {Brojac} from './scene/Brojac';
import {Glitch} from './scene/Glitch';
import {PIKSELNI_PRELAZ_TRAJANJE, PikselniPrelaz} from './scene/PikselniPrelaz';
import {TekstURitmu} from './scene/TekstURitmu';
import {C} from './theme';
import {Zvuk} from './ui';

// Probni klip: četiri tehnike iz analiziranog reel-a, 8,5 s na 30 fps.
// Scene se smenjuju na udarac (svakih 15 kadrova), a pikselni prelaz pokriva rez između prve i druge.
const PRELAZ_OD = 95;
const BROJAC_OD = PRELAZ_OD + 10; // rez je dok je ekran ceo pokriven
const GLITCH_OD = 195;
export const PROBNI_TRAJANJE = 255;

export const Probni: React.FC = () => (
	<AbsoluteFill style={{background: C.bg}}>
		<Html5Audio src={staticFile('sfx/beat.wav')} volume={0.45} />

		<Sequence from={0} durationInFrames={BROJAC_OD}>
			<TekstURitmu />
		</Sequence>
		<Sequence from={BROJAC_OD} durationInFrames={GLITCH_OD - BROJAC_OD}>
			<Brojac />
		</Sequence>
		<Sequence from={GLITCH_OD} durationInFrames={PROBNI_TRAJANJE - GLITCH_OD}>
			<Glitch />
		</Sequence>

		<Sequence from={PRELAZ_OD} durationInFrames={PIKSELNI_PRELAZ_TRAJANJE}>
			<PikselniPrelaz />
		</Sequence>
		<Zvuk fajl="whoosh.wav" od={PRELAZ_OD - 4} jacina={1} />
	</AbsoluteFill>
);
