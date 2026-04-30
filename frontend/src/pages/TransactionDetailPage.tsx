import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { listTransactions } from "../api/transactions";
import { DecisionBadge } from "../components/DecisionBadge";
import { RiskBadge } from "../components/RiskBadge";
import type { Transaction } from "../types/transaction";

function formatScore(score: number | null): string {
  return score === null ? "-" : score.toFixed(3);
}

export function TransactionDetailPage() {
  const { id } = useParams();
  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadTransaction() {
      const transactions = await listTransactions(100, 0);
      const match = transactions.find((item) => String(item.id) === id) ?? null;
      setTransaction(match);
      setIsLoading(false);
    }

    loadTransaction();
  }, [id]);

  if (isLoading) {
    return <p className="text-sm text-slate-500">Loading transaction...</p>;
  }

  if (!transaction) {
    return (
      <div className="space-y-4">
        <Link
          to="/transactions"
          className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-950"
        >
          <ArrowLeft size={16} />
          Transactions
        </Link>
        <p className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-500">
          Transaction not found in the current list.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link
        to="/transactions"
        className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-950"
      >
        <ArrowLeft size={16} />
        Transactions
      </Link>

      <div>
        <h1 className="text-2xl font-semibold text-slate-950">
          {transaction.transaction_id}
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          {new Intl.DateTimeFormat("en", {
            dateStyle: "full",
            timeStyle: "short",
          }).format(new Date(transaction.created_at))}
        </p>
      </div>

      <section className="grid gap-4 lg:grid-cols-3">
        <DetailCard label="Rule Score" value={formatScore(transaction.rule_score)} />
        <DetailCard label="ML Score" value={formatScore(transaction.ml_score)} />
        <DetailCard label="Final Score" value={formatScore(transaction.final_score)} />
      </section>

      <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="text-base font-semibold text-slate-950">Transaction Data</h2>
          <dl className="mt-4 grid gap-4 sm:grid-cols-2">
            <InfoItem label="User" value={transaction.user_id} />
            <InfoItem label="Amount" value={`${transaction.currency} ${Number(transaction.amount).toLocaleString()}`} />
            <InfoItem label="Country" value={transaction.country} />
            <InfoItem label="Device" value={transaction.device} />
            <InfoItem label="Hour" value={String(transaction.hour)} />
            <InfoItem label="Category" value={transaction.merchant_category} />
          </dl>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="text-base font-semibold text-slate-950">Decision</h2>
          <div className="mt-4 flex flex-wrap gap-3">
            <RiskBadge level={transaction.risk_level} />
            <DecisionBadge decision={transaction.decision} />
          </div>
          <p className="mt-4 text-sm text-slate-600">
            Model: {transaction.model_available ? "Available" : "Rules only"}
          </p>
        </div>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <h2 className="text-base font-semibold text-slate-950">Main Factors</h2>
        <div className="mt-4 grid gap-2 md:grid-cols-2">
          {transaction.main_factors.length > 0 ? (
            transaction.main_factors.map((factor) => (
              <div key={factor} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700">
                {factor}
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-500">No risk factors stored.</p>
          )}
        </div>
      </section>
    </div>
  );
}

function DetailCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
    </div>
  );
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-sm font-medium text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm font-semibold text-slate-900">{value}</dd>
    </div>
  );
}
