export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";
export type Decision = "APPROVE" | "REVIEW" | "BLOCK";

export interface TransactionInput {
  user_id: string;
  amount: number;
  currency: string;
  country: string;
  device: string;
  hour: number;
  merchant_category: string;
}

export interface Transaction extends TransactionInput {
  id: number;
  transaction_id: string;
  rule_score: number | null;
  ml_score: number | null;
  final_score: number | null;
  risk_level: RiskLevel | null;
  decision: Decision | null;
  main_factors: string[];
  model_available: boolean;
  created_at: string;
}
