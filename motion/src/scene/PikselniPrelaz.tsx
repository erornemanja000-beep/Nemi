import {AbsoluteFill, random, useCurrentFrame} from 'remotion';
import {C} from '../theme';

// Tehnika 2: ekran se pokrije kvadratima nasumičnim redom, pa se otkriva sledeća scena.
// Kadrovi 0–8: kvadrati se pojavljuju; 9–11: ekran je ceo pokriven (tu se menja scena); 12–21: nestaju.
export const PIKSELNI_PRELAZ_TRAJANJE = 22;

const KOLONE = 16;
const REDOVI = 9;
const VELICINA = 120;

const boja = (i: number) => {
	const r = random(`boja${i}`);
	if (r < 0.35) return C.red;
	if (r < 0.55) return C.white;
	if (r < 0.85) return C.black;
	return C.darkRed;
};

export const PikselniPrelaz: React.FC = () => {
	const f = useCurrentFrame();
	const polja = [];
	for (let i = 0; i < KOLONE * REDOVI; i++) {
		const ulaz = Math.floor(random(`ulaz${i}`) * 9);
		const izlaz = 12 + Math.floor(random(`izlaz${i}`) * 10);
		if (f < ulaz || f >= izlaz) continue;
		polja.push(
			<div
				key={i}
				style={{
					position: 'absolute',
					left: (i % KOLONE) * VELICINA,
					top: Math.floor(i / KOLONE) * VELICINA,
					width: VELICINA,
					height: VELICINA,
					background: boja(i),
				}}
			/>,
		);
	}
	return <AbsoluteFill>{polja}</AbsoluteFill>;
};
