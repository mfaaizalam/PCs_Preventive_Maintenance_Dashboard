import { PlugZap } from "lucide-react";

/**
 * The agent collects this data and the backend already models it
 * (see backend/app/models/computer.py relationships), but no GET
 * endpoint returns it yet — only POST /api/agent/report (ingest) and
 * the flat computer record are wired up. This renders instead of a
 * fake/mocked panel so the UI never claims to show live data it isn't
 * actually getting from the API.
 */
export default function NotExposedNotice({ title, endpointHint }) {
  return (
    <div className="flex items-start gap-3 rounded-xl2 border border-dashed border-ink-200 bg-ink-50/60 p-5">
      <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white text-ink-400 shadow-panel">
        <PlugZap className="h-4 w-4" strokeWidth={1.8} />
      </div>
      <div>
        <p className="text-sm font-medium text-ink-700">{title} isn't exposed by the API yet</p>
        <p className="mt-1 text-sm leading-relaxed text-ink-400">
          The agent already collects this and it's stored in the database, but there's no read
          endpoint for it today.
          {endpointHint && (
            <>
              {" "}
              Ask the backend team to add{" "}
              <code className="rounded bg-white px-1.5 py-0.5 font-mono text-[12px] text-ink-600 shadow-panel">
                {endpointHint}
              </code>
              .
            </>
          )}
        </p>
      </div>
    </div>
  );
}
