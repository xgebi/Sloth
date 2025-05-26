import {cookies} from "next/headers";
import SlothConstants from "@/constants";
import {redirect} from "next/navigation";
import {SlothCookie} from "@/app/interfaces/sloth-cookie";
import {keepLoggedInCheck} from "@/app/services/authn.service";

export async function checkLoggingCookie() {
	const cookieStore = await cookies()
	const token = cookieStore.get(SlothConstants.Token);
	if (token) {
		let parsedToken: SlothCookie | null = null;
		parsedToken = JSON.parse(token?.value);
		if (parsedToken && (parsedToken.expiryTime!) >= Date.now()) {
			const status = await keepLoggedInCheck();
			if (status && status.hasOwnProperty('status')) {
				const newExpiry = Date.now() + (30 * 60 * 1000);
				parsedToken = {
					...parsedToken,
					expiryTime: newExpiry
				};
				cookieStore.set('sloth-admin-token', JSON.stringify(parsedToken), {secure: process.env['MODE'] !== 'dev'})
				return;
			}
		}
	}
	redirect("/login");
}