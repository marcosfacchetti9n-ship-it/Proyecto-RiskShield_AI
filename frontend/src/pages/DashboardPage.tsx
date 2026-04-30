import { useEffect, useMemo, useState } from "react";
import { Ban, BrainCircuit, ClipboardCheck, Gauge, ShieldAlert } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  getCategoryRisk,
  getCountryRisk,
  getMetrics,
  getRecentTransactions,
} from "../api/dashboard";
import { MetricCard } from "../components/MetricCard";
import { getFeedbackLabel } from "../components/FeedbackBadge";
import { TransactionTable } from "../components/TransactionTable";
import type {
  CategoryRiskSummary,
  CountryRiskSummary,
  DashboardMetrics,
  RecentTransaction,
} from "../types/dashboard";

const riskColors: Record<string, string> = {
  LOW: "#059669",
  MEDIUM: "#d97706",
  HIGH: "#e11d48",
};

const decisionColors: Record<string, string> = {
  APPROVE: "#0284c7",
  REVIEW: "#7c3aed",
  BLOCK: "#dc2626",
};

function percent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<RecentTransaction[]>([]);
  const [countryRisk, setCountryRisk] = useState<CountryRiskSummary[]>([]);
  const [categoryRisk, setCategoryRisk] = useState<CategoryRiskSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [metricsData, recentData, countryData, categoryData] = await Promise.all([
          getMetrics(),
          getRecentTransactions(10),
          getCountryRisk(),
          getCategoryRisk(),
        ]);

        setMetrics(metricsData);
        setRecentTransactions(recentData);
        setCountryRisk(countryData);
        setCategoryRisk(categoryData);
      } catch {
        setError("Dashboard data could not be loaded.");
      } finally {
        setIsLoading(false);
      }
    }

    loadDashboard();
  }, []);

  const riskDistribution = useMemo(
    () =>
      Object.entries(metrics?.risk_level_counts ?? {}).map(([name, value]) => ({
        name,
        value,
      })),
    [metrics],
  );

  const decisionDistribution = useMemo(
    () =>
      Object.entries(metrics?.decision_counts ?? {}).map(([name, value]) => ({
        name,
        value,
      })),
    [metrics],
  );

  if (isLoading) {
    return <p className="text-sm text-slate-500">Loading dashboard...</p>;
  }

  if (error) {
    return <p className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</p>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-950">Dashboard</h1>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Transactions"
          value={metrics?.total_transactions ?? 0}
          helper="Total processed records"
          icon={<Gauge size={20} />}
        />
        <MetricCard
          title="Blocked Rate"
          value={percent(metrics?.blocked_rate ?? 0)}
          helper="BLOCK decisions over total"
          icon={<Ban size={20} />}
        />
        <MetricCard
          title="Average Score"
          value={(metrics?.average_final_score ?? 0).toFixed(3)}
          helper="Mean final risk score"
          icon={<ShieldAlert size={20} />}
        />
        <MetricCard
          title="ML Coverage"
          value={percent(metrics?.model_available_rate ?? 0)}
          helper="Analyses with model available"
          icon={<BrainCircuit size={20} />}
        />
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center gap-2">
          <ClipboardCheck size={18} className="text-slate-600" />
          <h2 className="text-base font-semibold text-slate-950">Feedback Review</h2>
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {Object.entries(metrics?.feedback_counts ?? {}).map(([label, count]) => (
            <div key={label} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2">
              <p className="text-xs font-medium uppercase text-slate-500">
                {getFeedbackLabel(label === "unreviewed" ? null : label)}
              </p>
              <p className="mt-1 text-xl font-semibold text-slate-950">{count}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="text-base font-semibold text-slate-950">Risk Distribution</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={riskDistribution} dataKey="value" nameKey="name" innerRadius={62} outerRadius={96}>
                  {riskDistribution.map((entry) => (
                    <Cell key={entry.name} fill={riskColors[entry.name] ?? "#64748b"} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="text-base font-semibold text-slate-950">Decision Distribution</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={decisionDistribution}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {decisionDistribution.map((entry) => (
                    <Cell key={entry.name} fill={decisionColors[entry.name] ?? "#64748b"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section>
        <div className="mb-3 flex items-center justify-between gap-4">
          <h2 className="text-base font-semibold text-slate-950">Recent Transactions</h2>
        </div>
        <TransactionTable transactions={recentTransactions} compact />
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <RiskSummaryTable
          title="Country Risk"
          rows={countryRisk.map((row) => ({
            label: row.country,
            total: row.total_transactions,
            high: row.high_risk_transactions,
            blocked: row.blocked_transactions,
            average: row.average_score,
          }))}
        />
        <RiskSummaryTable
          title="Category Risk"
          rows={categoryRisk.map((row) => ({
            label: row.merchant_category,
            total: row.total_transactions,
            high: row.high_risk_transactions,
            blocked: row.blocked_transactions,
            average: row.average_score,
          }))}
        />
      </section>
    </div>
  );
}

interface RiskSummaryRow {
  label: string;
  total: number;
  high: number;
  blocked: number;
  average: number;
}

function RiskSummaryTable({ title, rows }: { title: string; rows: RiskSummaryRow[] }) {
  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-4 py-3">
        <h2 className="text-base font-semibold text-slate-950">{title}</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Group</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Total</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">High</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Blocked</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-600">Avg Score</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rows.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                  No data available.
                </td>
              </tr>
            ) : (
              rows.map((row) => (
                <tr key={row.label}>
                  <td className="whitespace-nowrap px-4 py-3 font-medium text-slate-900">{row.label}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-slate-600">{row.total}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-slate-600">{row.high}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-slate-600">{row.blocked}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-slate-600">{row.average.toFixed(3)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
