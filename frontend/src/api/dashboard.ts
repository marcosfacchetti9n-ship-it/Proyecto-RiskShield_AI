import { apiClient } from "./client";
import type {
  CategoryRiskSummary,
  CountryRiskSummary,
  DashboardMetrics,
  RecentTransaction,
} from "../types/dashboard";

export async function getMetrics(): Promise<DashboardMetrics> {
  const response = await apiClient.get<DashboardMetrics>("/dashboard/metrics");
  return response.data;
}

export async function getRecentTransactions(limit = 10): Promise<RecentTransaction[]> {
  const response = await apiClient.get<RecentTransaction[]>(
    "/dashboard/recent-transactions",
    { params: { limit } },
  );
  return response.data;
}

export async function getCountryRisk(): Promise<CountryRiskSummary[]> {
  const response = await apiClient.get<CountryRiskSummary[]>(
    "/dashboard/country-risk",
  );
  return response.data;
}

export async function getCategoryRisk(): Promise<CategoryRiskSummary[]> {
  const response = await apiClient.get<CategoryRiskSummary[]>(
    "/dashboard/category-risk",
  );
  return response.data;
}
