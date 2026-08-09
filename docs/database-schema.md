# Database Schema

PostgreSQL (Neon) schema for the Lab Monitoring System, aligned with the planning and requirements documents.

## Design Principles

- **Live state vs history**: `computers` and detail tables are upserted on agent check-in; history is append-only only when meaningful.
- **Upsert keys**: child tables use composite unique constraints on `(computer_id, natural_key)` so agent reports replace stale rows instead of duplicating them.
- **Retention-ready**: `metrics_history` is indexed by `(computer_id, recorded_at)` for coarse-interval writes and future retention jobs.

## Tables

| Table | Purpose | Growth |
|---|---|---|
| `computers` | Current PC snapshot (hostname, IP, OS, health %, status) | 1 row per PC, upserted |
| `ram_slots` | RAM slot inventory | Upsert per `(computer_id, slot_number)` |
| `storage_devices` | HDD/SSD/NVMe inventory + SMART health | Upsert per `(computer_id, device_identifier)` |
| `peripherals` | Connected peripherals and baseline inventory | Upsert per `(computer_id, device_key)` |
| `peripheral_events` | USB connect/disconnect audit trail | Append on event |
| `software_licenses` | Windows/Office/VS Code license state | Upsert per `(computer_id, product_name)` |
| `installed_software` | Installed application inventory | Upsert per `(computer_id, name, publisher)` |
| `metrics_history` | CPU/RAM/disk/temperature time series | Append, coarse interval |
| `hardware_change_log` | Old → new audit trail for hardware changes | Append on change |
| `alerts` | Performance/security/license/hardware alerts | Append on trigger |
| `maintenance_assets` | Excel-derived PC inventory | Seeded/edited occasionally |
| `maintenance_tasks` | Preventive maintenance task catalog | Seeded/edited occasionally |
| `maintenance_log` | Completed checklist entries | Append on completion |
| `users` | Dashboard accounts and roles | Small/static |
| `audit_log` | Immutable admin action log | Append |

## Key Relationships

- `computers.id` is the parent key for all live monitoring tables.
- `maintenance_assets.asset_id` cross-references `computers.asset_id` once a PC is enrolled.
- `alerts.acknowledged_by_id`, `maintenance_log.completed_by_id`, and `audit_log.user_id` reference `users.id`.

## Migrations

```bash
cd backend
alembic upgrade head
```

Current revision chain:

1. `193fd880cb36` — initial `computers` table
2. `b7c4e2a91d03` — full lab monitoring schema
