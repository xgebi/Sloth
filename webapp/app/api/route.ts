// functions need to be named as HTTP method names
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function GET(request: Request) {
	return new Response('Hi');
}