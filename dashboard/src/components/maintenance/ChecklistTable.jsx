import { Check, Loader2, User, AlertCircle } from "lucide-react";
import { isPeriodElapsed } from "../../utils/period";
import { formatDateTime } from "../../utils/format";

function rowState(item, frequency, period) {
  if (item.completed) return "completed";
  if (isPeriodElapsed(frequency, period)) return "overdue";
  return "pending";
}

const STATE_META = {
  completed: { label: "Completed", chip: "bg-signal-healthyBg text-signal-healthy" },
  overdue: { label: "Overdue", chip: "bg-signal-criticalBg text-signal-critical" },
  pending: { label: "Pending", chip: "bg-signal-attentionBg text-signal-attention" },
};

export default function ChecklistTable({ checklist, frequency, period, savingTaskId, onToggle }) {
  return (
    <div className="overflow-hidden rounded-xl2 border border-ink-100 bg-white">
      <table className="w-full text-left text-sm">
        <thead className="bg-ink-50 text-[11px] uppercase tracking-wide text-ink-400">
          <tr>
            <th className="w-12 px-4 py-3"></th>
            <th className="px-3 py-3">Task</th>
            <th className="px-3 py-3">Responsible</th>
            <th className="px-3 py-3">Status</th>
            <th className="px-3 py-3">Completed</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-ink-100">
          {checklist.map((item) => {
            const state = rowState(item, frequency, period);
            const meta = STATE_META[state];
            const saving = savingTaskId === item.task_id;

            return (
              <tr key={item.task_id} className={state === "overdue" ? "bg-signal-criticalBg/30" : ""}>
                <td className="px-4 py-3">
                  <button
                    onClick={() => onToggle(item)}
                    disabled={saving}
                    aria-pressed={item.completed}
                    aria-label={`Mark "${item.task_name}" as ${item.completed ? "not done" : "done"}`}
                    className={`flex h-5 w-5 items-center justify-center rounded-[6px] border-2 transition ${
                      item.completed
                        ? "border-signal-healthy bg-signal-healthy text-white"
                        : "border-ink-300 bg-white hover:border-brand-400"
                    } ${saving ? "opacity-60" : ""}`}
                  >
                    {saving ? (
                      <Loader2 className="h-3 w-3 animate-spin" />
                    ) : (
                      item.completed && <Check className="h-3.5 w-3.5" strokeWidth={3} />
                    )}
                  </button>
                </td>
                <td className="px-3 py-3">
                  <p className="font-medium text-ink-800">{item.task_name}</p>
                  {item.notes && (
                    <p className="mt-0.5 flex items-center gap-1 text-[12px] text-ink-400">
                      <AlertCircle className="h-3 w-3" /> {item.notes}
                    </p>
                  )}
                </td>
                <td className="px-3 py-3 text-ink-500">
                  {item.responsible_person ? (
                    <span className="inline-flex items-center gap-1">
                      <User className="h-3.5 w-3.5 text-ink-300" /> {item.responsible_person}
                    </span>
                  ) : (
                    "—"
                  )}
                </td>
                <td className="px-3 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-[12px] font-medium ${meta.chip}`}>
                    {meta.label}
                  </span>
                </td>
                <td className="px-3 py-3 text-[12px] text-ink-400">
                  {item.completed ? (
                    <>
                      {formatDateTime(item.completed_at)}
                      {item.completed_by && <span className="block">by {item.completed_by}</span>}
                    </>
                  ) : (
                    "—"
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
