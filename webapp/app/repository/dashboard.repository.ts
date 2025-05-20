import {cookies} from "next/headers";

export async function fetchDashboardData() {
	const cookieStore = await cookies()
  const rawCookie = cookieStore.get('sloth-admin-token')
	if (rawCookie) {
		const cookie = JSON.parse(rawCookie.value);
		console.log(`${process.env['BACKEND_URL']}/api/dashboard-information`);
		try {
			const fetched = await fetch(`${process.env['BACKEND_URL']}/api/dashboard-information`, {
				method: "GET",
				headers: {
					'authorization': `${cookie.displayName}:${cookie.uuid}:${cookie.token}`
				},
			});
			return await fetched.json()
		} catch (_) {
			return { error: "Cannot connect to backend" }
		}
	}
}