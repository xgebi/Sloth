import {LoginData, UserInfo} from "@/app/interfaces/login-data";
import {ErrorMessage} from "@/app/interfaces/error-message";

export async function authenticateUser(loginData: LoginData) {
	const result = await fetch(`${process.env['BACKEND_URL']}/api/login`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(loginData),
	});
	console.log('gdi', result.body);
	const resultObj: object = await result.json();
	console.log('abc', resultObj);
	if (resultObj.hasOwnProperty('error')) {
		return (resultObj as ErrorMessage);
	}
	return resultObj as UserInfo;

}