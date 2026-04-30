import type { Transaction } from "./transaction";

export interface DashboardMetrics {
  total_transactions: number;
  risk_level_counts: Record<string, number>;
  decision_counts: Record<string, number>;
  blocked_rate: number;
  average_final_score: number;
  model_available_rate: number;
}

export type RecentTransaction = Pick<
  Transaction,
  | "id"
  | "transaction_id"
  | "user_id"
  | "amount"
  | "currency"
  | "country"
  | "merchant_category"
  | "risk_level"
  | "decision"
  | "final_score"
  | "created_at"
>;

export interface CountryRiskSummary {
  country: string;
  total_transactions: number;
  high_risk_transactions: number;
  blocked_transactions: number;
  average_score: number;
}

export interface CategoryRiskSummary {
  merchant_category: string;
  total_transactions: number;
  high_risk_transactions: number;
  blocked_transactions: number;
  average_score: number;
}
