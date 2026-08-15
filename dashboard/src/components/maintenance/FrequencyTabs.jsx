import { FREQUENCY_OPTIONS } from "../../utils/period";

export default function FrequencyTabs({ value, onChange }) {
  return (
    <div className="flex flex-wrap gap-1 rounded-lg bg-ink-100 p-1">
      {FREQUENCY_OPTIONS.map((f) => (
        <button
          key={f.value}
          onClick={() => onChange(f.value)}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
            value === f.value
              ? "bg-white text-brand-800 shadow-panel"
              : "text-ink-500 hover:text-ink-800"
          }`}
        >
          {f.label}
        </button>
      ))}
    </div>
  );
}
