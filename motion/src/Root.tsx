import {Composition} from 'remotion';
import {Probni, PROBNI_TRAJANJE} from './Probni';
import {FPS} from './theme';
import {Wuerfelwelt, WUERFELWELT_TRAJANJE} from './Wuerfelwelt';

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
	</>
);
