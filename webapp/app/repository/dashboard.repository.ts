import {cookies} from "next/headers";

export async function fetchDashboardData() {
	const cookieStore = await cookies()
  const rawCookie = cookieStore.get('sloth-admin-token')
	if (rawCookie) {
		const cookie = JSON.parse(rawCookie.value);
		console.log(`${process.env['BACKEND_URL']}/api/dashboard-information`);
		const fetched = await fetch(`${process.env['BACKEND_URL']}/api/dashboard-information`, {
			method: "GET",
			headers: {
				'authorization': `${cookie.displayName}:${cookie.uuid}:${cookie.token}`
			},
		});
		return fetched.json();
	}
}