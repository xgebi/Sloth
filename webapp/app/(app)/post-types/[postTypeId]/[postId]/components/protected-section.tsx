import {SyntheticEvent, useState} from "react";
import styles from '../post.module.css';

interface ProtectedSectionProps {
	passedPassword: string,
	passwordUpdated: (password: string) => void
}

export default function ProtectedSection({ passedPassword, passwordUpdated }: ProtectedSectionProps) {
	const [protectedPost, setProtectedPost] = useState(passedPassword && passedPassword.length > 0);
	const [password, setPassword] = useState(passedPassword ? passedPassword : '')

	function changeProtectedState() {
		if (protectedPost) {
			passwordUpdated('');
		}
		setProtectedPost(!protectedPost);
	}

	function updatePassword(ev: SyntheticEvent) {
		const val = (ev.target as HTMLInputElement).value;
		setPassword(val);
		passwordUpdated(val);
	}

	return (
		<>
			<button onClick={changeProtectedState}>{protectedPost ? "Cancel protection" : "Change to protected"}</button>
			{protectedPost && <div>
				<label htmlFor="password-post">Password for post:</label>
				<input type="text" id="password-post" value={password} onInput={updatePassword} className={styles['aside-input']} />
			</div>}
		</>
	)
}