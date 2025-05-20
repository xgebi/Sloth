export interface Message {
	uuid: string,
	sent_date: string,
	status: string,
}

export interface Messages {
	messages: Message[]
}