import {Config} from '@remotion/cli/config';
import {existsSync, readdirSync} from 'node:fs';

// U cloud okruženju Chromium već postoji, pa Remotion ne skida svoj.
// Na tvom računaru ovaj folder ne postoji i Remotion koristi svoj Chrome.
const PW = '/opt/pw-browsers';
if (existsSync(PW)) {
	const dir = readdirSync(PW).find((d) => d.startsWith('chromium_headless_shell-'));
	if (dir) {
		Config.setBrowserExecutable(`${PW}/${dir}/chrome-headless-shell-linux64/chrome-headless-shell`);
	}
}

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
