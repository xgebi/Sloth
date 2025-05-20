import 'server-only'
import {fetchMessage, fetchMessages} from "@/app/repository/message.repository";

export function getAllMessages() {
	return fetchMessages();
}

export function getMessage(messageId: string) {
	return fetchMessage(messageId);
}