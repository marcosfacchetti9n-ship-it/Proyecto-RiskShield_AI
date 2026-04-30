import { apiClient } from "./client";
import type {
  FeedbackUpdate,
  Transaction,
  TransactionInput,
} from "../types/transaction";

export async function listTransactions(limit = 50, offset = 0): Promise<Transaction[]> {
  const response = await apiClient.get<Transaction[]>("/transactions", {
    params: { limit, offset },
  });
  return response.data;
}

export async function analyzeTransaction(
  payload: TransactionInput,
): Promise<Transaction> {
  const response = await apiClient.post<Transaction>(
    "/transactions/analyze",
    payload,
  );
  return response.data;
}

export async function updateTransactionFeedback(
  transactionId: string,
  payload: FeedbackUpdate,
): Promise<Transaction> {
  const response = await apiClient.patch<Transaction>(
    `/transactions/${transactionId}/feedback`,
    payload,
  );
  return response.data;
}
