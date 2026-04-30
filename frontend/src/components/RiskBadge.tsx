import type { RiskLevel } from "../types/transaction";

interface RiskBadgeProps {
  level: RiskLevel | null;
}

const riskClasses: Record<RiskLevel, string> = {
  LOW: "border-emerald-200 bg-emerald-50 text-emerald-700",
  MEDIUM: "border-amber-200 bg-amber-50 text-amber-700",
  HIGH: "border-rose-200 bg-rose-50 text-rose-700",
};

export function RiskBadge({ level }: RiskBadgeProps) {
  if (!level) {
    return <span className="text-sm text-slate-400">Pending</span>;
  }

  return (
    <span
      className={`inline-flex min-w-16 items-center justify-center rounded-md border px-2 py-1 text-xs font-semibold ${riskClasses[level]}`}
    >
      {level}
    </span>
  );
}
