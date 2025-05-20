import {getAllMessages} from "@/app/services/message.service";
import {Message} from "@/app/interfaces/message";
import Link from "next/link";

export default async function MessagesPage() {
	const messages = await getAllMessages();
	console.log(messages);
	if (!messages || messages.hasOwnProperty('error')) {
		return (
			<main>
				Failed to retrieve messages
			</main>
		)
	}
	return (
		<main>
			<h1>Recent messages</h1>
			<ul>
				{(messages as Message[]).map((msg) => {
					return (
						<li key={msg.uuid}>
							<Link href={`/dashboard/messages/${msg.uuid}`}>Message from {msg.sent_date}</Link>
						</li>
					)
				})}
			</ul>
		</main>
	)
}