import { useState } from "react";
import { X, PlusCircle } from "lucide-react";
import { createComputer } from "../../api/computersApi";

const FIELD_CLASS =
  "mt-1 w-full rounded-lg border border-ink-200 px-3 py-2 text-sm focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100";

export default function AddPCModal({ open, onClose, onCreated }) {
  const [form, setForm] = useState({
    hostname: "",
    assetId: "",
    labSection: "",
    labName: "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  if (!open) return null;

  function setField(key, value) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.hostname.trim()) {
      setError("Hostname / PC name is required.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const computer = await createComputer(form);
      setForm({ hostname: "", assetId: "", labSection: "", labName: "" });
      onCreated?.(computer);
      onClose();
    } catch (err) {
      setError(err.message ?? "Couldn't add that PC. Try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink-950/40 p-4">
      <div className="w-full max-w-md rounded-xl2 bg-white p-5 shadow-cardHover">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            <PlusCircle className="h-5 w-5 text-brand-600" />
            <p className="text-sm font-semibold text-ink-900">Add a PC</p>
          </div>
          <button onClick={onClose} className="text-ink-300 hover:text-ink-600">
            <X className="h-4 w-4" />
          </button>
        </div>
        <p className="mt-1 text-[12px] text-ink-400">
          For a PC that doesn't run the monitoring agent (or hasn't checked in yet). Live
          CPU/RAM/disk usage will show as unknown until it does.
        </p>

        <form onSubmit={handleSubmit} className="mt-4 space-y-3">
          <div>
            <label className="text-[12px] font-medium text-ink-500">Hostname / PC name *</label>
            <input
              autoFocus
              value={form.hostname}
              onChange={(e) => setField("hostname", e.target.value)}
              placeholder="e.g. CAED-LAB-14"
              className={FIELD_CLASS}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[12px] font-medium text-ink-500">Asset ID</label>
              <input
                value={form.assetId}
                onChange={(e) => setField("assetId", e.target.value)}
                placeholder="Optional"
                className={FIELD_CLASS}
              />
            </div>
            <div>
              <label className="text-[12px] font-medium text-ink-500">Lab section</label>
              <input
                value={form.labSection}
                onChange={(e) => setField("labSection", e.target.value)}
                placeholder="e.g. CAD/CAM"
                className={FIELD_CLASS}
              />
            </div>
          </div>

          <div>
            <label className="text-[12px] font-medium text-ink-500">Lab / room name</label>
            <input
              value={form.labName}
              onChange={(e) => setField("labName", e.target.value)}
              placeholder="Optional"
              className={FIELD_CLASS}
            />
          </div>

          {error && <p className="text-sm text-signal-critical">{error}</p>}

          <div className="mt-2 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg px-3 py-1.5 text-sm font-medium text-ink-500 hover:bg-ink-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-brand-700 px-3.5 py-1.5 text-sm font-medium text-white hover:bg-brand-800 disabled:opacity-60"
            >
              {saving ? "Adding…" : "Add PC"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}