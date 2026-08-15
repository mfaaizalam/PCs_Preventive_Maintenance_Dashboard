import { Link } from "react-router-dom";
import { ClipboardList, Tag } from "lucide-react";
import StatusBadge from "../common/StatusBadge";
import { effectiveStatus } from "../../utils/status";

export default function MaintenanceComputerCard({ computer }) {
  const status = effectiveStatus(computer);

  return (
    <Link
      to={`/maintenance/${computer.id}`}
      className="group flex flex-col rounded-xl2 border border-ink-100 bg-white p-4 shadow-card transition hover:-translate-y-0.5 hover:shadow-cardHover"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="truncate font-display text-[15px] font-semibold text-ink-900">
            {computer.hostname}
          </p>
          <div className="mt-1 flex flex-wrap items-center gap-x-2.5 gap-y-1 text-[12px] text-ink-400">
            {computer.asset_id && (
              <span className="inline-flex items-center gap-1 font-mono">
                <Tag className="h-3 w-3" /> {computer.asset_id}
              </span>
            )}
            {computer.lab_section && <span>{computer.lab_section}</span>}
          </div>
        </div>
        <StatusBadge status={status} size="sm" />
      </div>

      <div className="mt-4 flex items-center justify-between rounded-lg bg-ink-50/70 px-3 py-2.5 text-sm font-medium text-brand-700">
        <span className="inline-flex items-center gap-1.5">
          <ClipboardList className="h-4 w-4" />
          Open checklist
        </span>
        <span className="text-ink-300 transition group-hover:translate-x-0.5 group-hover:text-brand-500">
          →
        </span>
      </div>
    </Link>
  );
}
