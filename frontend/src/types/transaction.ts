export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";
export type Decision = "APPROVE" | "REVIEW" | "BLOCK";
export type FeedbackLabel = "confirmed_fraud" | "false_positive" | "legitimate";

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
  feedback_label: FeedbackLabel | null;
  feedback_notes: string | null;
  feedback_created_at: string | null;
  feedback_updated_at: string | null;
  created_at: string;
}

export interface FeedbackUpdate {
  feedback_label: FeedbackLabel;
  feedback_notes?: string | null;
}
