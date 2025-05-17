import {NextRequest, NextResponse} from "next/server";

export const config = {
  matcher: ['/dashboard/:path*', '/post-types/:path*', '/settings/:path*', '/api/:path*'],
}

export function middleware(request: NextRequest) {
	console.log('abc', request.nextUrl.pathname);
	const token = request.cookies.get("slothAuthToken");
	if (!token) {
		return NextResponse.redirect(new URL('/login', request.url))
	}
  return NextResponse.next();
}