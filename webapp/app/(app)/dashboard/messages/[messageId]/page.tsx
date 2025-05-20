import {getMessage} from "@/app/services/message.service";
import Link from "next/link";
import {Message} from "@/app/interfaces/message";
type MessagePageParams = Promise<{messageId: string}>

export default async function MessagePage({ params }: { params: MessagePageParams }) {
	const uuid = (await params).messageId;
	const messageData = await getMessage(uuid);
	if (!messageData || messageData.hasOwnProperty('error')) {
		return (
			<main>
				<p>Message was not found</p>
				<Link href={"/dashboard/messages"}>Go back to list of message</Link>
			</main>
		)
	}

	const msg: Message = messageData as Message;
	return (
		<main>
			<p>
				Received on {msg.sent_date}
			</p>
			{msg.items?.map((item, idx) => {
				return (
					<section key={idx}>
						<h3>{item.name}</h3>
						<pre>{item.value}</pre>
					</section>
				)
			})}
		</main>
	)
}