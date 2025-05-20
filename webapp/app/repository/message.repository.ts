import {ErrorMessage} from "@/app/interfaces/error-message";
import {cookies} from "next/headers";
import {Message} from "@/app/interfaces/message";

export async function fetchMessages() {
	const cookieStore = await cookies()
  const rawCookie = cookieStore.get('sloth-admin-token')
	if (rawCookie) {
		const cookie = JSON.parse(rawCookie.value);
		const result = await fetch(`${process.env['BACKEND_URL']}/api/messages`, {
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
		return resultObj as Message[];
	}
}

export async function fetchMessage(messageId: string) {
	const cookieStore = await cookies()
  const rawCookie = cookieStore.get('sloth-admin-token')
	if (rawCookie) {
		const cookie = JSON.parse(rawCookie.value);
		const result = await fetch(`${process.env['BACKEND_URL']}/api/messages/${messageId}`, {
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