import {cookies} from "next/headers";
import {ErrorMessage} from "@/app/interfaces/error-message";
import {Message} from "@/app/interfaces/message";

export async function fetchSettingsByType(settingsType: string) {
	const cookieStore = await cookies()
  const rawCookie = cookieStore.get('sloth-admin-token')
	if (rawCookie) {
		const cookie = JSON.parse(rawCookie.value);
		const result = await fetch(`${process.env['BACKEND_URL']}/api/settings/type/${settingsType}>`, {
			method: "GET",
			headers: {
				'authorization': `${cookie.displayName}:${cookie.uuid}:${cookie.token}`
			},
		});
		console.log('gdi', result.body);
		const resultObj: object = await result.json();
		console.log('abc', resultObj);
		if (resultObj.hasOwnProperty('error')) {
			return (resultObj as ErrorMessage);
		}
		return resultObj as Message;
	}
}

export async function saveSetting(settingName: string, settingValue: string) {
	const cookieStore = await cookies()
  const rawCookie = cookieStore.get('sloth-admin-token')
	if (rawCookie) {
		const cookie = JSON.parse(rawCookie.value);
		const result = await fetch(`${process.env['BACKEND_URL']}/api/settings`, {
			method: "POST",
			headers: {
				'authorization': `${cookie.displayName}:${cookie.uuid}:${cookie.token}`
			},
		});
		console.log('gdi', result.body);
		const resultObj: object = await result.json();
		console.log('abc', resultObj);
		if (resultObj.hasOwnProperty('error')) {
			return (resultObj as ErrorMessage);
		}
		return resultObj as Message;
	}
}