"use client";

import styles from './login.module.css';
import {SyntheticEvent, useState} from "react";

export default function LoginPage() {
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');

	function updateUsername(ev: SyntheticEvent) {
		setUsername((ev.target as HTMLInputElement).value);
	}

	function updatePassword(ev: SyntheticEvent) {
		setPassword((ev.target as HTMLInputElement).value);
	}

	return (
		<main className={styles['login-wrapper']}>
			<section className={styles['login-section']}>
				<form>
					<div>
						<label htmlFor="username-field">Username:</label>
						<input type="text" value={username} onInput={updateUsername} />
					</div>
					<div>
						<label htmlFor="username-field">Password:</label>
						<input type="password" value={password} onInput={updatePassword} />
					</div>
					<div>
						<button>Login</button>
					</div>
				</form>
			</section>
		</main>
	)
}