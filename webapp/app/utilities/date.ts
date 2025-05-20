export function formatDate(d: Date | null | number) {
	if (!d) {
		return '';
	}
	if (typeof d === "number") {
		d = new Date(d);
	}
	return `${d.getFullYear()}-${d.getMonth() <= 9 ? `0${d.getMonth()}` : d.getMonth()}-${d.getDay() <= 9 ? `0${d.getDay()}` : d.getDay()} ${d.getHours() <= 9 ? `0${d.getHours()}` : d.getHours()}:${d.getMinutes() <= 9 ? `0${d.getMinutes()}` : d.getMinutes()}`;
}