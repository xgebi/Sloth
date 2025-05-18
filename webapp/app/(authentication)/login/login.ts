"use server";

import {loginUser} from "@/app/services/login.service";
import {redirect} from "next/navigation";

export async function processLogin(formData: FormData) {
	const username = formData.get('username');
	const password = formData.get('password');

	if (username && username.toString().length > 0 && password && password.toString().length > 0) {
		const result = await loginUser({
			username: username.toString(),
			password: password.toString(),
		});
		console.log(result);
		if (result.hasOwnProperty('uuid')) {
			console.log('def');
			redirect("/dashboard");
		}
	}
}