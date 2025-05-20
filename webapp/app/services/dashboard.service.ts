import 'server-only'
import {fetchDashboardData} from "@/app/repository/dashboard.repository";

export function getDashboardInformation() {
	return fetchDashboardData();
}