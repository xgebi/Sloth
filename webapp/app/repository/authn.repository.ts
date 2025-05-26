import {AuthnData, LoginStatus, UserInfo} from "@/app/interfaces/authn-data";
import {ErrorMessage} from "@/app/interfaces/error-message";
import {cookies} from "next/headers";

export async function authenticateUser(loginData: AuthnData) {
	const result = await fetch(`${process.env['BACKEND_URL']}/api/v2/login`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(loginData),
	});
	const resultObj: object = await result.json();
	if (resultObj.hasOwnProperty('error')) {
		return (resultObj as ErrorMessage);
	}
	return resultObj as UserInfo;
}

export async function keepLoggedIn() {
	const cookieStore = await cookies();
  const rawCookie = cookieStore.get('sloth-admin-token');
	if (rawCookie) {
		const cookie = JSON.parse(rawCookie.value);
		const result = await fetch(`${process.env['BACKEND_URL']}/api/v2/check-in`, {
			method: "POST",
			headers: {
				'authorization': `${cookie.displayName}:${cookie.uuid}:${cookie.token}`
			},
		});
		const resultObj: object = await result.json();
		if (resultObj.hasOwnProperty('error')) {
			return (resultObj as ErrorMessage);
		}
		return resultObj as LoginStatus;
	}
}