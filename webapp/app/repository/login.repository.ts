import {LoginData, UserInfo} from "@/app/interfaces/login-data";
import {ErrorMessage} from "@/app/interfaces/error-message";

export async function authenticateUser(loginData: LoginData) {
	const result = await fetch(`${process.env['BACKEND_URL']}/api/login`, {
		method: "POST",
		body: JSON.stringify(loginData),
	});
	const resultObj: object = await result.json();
	if (resultObj.hasOwnProperty('error')) {
		return (resultObj as ErrorMessage);
	}
	return resultObj as UserInfo;

}