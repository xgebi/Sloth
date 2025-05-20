import {ErrorMessage} from "@/app/interfaces/error-message";
import {cookies} from "next/headers";

export async function simpleGet(pathname: string): Promise<object | ErrorMessage> {
	const cookieStore = await cookies()
  const rawCookie = cookieStore.get('sloth-admin-token')
	if (rawCookie) {
		const cookie = JSON.parse(rawCookie.value);
		try {
			const fetched = await fetch(`${process.env['BACKEND_URL']}${pathname}`, {
				method: "GET",
				headers: {
					'authorization': `${cookie.displayName}:${cookie.uuid}:${cookie.token}`
				},
			});
			return await fetched.json();
		} catch (_) {
			return { error: "Cannot connect to backend" }
		}
	}
	return { error: "Cookie issue"}
}