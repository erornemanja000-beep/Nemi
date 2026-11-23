import {Composition} from 'remotion';
import {Probni, PROBNI_TRAJANJE} from './Probni';
import {FPS} from './theme';
import {Wuerfelwelt, WUERFELWELT_TRAJANJE} from './Wuerfelwelt';
import {Pozadina} from './pozadine/Pozadina';
import * as Sim from './pozadine/simulacija';
import {HYPE_SIRINA, HYPE_VISINA, HypeTraka, type HypeProps} from './hype/HypeTraka';

export const Root: React.FC = () => (
	<>
		<Composition
			id="Probni"
			component={Probni}
			durationInFrames={PROBNI_TRAJANJE}
			fps={FPS}
			width={1920}
			height={1080}
		/>
		<Composition
			id="Wuerfelwelt"
			component={Wuerfelwelt}
			durationInFrames={WUERFELWELT_TRAJANJE}
			fps={FPS}
			width={1080}
			height={1920}
		/>
		<Composition
			id="Pozadina"
			component={Pozadina}
			durationInFrames={Sim.TRAJANJE}
			fps={Sim.FPS}
			width={Sim.SIRINA}
			height={Sim.VISINA}
			defaultProps={{seed: 1}}
		/>
		<Composition
			id="HypeTraka"
			component={HypeTraka}
			durationInFrames={300}
			fps={30}
			width={HYPE_SIRINA}
			height={HYPE_VISINA}
			defaultProps={{vrednosti: [], video: 'clipper/voznja.mp4', oznaka: 'HYPE'} as HypeProps}
			calculateMetadata={({props}) => ({durationInFrames: Math.max(1, props.vrednosti.length)})}
		/>
	</>
);
