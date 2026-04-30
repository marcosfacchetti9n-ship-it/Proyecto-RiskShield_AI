import { Link } from "react-router-dom";
import { DecisionBadge } from "./DecisionBadge";
import { FeedbackBadge } from "./FeedbackBadge";
import { RiskBadge } from "./RiskBadge";
import type { RecentTransaction } from "../types/dashboard";
import type { Transaction } from "../types/transaction";

interface TransactionTableProps {
  transactions: Array<Transaction | RecentTransaction>;
  compact?: boolean;
}

function formatScore(score: number | null | undefined): string {
  if (score === null || score === undefined) {
    return "-";
  }

  return score.toFixed(3);
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function TransactionTable({ transactions, compact = false }: TransactionTableProps) {
  if (transactions.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
        No transactions found.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Transaction</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">User</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Amount</th>
              {!compact ? (
                <th className="px-4 py-3 text-left font-semibold text-slate-600">Country</th>
              ) : null}
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Category</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Risk</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Decision</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Feedback</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Score</th>
              {!compact ? (
                <th className="px-4 py-3 text-left font-semibold text-slate-600">Created</th>
              ) : null}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {transactions.map((transaction) => (
              <tr key={transaction.id} className="hover:bg-slate-50">
                <td className="whitespace-nowrap px-4 py-3 font-medium text-slate-900">
                  <Link
                    className="text-slate-950 underline-offset-4 hover:underline"
                    to={`/transactions/${transaction.id}`}
                  >
                    {transaction.transaction_id}
                  </Link>
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-slate-600">
                  {transaction.user_id}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-slate-600">
                  {transaction.currency} {Number(transaction.amount).toLocaleString()}
                </td>
                {!compact ? (
                  <td className="whitespace-nowrap px-4 py-3 text-slate-600">
                    {transaction.country}
                  </td>
                ) : null}
                <td className="whitespace-nowrap px-4 py-3 text-slate-600">
                  {transaction.merchant_category}
                </td>
                <td className="whitespace-nowrap px-4 py-3">
                  <RiskBadge level={transaction.risk_level} />
                </td>
                <td className="whitespace-nowrap px-4 py-3">
                  <DecisionBadge decision={transaction.decision} />
                </td>
                <td className="whitespace-nowrap px-4 py-3">
                  <FeedbackBadge label={transaction.feedback_label} />
                </td>
                <td className="whitespace-nowrap px-4 py-3 font-medium text-slate-700">
                  {formatScore(transaction.final_score)}
                </td>
                {!compact ? (
                  <td className="whitespace-nowrap px-4 py-3 text-slate-500">
                    {formatDate(transaction.created_at)}
                  </td>
                ) : null}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
