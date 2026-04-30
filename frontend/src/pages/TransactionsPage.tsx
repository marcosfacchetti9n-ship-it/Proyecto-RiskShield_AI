import { FormEvent, useEffect, useMemo, useState } from "react";
import { RefreshCw, ShieldCheck } from "lucide-react";
import { analyzeTransaction, listTransactions } from "../api/transactions";
import { DecisionBadge } from "../components/DecisionBadge";
import { RiskBadge } from "../components/RiskBadge";
import { TransactionTable } from "../components/TransactionTable";
import type { Transaction, TransactionInput } from "../types/transaction";

const initialForm: TransactionInput = {
  user_id: "USR-001",
  amount: 250000,
  currency: "ARS",
  country: "Argentina",
  device: "mobile",
  hour: 3,
  merchant_category: "electronics",
};

export function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [analysisResult, setAnalysisResult] = useState<Transaction | null>(null);
  const [form, setForm] = useState<TransactionInput>(initialForm);
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function loadTransactions() {
    setIsLoading(true);
    setError("");

    try {
      setTransactions(await listTransactions(100, 0));
    } catch {
      setError("Transactions could not be loaded.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadTransactions();
  }, []);

  const filteredTransactions = useMemo(() => {
    return transactions.filter((transaction) => {
      const matchesRisk =
        riskFilter === "ALL" || transaction.risk_level === riskFilter;
      const normalizedQuery = query.trim().toLowerCase();
      const matchesQuery =
        normalizedQuery.length === 0 ||
        transaction.transaction_id.toLowerCase().includes(normalizedQuery) ||
        transaction.user_id.toLowerCase().includes(normalizedQuery) ||
        transaction.country.toLowerCase().includes(normalizedQuery) ||
        transaction.merchant_category.toLowerCase().includes(normalizedQuery);

      return matchesRisk && matchesQuery;
    });
  }, [transactions, riskFilter, query]);

  function updateField<K extends keyof TransactionInput>(
    key: K,
    value: TransactionInput[K],
  ) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function handleAnalyze(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError("");

    try {
      const result = await analyzeTransaction(form);
      setAnalysisResult(result);
      await loadTransactions();
    } catch {
      setError("Transaction analysis failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <h1 className="text-2xl font-semibold text-slate-950">Transactions</h1>
        </div>
        <button
          type="button"
          onClick={loadTransactions}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {error ? (
        <p className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {error}
        </p>
      ) : null}

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_380px]">
        <div className="space-y-4">
          <div className="grid gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-[1fr_180px]">
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search transaction, user, country or category"
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-950 focus:ring-2 focus:ring-slate-200"
            />
            <select
              value={riskFilter}
              onChange={(event) => setRiskFilter(event.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-950 focus:ring-2 focus:ring-slate-200"
            >
              <option value="ALL">All risk levels</option>
              <option value="LOW">LOW</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="HIGH">HIGH</option>
            </select>
          </div>

          {isLoading ? (
            <p className="text-sm text-slate-500">Loading transactions...</p>
          ) : (
            <TransactionTable transactions={filteredTransactions} />
          )}
        </div>

        <aside className="space-y-4">
          <form
            onSubmit={handleAnalyze}
            className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
          >
            <h2 className="text-base font-semibold text-slate-950">Analyze Transaction</h2>
            <div className="mt-4 space-y-3">
              <TextField label="User ID" value={form.user_id} onChange={(value) => updateField("user_id", value)} />
              <NumberField label="Amount" value={form.amount} onChange={(value) => updateField("amount", value)} />
              <TextField label="Currency" value={form.currency} onChange={(value) => updateField("currency", value.toUpperCase())} />
              <TextField label="Country" value={form.country} onChange={(value) => updateField("country", value)} />
              <TextField label="Device" value={form.device} onChange={(value) => updateField("device", value)} />
              <NumberField label="Hour" value={form.hour} onChange={(value) => updateField("hour", value)} min={0} max={23} />
              <TextField
                label="Merchant Category"
                value={form.merchant_category}
                onChange={(value) => updateField("merchant_category", value)}
              />
            </div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              <ShieldCheck size={18} />
              {isSubmitting ? "Analyzing" : "Analyze"}
            </button>
          </form>

          {analysisResult ? (
            <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <h2 className="text-base font-semibold text-slate-950">Analysis Result</h2>
              <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-slate-500">Final Score</p>
                  <p className="mt-1 font-semibold text-slate-950">
                    {analysisResult.final_score?.toFixed(3) ?? "-"}
                  </p>
                </div>
                <div>
                  <p className="text-slate-500">Model</p>
                  <p className="mt-1 font-semibold text-slate-950">
                    {analysisResult.model_available ? "Available" : "Rules only"}
                  </p>
                </div>
                <div>
                  <p className="mb-1 text-slate-500">Risk</p>
                  <RiskBadge level={analysisResult.risk_level} />
                </div>
                <div>
                  <p className="mb-1 text-slate-500">Decision</p>
                  <DecisionBadge decision={analysisResult.decision} />
                </div>
              </div>
              <div className="mt-4">
                <p className="text-sm font-medium text-slate-700">Main Factors</p>
                <ul className="mt-2 space-y-2 text-sm text-slate-600">
                  {analysisResult.main_factors.length > 0 ? (
                    analysisResult.main_factors.map((factor) => (
                      <li key={factor} className="rounded-md bg-slate-50 px-3 py-2">
                        {factor}
                      </li>
                    ))
                  ) : (
                    <li className="rounded-md bg-slate-50 px-3 py-2">No risk factors triggered.</li>
                  )}
                </ul>
              </div>
            </div>
          ) : null}
        </aside>
      </section>
    </div>
  );
}

function TextField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block text-sm font-medium text-slate-700">
      {label}
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        required
        className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-950 focus:ring-2 focus:ring-slate-200"
      />
    </label>
  );
}

function NumberField({
  label,
  value,
  onChange,
  min,
  max,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
}) {
  return (
    <label className="block text-sm font-medium text-slate-700">
      {label}
      <input
        type="number"
        value={value}
        min={min}
        max={max}
        onChange={(event) => onChange(Number(event.target.value))}
        required
        className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-950 focus:ring-2 focus:ring-slate-200"
      />
    </label>
  );
}
