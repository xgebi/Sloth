"use server";

import {loginUser} from "@/app/services/authn.service";
import {redirect} from "next/navigation";

export async function processLogin(formData: FormData) {
	const username = formData.get('username');
	const password = formData.get('password');

	if (username && username.toString().length > 0 && password && password.toString().length > 0) {
		const result = await loginUser({
			username: username.toString(),
			password: password.toString(),
		});
		if (result.hasOwnProperty('uuid')) {
			redirect("/dashboard");
		} else {
			redirect("/login?error=credentials");
		}
	}
}