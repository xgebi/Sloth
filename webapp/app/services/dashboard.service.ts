import 'server-only'
import {fetchDashboardData} from "@/app/repository/dashboard.repository";

export function getDashboardInformation() {
	console.log('abc');
	return fetchDashboardData();
}