# Lab Monitor — PC Preventive Maintenance Dashboard (Frontend)

React 18 + Vite + Tailwind CSS frontend for the existing FastAPI backend in
`backend/`. This app makes **live API calls only** — there is no mock or
placeholder data anywhere in the shipped code.

## Setup

```bash
npm install
cp .env.example .env   # adjust VITE_API_BASE_URL if your backend isn't on :8000
npm run dev
```

Open http://localhost:5173. The backend must be running separately
(`uvicorn app.main:app --reload` from `backend/`, with Postgres available).

## Connecting to the backend — read this first

**The backend has no `CORSMiddleware` configured.** A browser calling it
directly from a different origin (e.g. the Vite dev server on `:5173`
calling the API on `:8000`) will be blocked by CORS, regardless of what the
frontend code does — this is a browser security rule, not something client
code can work around.

This project avoids the problem without touching the backend, using two
routing conventions:

- **Dev**: `vite.config.js` proxies `/api/*` and `/health` to
  `VITE_API_BASE_URL` (default `http://localhost:8000`). The browser only
  ever talks to the Vite origin; Vite forwards the request server-side,
  which isn't subject to CORS. `src/api/client.js` calls relative paths
  (e.g. `/api/agent/dashboard`) so this works automatically.
- **Production**: serve this app's build output behind the same reverse
  proxy (nginx, etc.) that routes `/api` and `/health` to the backend, so
  everything is same-origin from the browser's point of view. This is the
  standard pattern and needs no backend changes either.

If you instead deploy the frontend on a genuinely different origin with no
proxy in front of it, the only fix is to add `CORSMiddleware` to
`backend/app/main.py` — no amount of frontend configuration can bypass
browser CORS enforcement in that topology.

## What's wired to real endpoints

| Screen | Backend endpoint(s) |
|---|---|
| Dashboard (cards, stats, alerts feed) | `GET /api/agent/dashboard` |
| Categories | `GET /api/agent/dashboard` (grouped client-side by `lab_section`) |
| PC Details — identity, live CPU/RAM/disk, OS/IP | `GET /api/agent/computers/{agent_id}` |
| PC Details — alerts | `GET /api/agent/dashboard`, filtered to this PC (see limitation below) |
| Maintenance — PC list | `GET /api/maintenance/computers` |
| Maintenance — checklist | `GET /api/maintenance/computers/{id}/checklist?period=&frequency=` |
| Maintenance — tick/untick | `POST /api/maintenance/log` |

## Known gaps (by design — see decision log below)

The `Computer` SQLAlchemy model already has relationships for RAM slots,
storage devices, peripherals, peripheral connect/disconnect events,
installed software, software licenses, hardware change history, metric
history, and per-PC alerts — the agent collects and stores all of this.
**No GET endpoint returns any of it today.** The PC Details page shows an
honest "not exposed by the API yet" panel for each of these sections
(`src/components/details/UnexposedSectionsGrid.jsx`) instead of faking the
data, along with the exact endpoint each one would need
(e.g. `GET /api/agent/computers/{agent_id}/peripheral-events`).

Two related, smaller effects of the same gap:
- **Categories** use `lab_section` (there's no dedicated category field in
  the schema).
- **Per-PC alerts** on the details page come from `GET /api/agent/dashboard`,
  which only returns the 10 most recent *unresolved* alerts system-wide —
  so older or resolved alerts for a given PC won't show up there until a
  real per-PC alerts endpoint exists. The UI says this explicitly rather
  than implying it's the complete history.
- **Maintenance "history"** is handled by letting you pick past periods
  from the period dropdown (re-querying the existing checklist endpoint
  per period) rather than a dedicated history endpoint, since the
  checklist API already returns `completed_by` / `completed_at` per item.

This was a deliberate choice, not an oversight: the alternative (adding
those GET endpoints) was offered and declined in favor of keeping the
backend untouched — see the app's in-UI notices for the exact endpoints
that would unblock each section.

## Verified

- `npm run build` — clean, 0 errors
- `npm run lint` (oxlint) — 0 warnings, 0 errors
- Vite dev proxy manually verified against a schema-accurate mock of
  `/health`, `/api/agent/dashboard`, `/api/agent/computers/{id}`,
  `/api/maintenance/computers`, `/api/maintenance/tasks`, and
  `/api/maintenance/computers/{id}/checklist`
- Every field the frontend reads was cross-checked against the actual
  Pydantic response schemas in `backend/app/schemas/` (not assumed from
  the prompt) — see `api/agentApi.js` and `api/maintenanceApi.js` for the
  endpoint-to-schema mapping.

No headless browser was available in the build sandbox to screenshot the
running app, so this wasn't visually verified beyond code-level checks —
worth a quick look once you run it locally.

## Project structure

```
src/
  api/            axios client + one file per backend router
  hooks/          data-fetching hooks (polling, per-page state)
  utils/          status/format/period logic, kept out of components
  components/
    layout/       Sidebar, Topbar, Layout
    common/       StatusBadge, MetricGauge, EmptyState, ErrorState,
                   NotExposedNotice, LoadingState
    pcs/          dashboard-grid pieces (card, filters, alerts panel)
    details/      PC Details page sections
    maintenance/  checklist page pieces
  pages/          one file per route
```
