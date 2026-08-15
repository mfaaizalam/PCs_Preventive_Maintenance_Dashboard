// Period-label conventions for the maintenance checklist.
//
// The backend (`MaintenanceLogToggle.period_label`) treats this as an
// opaque string — it never parses it — so the *frontend* owns the
// convention. It documents its own examples in
// backend/app/api/maintenance.py:
//   '2026-08-W2'  (biweekly)   '2026-08'  (monthly)   '2026-H1'  (half-yearly)
// We extend that same pattern to the two frequencies the API defines
// but the docstring doesn't show an example for (weekly, quarterly),
// and fall back to a monthly bucket for "custom" tasks.

function pad2(n) {
  return String(n).padStart(2, "0");
}

function isoWeekNumber(date) {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil(((d - yearStart) / 86400000 + 1) / 7);
}

export function periodLabelFor(frequency, date = new Date()) {
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const dayOfMonth = date.getDate();

  switch (frequency) {
    case "weekly":
      return `${year}-W${pad2(isoWeekNumber(date))}`;
    case "biweekly":
      return `${year}-${pad2(month)}-W${dayOfMonth <= 15 ? 1 : 2}`;
    case "monthly":
    case "custom":
      return `${year}-${pad2(month)}`;
    case "quarterly":
      return `${year}-Q${Math.ceil(month / 3)}`;
    case "half_yearly":
      return `${year}-H${month <= 6 ? 1 : 2}`;
    default:
      return `${year}-${pad2(month)}`;
  }
}

// Human-friendly rendering of a period label for a given frequency,
// e.g. "Aug 2026 · Week 2", "Q3 2026", "2026 H1".
export function formatPeriodLabel(frequency, label) {
  const MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
  ];
  if (!label) return "—";

  if (frequency === "biweekly") {
    const [year, month, week] = label.split("-");
    const idx = Number(month) - 1;
    return `${MONTHS[idx] ?? month} ${year} · Week ${week?.replace("W", "")}`;
  }
  if (frequency === "monthly" || frequency === "custom") {
    const [year, month] = label.split("-");
    const idx = Number(month) - 1;
    return `${MONTHS[idx] ?? month} ${year}`;
  }
  if (frequency === "quarterly") {
    const [year, q] = label.split("-");
    return `${q} ${year}`;
  }
  if (frequency === "half_yearly") {
    const [year, h] = label.split("-");
    return `${year} ${h}`;
  }
  if (frequency === "weekly") {
    const [year, week] = label.split("-");
    return `${year} Week ${week?.replace("W", "")}`;
  }
  return label;
}

// The end-of-period date, used to decide whether an incomplete task
// counts as "overdue" (period has fully elapsed) vs. still "pending"
// (period is ongoing).
export function periodEndDate(frequency, label) {
  if (!label) return null;
  try {
    if (frequency === "biweekly") {
      const [year, month, week] = label.split("-");
      const isSecondHalf = week === "W2" || week === "2";
      const lastDayOfMonth = new Date(Number(year), Number(month), 0).getDate();
      return new Date(Number(year), Number(month) - 1, isSecondHalf ? lastDayOfMonth : 15, 23, 59, 59);
    }
    if (frequency === "monthly" || frequency === "custom") {
      const [year, month] = label.split("-");
      const lastDay = new Date(Number(year), Number(month), 0).getDate();
      return new Date(Number(year), Number(month) - 1, lastDay, 23, 59, 59);
    }
    if (frequency === "quarterly") {
      const [year, q] = label.split("-");
      const qNum = Number(q.replace("Q", ""));
      const endMonth = qNum * 3;
      const lastDay = new Date(Number(year), endMonth, 0).getDate();
      return new Date(Number(year), endMonth - 1, lastDay, 23, 59, 59);
    }
    if (frequency === "half_yearly") {
      const [year, h] = label.split("-");
      const endMonth = h === "H1" ? 6 : 12;
      const lastDay = new Date(Number(year), endMonth, 0).getDate();
      return new Date(Number(year), endMonth - 1, lastDay, 23, 59, 59);
    }
    if (frequency === "weekly") {
      // Approximate: Sunday of the ISO week, good enough for overdue logic.
      const [year, week] = label.split("-");
      const w = Number(week.replace("W", ""));
      const simple = new Date(Number(year), 0, 1 + (w - 1) * 7);
      const dow = simple.getDay();
      const isoStart = new Date(simple);
      isoStart.setDate(simple.getDate() - (dow === 0 ? 6 : dow - 1));
      const end = new Date(isoStart);
      end.setDate(isoStart.getDate() + 6);
      end.setHours(23, 59, 59);
      return end;
    }
  } catch {
    return null;
  }
  return null;
}

export function isPeriodElapsed(frequency, label, now = new Date()) {
  const end = periodEndDate(frequency, label);
  if (!end) return false;
  return now.getTime() > end.getTime();
}

// Builds the last `count` period labels for a frequency, most recent
// first, so the UI can offer a period picker ("history") without the
// backend needing a dedicated history endpoint — we just re-query the
// existing checklist endpoint once per period.
export function recentPeriods(frequency, count = 6, referenceDate = new Date()) {
  const periods = [];
  const cursor = new Date(referenceDate);

  for (let i = 0; i < count; i++) {
    periods.push(periodLabelFor(frequency, cursor));
    switch (frequency) {
      case "weekly":
        cursor.setDate(cursor.getDate() - 7);
        break;
      case "biweekly":
        cursor.setDate(cursor.getDate() - 15);
        break;
      case "quarterly":
        cursor.setMonth(cursor.getMonth() - 3);
        break;
      case "half_yearly":
        cursor.setMonth(cursor.getMonth() - 6);
        break;
      case "monthly":
      case "custom":
      default:
        cursor.setMonth(cursor.getMonth() - 1);
        break;
    }
  }
  // De-dupe in case a step lands on the same label twice.
  return [...new Set(periods)];
}

export const FREQUENCY_OPTIONS = [
  { value: "weekly", label: "Weekly" },
  { value: "biweekly", label: "Biweekly" },
  { value: "monthly", label: "Monthly" },
  { value: "quarterly", label: "Quarterly" },
  { value: "half_yearly", label: "Half-Yearly" },
  { value: "custom", label: "Custom" },
];
