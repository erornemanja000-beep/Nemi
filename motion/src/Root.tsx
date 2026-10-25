import {Composition} from 'remotion';
import {Probni, PROBNI_TRAJANJE} from './Probni';
import {FPS} from './theme';

export const Root: React.FC = () => (
	<Composition
		id="Probni"
		component={Probni}
		durationInFrames={PROBNI_TRAJANJE}
		fps={FPS}
		width={1920}
		height={1080}
	/>
);
