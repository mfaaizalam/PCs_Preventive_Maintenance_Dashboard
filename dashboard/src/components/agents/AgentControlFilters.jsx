import { Search } from "lucide-react";

export default function AgentControlFilters({
  query,
  onQueryChange,
  labSection,
  onLabSectionChange,
  labSectionOptions,
}) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="relative min-w-[220px] max-w-xs flex-1">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-300" />
        <input
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          placeholder="Search hostname, IP, lab…"
          className="w-full rounded-lg border border-ink-200 bg-white py-2 pl-9 pr-3 text-sm text-ink-800 placeholder:text-ink-300 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
        />
      </div>

      <select
        value={labSection}
        onChange={(e) => onLabSectionChange(e.target.value)}
        className="w-full min-w-0 rounded-lg border border-ink-200 bg-white px-3 py-2 text-sm text-ink-700 sm:w-auto focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
      >
        <option value="all">All labs</option>
        {labSectionOptions.map((l) => (
          <option key={l} value={l}>
            {l}
          </option>
        ))}
      </select>
    </div>
  );
}