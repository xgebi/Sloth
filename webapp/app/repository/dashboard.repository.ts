import {simpleGet} from "@/app/repository/fetch";

export async function fetchDashboardData() {
	return simpleGet("/api/dashboard-information");
}