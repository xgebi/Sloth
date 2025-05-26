import 'server-only'

import {AuthnData, UserInfo} from "@/app/interfaces/authn-data";
import {authenticateUser, keepLoggedIn} from "@/app/repository/authn.repository";
import {cookies} from "next/headers";
import {ErrorMessage} from "@/app/interfaces/error-message";

export async function loginUser(loginData: AuthnData): Promise<UserInfo | ErrorMessage> {
	const info = await authenticateUser(loginData);
	if (info.hasOwnProperty('error')) {
		return info;
	}
	const cookieStore = await cookies()
	cookieStore.set('sloth-admin-token', JSON.stringify(info), {secure: process.env['MODE'] !== 'dev'})
	return info;
}

export async function keepLoggedInCheck() {
	return keepLoggedIn();
}