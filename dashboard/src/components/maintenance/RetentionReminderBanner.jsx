import { useEffect, useState } from "react";
import { AlertTriangle, Download } from "lucide-react";
import { fetchMaintenanceRetentionStatus, downloadChecklistExport } from "../../api/maintenanceApi";
import { periodLabelFor } from "../../utils/period";

const FREQUENCIES = ["biweekly", "monthly", "half_yearly"];

export default function RetentionReminderBanner() {
  const [status, setStatus] = useState(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    fetchMaintenanceRetentionStatus(controller.signal)
      .then(setStatus)
      .catch(() => {});
    return () => controller.abort();
  }, []);

  if (!status || !status.show_reminder || status.affected_record_count === 0) return null;

  async function handleExportAll() {
    setExporting(true);
    try {
      for (const frequency of FREQUENCIES) {
        const period = periodLabelFor(frequency);
        await downloadChecklistExport({ frequency, period });
      }
    } finally {
      setExporting(false);
    }
  }

  const dayWord = status.days_remaining === 1 ? "din" : "din";

  return (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-lg border-l-4 border-l-signal-attention bg-amber-50 px-4 py-3">
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
        <div>
          <p className="text-sm font-semibold text-amber-900">
            {status.days_remaining <= 0
              ? "Maintenance data purge ho rahi hai aaj"
              : `${status.days_remaining} ${dayWord} mein purana maintenance data delete ho jayega`}
          </p>
          <p className="mt-0.5 text-sm text-amber-800">
            {status.affected_record_count} records ({status.period_label}) affected. Zaroorat ho to abhi export kar lein.
          </p>
        </div>
      </div>
      <button
        onClick={handleExportAll}
        disabled={exporting}
        className="flex items-center gap-1.5 rounded-md bg-amber-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-amber-700 disabled:opacity-50"
      >
        <Download className="h-4 w-4" />
        {exporting ? "Exporting…" : "Export / Print records"}
      </button>
    </div>
  );
}