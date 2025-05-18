export interface LoginData {
	username: string,
	password: string,
}

export interface UserInfo {
	uuid: string,
	display_name: string,
	token: string,
	expiry_time: string,
	permissions_level: number
}