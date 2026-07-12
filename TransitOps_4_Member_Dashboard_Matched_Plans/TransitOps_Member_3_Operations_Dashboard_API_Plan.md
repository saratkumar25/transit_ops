# Member 3 — Operations, Finance, Dashboard API, and Release Integration

> **Branch:** `member3-ops-integration`  
> **Workload:** High  
> **Release owner:** imports, manifest, installation, merge coordination  
> **No overlap:** never edit Member 1 models or Member 2 security/views/static files.

---

## 1. Mission

Implement:

- Maintenance model and workflow
- Fuel Log model
- Expense model
- Dashboard backend service with the exact frozen response
- Maintenance/Fuel/Expense views and action XML IDs
- Module imports and manifest
- Clean install, upgrade, and release merge

---

## 2. Exclusive File Ownership

```text
transit_ops/__init__.py
transit_ops/__manifest__.py
transit_ops/models/__init__.py
transit_ops/models/maintenance.py
transit_ops/models/fuel_log.py
transit_ops/models/expense.py
transit_ops/models/dashboard.py
transit_ops/views/maintenance_views.xml
transit_ops/views/fuel_log_views.xml
transit_ops/views/expense_views.xml
transit_ops/data/mail_template.xml          # P2 only
transit_ops/data/license_cron.xml           # P2 only
transit_ops/report/*                        # P2 only
```

Never edit:

```text
transit_ops/models/vehicle.py
transit_ops/models/driver.py
transit_ops/models/trip.py
transit_ops/security/*
transit_ops/views/vehicle_views.xml
transit_ops/views/driver_views.xml
transit_ops/views/trip_views.xml
transit_ops/views/dashboard_action.xml
transit_ops/views/menu_views.xml
transit_ops/static/*
transit_ops/data/sequence.xml
transit_ops/data/demo_data.xml
README.md
docs/*
```

You may merge another member's commit, but you may not rewrite their file.

---

## 3. Frozen References

Models:

```text
transit.maintenance
transit.fuel.log
transit.expense
transit.dashboard
```

Actions you define:

```text
action_transit_maintenance
action_transit_fuel_log
action_transit_expense
```

Methods:

```text
transit.maintenance.action_start
transit.maintenance.action_close
transit.maintenance.action_cancel
transit.dashboard.get_dashboard_data
```

---

## 4. `maintenance.py`

### Fields

```text
name: Char, required
vehicle_id: Many2one(transit.vehicle), required, ondelete restrict
maintenance_type: Selection(service, repair, inspection, other), required
start_date: Date, required, default today
end_date: Date
cost: Monetary, required, default 0
notes: Text
state: Selection(draft, open, closed, cancelled), default draft, indexed
currency_id: Many2one(res.currency), required
```

### Constraints

- cost >= 0
- end date >= start date
- only one open maintenance record per vehicle

### `action_start`

1. state must be draft
2. vehicle must not be on_trip or retired
3. no other open maintenance for the vehicle
4. state -> open
5. vehicle status -> in_shop

### `action_close`

1. state must be open
2. set end date when missing
3. state -> closed
4. vehicle -> available unless retired

### `action_cancel`

- draft -> cancelled, no vehicle change
- open -> cancelled and restore available unless retired
- closed -> block in MVP

---

## 5. `fuel_log.py`

Fields:

```text
vehicle_id: Many2one(transit.vehicle), required
trip_id: Many2one(transit.trip)
date: Date, required, default today
liters: Float, required
cost: Monetary, required
odometer: Float
currency_id: Many2one(res.currency), required
```

Constraints:

- liters > 0
- cost >= 0
- odometer >= 0 when set
- prevent duplicate fuel log for the same trip when `trip_id` is set

Member 1 creates this record during completion. Keep the exact field names.

---

## 6. `expense.py`

Fields:

```text
name: Char, required
vehicle_id: Many2one(transit.vehicle), required
trip_id: Many2one(transit.trip)
expense_type: Selection(toll, parking, permit, other), required
date: Date, required, default today
amount: Monetary, required
currency_id: Many2one(res.currency), required
```

