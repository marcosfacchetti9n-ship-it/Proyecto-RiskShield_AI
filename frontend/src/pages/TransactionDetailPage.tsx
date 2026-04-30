import { FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Save } from "lucide-react";
import { listTransactions, updateTransactionFeedback } from "../api/transactions";
import { DecisionBadge } from "../components/DecisionBadge";
import { FeedbackBadge, getFeedbackLabel } from "../components/FeedbackBadge";
import { RiskBadge } from "../components/RiskBadge";
import type { FeedbackLabel, Transaction } from "../types/transaction";

function formatScore(score: number | null): string {
  return score === null ? "-" : score.toFixed(3);
}

export function TransactionDetailPage() {
  const { id } = useParams();
  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [feedbackLabel, setFeedbackLabel] = useState<FeedbackLabel>("confirmed_fraud");
  const [feedbackNotes, setFeedbackNotes] = useState("");
  const [feedbackMessage, setFeedbackMessage] = useState("");
  const [feedbackError, setFeedbackError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSavingFeedback, setIsSavingFeedback] = useState(false);

  useEffect(() => {
    async function loadTransaction() {
      const transactions = await listTransactions(100, 0);
      const match = transactions.find((item) => String(item.id) === id) ?? null;
      setTransaction(match);
      setFeedbackLabel(match?.feedback_label ?? "confirmed_fraud");
      setFeedbackNotes(match?.feedback_notes ?? "");
      setIsLoading(false);
    }

    loadTransaction();
  }, [id]);

  async function handleFeedbackSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!transaction) {
      return;
    }

    setIsSavingFeedback(true);
    setFeedbackMessage("");
    setFeedbackError("");

    try {
      const updatedTransaction = await updateTransactionFeedback(
        transaction.transaction_id,
        {
          feedback_label: feedbackLabel,
          feedback_notes: feedbackNotes.trim() || null,
        },
      );
      setTransaction(updatedTransaction);
      setFeedbackLabel(updatedTransaction.feedback_label ?? "confirmed_fraud");
      setFeedbackNotes(updatedTransaction.feedback_notes ?? "");
      setFeedbackMessage("Feedback saved.");
    } catch {
      setFeedbackError("Feedback could not be saved.");
    } finally {
      setIsSavingFeedback(false);
    }
  }

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

      <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="text-base font-semibold text-slate-950">Manual Review</h2>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <FeedbackBadge label={transaction.feedback_label} />
            <span className="text-sm text-slate-500">
              {transaction.feedback_updated_at
                ? new Intl.DateTimeFormat("en", {
                    dateStyle: "medium",
                    timeStyle: "short",
                  }).format(new Date(transaction.feedback_updated_at))
                : "Pending review"}
            </span>
          </div>
          {transaction.feedback_notes ? (
            <p className="mt-4 rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-700">
              {transaction.feedback_notes}
            </p>
          ) : null}
        </div>

        <form
          onSubmit={handleFeedbackSubmit}
          className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
        >
          <label className="block text-sm font-medium text-slate-700">
            Feedback
            <select
              value={feedbackLabel}
              onChange={(event) => setFeedbackLabel(event.target.value as FeedbackLabel)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-950 focus:ring-2 focus:ring-slate-200"
            >
              <option value="confirmed_fraud">{getFeedbackLabel("confirmed_fraud")}</option>
              <option value="false_positive">{getFeedbackLabel("false_positive")}</option>
              <option value="legitimate">{getFeedbackLabel("legitimate")}</option>
            </select>
          </label>
          <label className="mt-3 block text-sm font-medium text-slate-700">
            Notes
            <textarea
              value={feedbackNotes}
              onChange={(event) => setFeedbackNotes(event.target.value)}
              rows={4}
              maxLength={500}
              className="mt-1 w-full resize-none rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-950 focus:ring-2 focus:ring-slate-200"
            />
          </label>
          {feedbackMessage ? (
            <p className="mt-3 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
              {feedbackMessage}
            </p>
          ) : null}
          {feedbackError ? (
            <p className="mt-3 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
              {feedbackError}
            </p>
          ) : null}
          <button
            type="submit"
            disabled={isSavingFeedback}
            className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            <Save size={18} />
            {isSavingFeedback ? "Saving" : "Save Feedback"}
          </button>
        </form>
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
