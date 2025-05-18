"use client";

import styles from './login.module.css';

import {processLogin} from "@/app/(authentication)/login/login";
import Form from "next/form";
import {useSearchParams} from "next/navigation";
import Cookies from 'js-cookie'

export default function LoginPage() {
	const searchParams = useSearchParams()
	const error = searchParams.get('error');
	const rawCookie = Cookies.get('sloth-admin-token');
	console.log(rawCookie);
	if (rawCookie) {
		console.log('abc')
		const cookie = JSON.parse(rawCookie);
		console.log('def', cookie, cookie.uuid, (cookie.expiryTime * 1000), (new Date()).getTime())
		if (cookie.uuid && (cookie.expiryTime * 1000) > (new Date()).getTime()) {
			// there might be a better way, good enough for now, it after 10pm
			window.location.replace(`${window.location.origin}/dashboard`);
		}
	}

	return (
		<main className={styles['login-wrapper']}>
			<section className={styles['login-section']}>
				{error && <p className={styles['error-box']}>Incorrect credentials</p>}
					<Form action={processLogin}>
						<div>
							<label htmlFor="username-field">Username:</label>
							<input type="text" id="username-field" name="username" />
						</div>
						<div>
							<label htmlFor="password-field">Password:</label>
							<input type="password" id="password-field" name="password" />
						</div>
						<div>
								<button>Login</button>
						</div>
					</Form>
			</section>
		</main>
	)
}