Constraints:

- amount >= 0
- trim name

---

## 7. `dashboard.py`

Use a small regular model with an `@api.model` service method. No dashboard records need to be created.

```python
_name = "transit.dashboard"
_description = "TransitOps Dashboard Service"
```

### Exact method

```python
@api.model
def get_dashboard_data(self, filters=None):
    ...
```

### Exact response

```python
{
    "schema_version": 1,
    "kpis": {
        "active_vehicles": 0,
        "available_vehicles": 0,
        "vehicles_in_maintenance": 0,
        "active_trips": 0,
        "pending_trips": 0,
        "drivers_on_duty": 0,
        "fleet_utilization": 0.0,
    },
    "vehicle_status": [
        {"key": "available", "label": "Available", "count": 0, "percentage": 0.0},
        {"key": "on_trip", "label": "On Trip", "count": 0, "percentage": 0.0},
        {"key": "in_shop", "label": "In Shop", "count": 0, "percentage": 0.0},
        {"key": "retired", "label": "Retired", "count": 0, "percentage": 0.0},
    ],
    "recent_trips": [],
    "filter_options": {
        "vehicle_types": [],
        "statuses": [],
        "regions": [],
    },
    "applied_filters": {
        "vehicle_type": False,
        "status": False,
        "region": False,
    },
    "current_user": {
        "name": "",
        "initials": "",
        "role": "",
    },
}
```

### Filter validation

Accept only:

```text
vehicle_type: van, truck, bus, other
status: available, on_trip, in_shop, retired
region: exact known region string
```

Ignore or reject unsupported values safely. Never interpolate raw input into SQL.

### Domains

Create a filtered vehicle domain from type/status/region. Use its IDs for trip filtering where appropriate.

Recommended behavior:

- vehicle KPIs and status distribution use the filtered vehicle set
- trip KPIs and recent trips use assigned vehicles from that set
- when no type/status filter is selected, draft trips without a vehicle may still appear
- region filters both vehicle region and trip region

### KPI formulas

```text
active_vehicles = status != retired
available_vehicles = status == available
vehicles_in_maintenance = status == in_shop
active_trips = state == dispatched
pending_trips = state == draft
drivers_on_duty = status == on_trip
fleet_utilization = on_trip vehicles / non-retired vehicles * 100
```

Round utilization and percentages to one decimal place.

### Vehicle status list

Always return all four entries and preserve this order:

```text
Available, On Trip, In Shop, Retired
```

Calculate percentage from the filtered total vehicle count. Return zero for empty totals.

### Recent trips

Return latest 6 ordered by:

```text
dispatch_date desc, completion_date desc, create_date desc, id desc
```

Each row:

```python
{
    "id": trip.id,
    "name": trip.name,
    "vehicle": trip.vehicle_id.name or "—",
    "driver": trip.driver_id.name or "—",
    "state": trip.state,
    "status_label": label,
    "eta": eta_string,
}
```

Status label mapping:

```text
dispatched -> On Trip
completed -> Completed
draft -> Draft
cancelled -> Cancelled
```

ETA:

```text
dispatched -> ceil(planned_distance / 40 * 60), formatted as "45 min" or "1h 10m"
completed/cancelled -> "—"
draft -> "Awaiting vehicle"
```

### Filter options

- Vehicle types: exact selection labels from `transit.vehicle`.
- Statuses: exact vehicle-status labels.
- Regions: unique non-empty vehicle/trip regions, alphabetically sorted.

### Current user

Return:

- `name`: current user's display name
- `initials`: first letters of first two words, uppercase
- `role`: one role label

Role precedence when multiple groups exist:

```text
Dispatcher
Fleet Manager
Safety Officer
Financial Analyst
User
```

The demo user should normally belong to one role only.

### Security and performance

