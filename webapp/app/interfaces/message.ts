export interface Message {
	uuid: string,
	sent_date: string,
	status: string,
	items?: {
		name: string,
		value: string,
	}[]
}

export interface Messages {
	messages: Message[]
}