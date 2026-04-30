import type { FeedbackLabel } from "../types/transaction";

const feedbackStyles: Record<FeedbackLabel | "unreviewed", string> = {
  confirmed_fraud: "bg-rose-50 text-rose-700 ring-rose-200",
  false_positive: "bg-amber-50 text-amber-700 ring-amber-200",
  legitimate: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  unreviewed: "bg-slate-100 text-slate-600 ring-slate-200",
};

const feedbackLabels: Record<FeedbackLabel | "unreviewed", string> = {
  confirmed_fraud: "Confirmed Fraud",
  false_positive: "False Positive",
  legitimate: "Legitimate",
  unreviewed: "Unreviewed",
};

export function getFeedbackLabel(label: string | null | undefined): string {
  if (
    label === "confirmed_fraud" ||
    label === "false_positive" ||
    label === "legitimate" ||
    label === "unreviewed"
  ) {
    return feedbackLabels[label];
  }

  return feedbackLabels.unreviewed;
}

export function FeedbackBadge({
  label,
}: {
  label: FeedbackLabel | null | undefined;
}) {
  const value = label ?? "unreviewed";

  return (
    <span
      className={`inline-flex whitespace-nowrap rounded-full px-2 py-1 text-xs font-semibold ring-1 ring-inset ${feedbackStyles[value]}`}
    >
      {feedbackLabels[value]}
    </span>
  );
}
