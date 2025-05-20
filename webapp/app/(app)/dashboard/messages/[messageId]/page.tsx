import {getMessage} from "@/app/services/message.service";
import Link from "next/link";
type MessagePageParams = Promise<{messageId: string}>

export default async function MessagePage({ params }: { params: MessagePageParams }) {
	const uuid = (await params).messageId;
	const messageData = await getMessage(uuid);
	if (!messageData || messageData.hasOwnProperty('error')) {
		return (
			<main>
				<p>Message was not found</p>
				<Link href={"/dashboard/message"}>Go back to list of message</Link>
			</main>
		)
	}
	console.log(messageData);
	return (
		<main>

		</main>
	)
}