- Method is for authenticated users in one TransitOps group.
- Use ORM `search_count`, `search`, or `read_group`; do not use unsafe SQL.
- Keep to a small number of queries.
- Do not `sudo()` the whole method. Respect the logged-in user's access where possible.
- Return plain JSON-safe values.

---

## 8. Operational Views

### Maintenance action XML ID

```text
action_transit_maintenance
```

Views:

- list: vehicle, type, start/end, cost, state
- form: header buttons/start-close-cancel and statusbar
- search: open/closed, type, vehicle; group by state/type/vehicle

### Fuel action XML ID

```text
action_transit_fuel_log
```

Views:

- list: date, vehicle, trip, liters, cost, odometer
- form
- search/group by vehicle/date
- graph/pivot if stable

### Expense action XML ID

```text
action_transit_expense
```

Views:

- list: date, name, vehicle, trip, type, amount
- form
- search/group by type/vehicle/date
- graph/pivot if stable

Send these exact action IDs to Member 2 by 01:30. Do not edit `menu_views.xml`.

---

## 9. Imports and Manifest

### `models/__init__.py`

Import all model files from both owners:

```text
vehicle
driver
trip
maintenance
fuel_log
expense
dashboard
```

Member 1 never edits this file.

### Manifest order

Recommended data order:

1. `security/security.xml`
2. `security/ir.model.access.csv`
3. `data/sequence.xml`
4. Member 1 core views
5. Member 3 operational views
6. dashboard action
7. menu views
8. optional data/report files
9. demo data only when appropriate

Assets must include only the three exact dashboard files supplied by Member 2. Confirm the installed Odoo version's backend asset bundle name.

---

## 10. Integration Duties Without Ownership Violation

- Create scaffold and branches.
- Merge commits in agreed order.
- On conflict, keep the designated owner's file.
- Run install/upgrade and route failures by owner.
- Do not make “quick fixes” in another member's file.
- Provide exact commands and logs to Member 4.
- Tag/release only after clean install and regression.

---

## 11. Hour Plan

### 00:00–00:15

Create scaffold, imports/manifest skeleton, and freeze contracts.

### 00:15–01:30

Implement operations models, action IDs, service skeleton, and first views.

### 01:30–02:45

Implement workflows, constraints, exact dashboard payload, and first installation.

### 02:45–04:00

Merge M1/M2, fix only owned integration files, finalize views and API.

### 04:00–05:15

Validate filters, KPI formulas, role payload, recent trips, percentages, and asset order.

### 05:15–06:15

Clean install/upgrade, fix operations/API/manifest failures, freeze.

### 06:15–08:00

Release stabilization, tag, backup, and demo support.

---

## 12. Acceptance Tests

- Maintenance start/close/cancel transitions work.
- Open-maintenance uniqueness works.
- Fuel and expense constraints work.
- Member 1 trip completion can create a fuel log.
- Dashboard method returns every frozen key and all four status entries.
- Filters return correct counts.
- Recent trips use real records and exact labels.
- Current user/role/avatar data are correct.
- Asset bundle loads the three Member 2 files.
- Clean install and upgrade pass.
- No other owner's file is modified.

---

## 13. Claude / Antigravity Prompt

```text
You are Member 3 implementing only operations, finance, dashboard backend, imports,
manifest, and release-owned views for an Odoo addon named transit_ops.
Generate or edit only:
- transit_ops/__init__.py
- transit_ops/__manifest__.py
- transit_ops/models/__init__.py
- transit_ops/models/maintenance.py
- transit_ops/models/fuel_log.py
- transit_ops/models/expense.py
- transit_ops/models/dashboard.py
- transit_ops/views/maintenance_views.xml
- transit_ops/views/fuel_log_views.xml
- transit_ops/views/expense_views.xml
Optional P2 only: transit_ops/data/mail_template.xml, transit_ops/data/license_cron.xml,
transit_ops/report/*
Do not output or modify Member 1 models, security, core views, dashboard JS/XML/SCSS,
menu_views.xml, sequence, demo data, README, or docs. Use the exact dashboard response
schema and action IDs. Output each owned file separately with its exact path.
```
