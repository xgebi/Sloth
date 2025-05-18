import 'server-only'

import {LoginData, UserInfo} from "@/app/interfaces/login-data";
import {authenticateUser} from "@/app/repository/login.repository";
import {cookies} from "next/headers";
import {ErrorMessage} from "@/app/interfaces/error-message";

export async function loginUser(loginData: LoginData): Promise<UserInfo | ErrorMessage> {
	const info = await authenticateUser(loginData);
	if (info.hasOwnProperty('error')) {
		return info;
	}
	const cookieStore = await cookies()
	cookieStore.set('sloth-admin-token', JSON.stringify(info), {secure: process.env['MODE'] !== 'dev'})
	return info;
}