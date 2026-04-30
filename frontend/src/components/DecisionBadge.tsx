import type { Decision } from "../types/transaction";

interface DecisionBadgeProps {
  decision: Decision | null;
}

const decisionClasses: Record<Decision, string> = {
  APPROVE: "border-sky-200 bg-sky-50 text-sky-700",
  REVIEW: "border-violet-200 bg-violet-50 text-violet-700",
  BLOCK: "border-red-200 bg-red-50 text-red-700",
};

export function DecisionBadge({ decision }: DecisionBadgeProps) {
  if (!decision) {
    return <span className="text-sm text-slate-400">Pending</span>;
  }

  return (
    <span
      className={`inline-flex min-w-20 items-center justify-center rounded-md border px-2 py-1 text-xs font-semibold ${decisionClasses[decision]}`}
    >
      {decision}
    </span>
  );
}
