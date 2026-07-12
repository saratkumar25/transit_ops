# Member 2 — Security, Core Views, and Exact Dashboard Frontend

> **Branch:** `member2-ui-dashboard`  
> **Workload:** High  
> **Primary responsibility:** make the dashboard look like the supplied Excalidraw wireframe.  
> **No overlap:** do not edit Python models, manifest, Member 3 operational views, demo data, or docs.

---

## 1. Mission

Own all access control and the user-facing core UI:

- Four security groups and ACL rows
- Vehicle, Driver, and Trip views
- Root menus and actions
- Exact TransitOps dashboard structure, behavior, and styling
- Role-aware sidebar navigation
- Loading, empty, error, filter, and local-search behavior

---

## 2. Exclusive File Ownership

```text
transit_ops/security/security.xml
transit_ops/security/ir.model.access.csv
transit_ops/views/vehicle_views.xml
transit_ops/views/driver_views.xml
transit_ops/views/trip_views.xml
transit_ops/views/dashboard_action.xml
transit_ops/views/menu_views.xml
transit_ops/static/src/components/dashboard/dashboard.js
transit_ops/static/src/components/dashboard/dashboard.xml
transit_ops/static/src/components/dashboard/dashboard.scss
```

Never edit:

```text
transit_ops/__init__.py
transit_ops/__manifest__.py
transit_ops/models/*
transit_ops/views/maintenance_views.xml
transit_ops/views/fuel_log_views.xml
transit_ops/views/expense_views.xml
transit_ops/data/*
transit_ops/report/*
README.md
docs/*
```

When an asset is ready, send its path to Member 3. Do not insert it into the manifest yourself.

---

## 3. Frozen References

### Models

```text
transit.vehicle
transit.driver
transit.trip
transit.maintenance
transit.fuel.log
transit.expense
transit.dashboard
```

### Groups

```text
module_category_transit_ops
group_transit_fleet_manager
group_transit_dispatcher
group_transit_safety_officer
group_transit_financial_analyst
```

### Actions

You define:

```text
action_transit_dashboard
action_transit_vehicle
action_transit_driver
action_transit_trip
action_transit_analytics
```

Member 3 defines; you only reference:

```text
action_transit_maintenance
action_transit_fuel_log
action_transit_expense
```

### Dashboard action tag

```text
transit_ops.dashboard
```

### Dashboard ORM call

```text
Model: transit.dashboard
Method: get_dashboard_data
Argument: [filters]
```

---

## 4. RBAC

Create one module category and these four groups:

- TransitOps / Fleet Manager
- TransitOps / Dispatcher
- TransitOps / Safety Officer
- TransitOps / Financial Analyst

ACL intent:

| Model | Fleet Manager | Dispatcher | Safety Officer | Financial Analyst |
|---|---:|---:|---:|---:|
| Vehicle | CRUD | Read | Read | Read |
| Driver | Read | Read | Read/Write | Read |
| Trip | Read | CRUD | Read | Read |
| Maintenance | CRUD | Read | Read | Read |
| Fuel Log | CRUD | Create/Read | Read | CRUD |
| Expense | Read | Create/Read | Read | CRUD |
| Dashboard | Read | Read | Read | Read |

Trip workflow buttons are Dispatcher-only. Maintenance buttons are handled in Member 3's view.

---

## 5. Core Views

### Vehicle views

List:

```text
registration_number, name, vehicle_type, region, max_load_capacity,
odometer, status, operational_cost, roi
```

Search:

- registration/name
- Available, On Trip, In Shop, Retired
- group by type, status, region

Form:

- header status
- identification and capacity
- odometer and acquisition cost
- computed costs, revenue, ROI
- notebook tabs for trips, maintenance, fuel, expenses

### Driver views

List:

```text
name, license_number, license_category, license_expiry_date,
license_state, contact_number, safety_score, status
```

Search:

- name/licence
- Available, On Trip, Off Duty, Suspended, Expired, Expiring
- group by status/category

### Trip views

List:

```text
name, source, destination, vehicle_id, driver_id,
cargo_weight, planned_distance, state
```

Form header:

```text
action_dispatch: Draft, Dispatcher only
action_complete: Dispatched, Dispatcher only
action_cancel: Draft/Dispatched, Dispatcher only
state statusbar
```

Domains for UX:

```xml
vehicle_id -> status = available
driver_id -> status = available
```

Member 1 enforces the rules in Python.

---

## 6. Menu Structure

The native Odoo app menu and the dashboard's internal sidebar must use the same order:

```text
TransitOps
├── Dashboard
├── Fleet
├── Drivers
├── Trips
├── Maintenance
├── Fuel & Expenses
├── Analytics
└── Settings
```

Mapping:

```text
Dashboard -> action_transit_dashboard
Fleet -> action_transit_vehicle
Drivers -> action_transit_driver
Trips -> action_transit_trip
Maintenance -> action_transit_maintenance
Fuel & Expenses -> action_transit_fuel_log
Analytics -> action_transit_analytics
Settings -> visible in custom sidebar; disabled unless system admin
```

Do not define Member 3's action records a second time.

---

## 7. Exact Dashboard Data Shape

Expect this exact response; do not rename keys:

```javascript
{
  schema_version: 1,
  kpis: {
    active_vehicles: 0,
    available_vehicles: 0,
    vehicles_in_maintenance: 0,
    active_trips: 0,
    pending_trips: 0,
    drivers_on_duty: 0,
    fleet_utilization: 0.0,
  },
  vehicle_status: [
    { key: "available", label: "Available", count: 0, percentage: 0.0 },
    { key: "on_trip", label: "On Trip", count: 0, percentage: 0.0 },
    { key: "in_shop", label: "In Shop", count: 0, percentage: 0.0 },
    { key: "retired", label: "Retired", count: 0, percentage: 0.0 },
  ],
  recent_trips: [
    { id: 1, name: "TR001", vehicle: "VAN-05", driver: "Alex",
      state: "dispatched", status_label: "On Trip", eta: "45 min" },
  ],
  filter_options: {
    vehicle_types: [{ value: "van", label: "Van" }],
    statuses: [{ value: "available", label: "Available" }],
    regions: [{ value: "Hyderabad", label: "Hyderabad" }],
  },
  applied_filters: { vehicle_type: false, status: false, region: false },
  current_user: { name: "Raven K.", initials: "RK", role: "Dispatcher" },
}
```

---

## 8. `dashboard.js`

Use the installed Odoo version's supported Owl imports. Inspect an existing client action before finalizing imports.

### Required structure

- Register action tag `transit_ops.dashboard`.
- Use `useService("orm")` for data.
- Use `useService("action")` for sidebar navigation.
- Keep one reactive state containing:
  - `loading`
  - `error`
  - `data`
  - `filters`
  - `searchTerm`
  - `sidebarOpen`
- Load data in `onWillStart`.
- `reloadDashboard()` calls:

```javascript
orm.call("transit.dashboard", "get_dashboard_data", [state.filters])
```

- Filter changes call the backend.
- Search does not call the backend; it filters `recent_trips` by trip, vehicle, or driver.
- Prevent stale requests from overwriting the newest filter response.
- Show a Retry button when an error occurs.
- Never hard-code KPI numbers.

### Navigation map

```javascript
Dashboard: reload current client action
Fleet: transit_ops.action_transit_vehicle
Drivers: transit_ops.action_transit_driver
Trips: transit_ops.action_transit_trip
Maintenance: transit_ops.action_transit_maintenance
Fuel & Expenses: transit_ops.action_transit_fuel_log
Analytics: transit_ops.action_transit_analytics
Settings: disabled for ordinary roles; optional native settings action for system admin
```

### Status classes

```text
dispatched / on_trip -> blue
completed -> green
draft -> grey
cancelled -> red/grey
```

---

## 9. `dashboard.xml` — Exact Layout

Use one root class:

```html
<div class="o_transit_dashboard">
```

Required hierarchy:

```text
.o_transit_dashboard
├── aside.to_sidebar
│   ├── .to_brand           -> TransitOps
│   └── nav.to_nav          -> 8 items in exact order
└── section.to_workspace
    ├── header.to_topbar
    │   ├── .to_search      -> Search...
    │   └── .to_user_area   -> name, role pill, circular initials
    └── main.to_content
        ├── .to_filters_title -> FILTERS
        ├── .to_filters       -> 3 compact selects
        ├── .to_kpi_grid      -> exactly 7 cards
        └── .to_main_grid
            ├── section.to_recent_trips
            │   └── table -> TRIP, VEHICLE, DRIVER, STATUS, ETA
            └── section.to_vehicle_status
                └── 4 horizontal bars
```

### Sidebar text order

```text
Dashboard
Fleet
Drivers
Trips
Maintenance
Fuel & Expenses
Analytics
Settings
```

### KPI label order

```text
ACTIVE VEHICLES
AVAILABLE VEHICLES
VEHICLES IN MAINTENANCE
ACTIVE TRIPS
PENDING TRIPS
DRIVERS ON DUTY
FLEET UTILIZATION
```

### Empty states

- Recent trips: `No trips match the current filters.`
- Vehicle status: render zero-width fills and zero counts.
- KPI values: show `0`, not blank.

---

## 10. `dashboard.scss` — Wireframe-Matched Styling

### Required tokens

```scss
--to-white: #ffffff;
--to-sidebar: #f1f3f5;
--to-text: #1e1e1e;
--to-text-secondary: #495057;
--to-muted: #868e96;
--to-border: #adb5bd;
--to-divider: #dee2e6;
--to-soft-divider: #f1f3f5;
--to-blue: #4d84bf;
--to-blue-strong: #1971c2;
--to-blue-soft: #e7f0fa;
--to-green: #2f9e44;
--to-green-alt: #66a80f;
--to-orange: #f08c00;
--to-orange-soft: #ffe8cc;
--to-red: #e03131;
```

### Desktop dimensions

```text
root min-height: calc(100vh - Odoo top chrome)
sidebar width: 190 px
topbar height: 56 px
content padding: 20 px
search: about 260 x 28 px
KPI card height: 80 px
KPI grid: 7 equal columns at >= 1200 px
KPI accent: 4 px left strip
main grid: roughly 2fr 1fr
```

### Visual rules

- white page
- flat light-grey sidebar
- 1 px borders
- no heavy shadows
- squared KPI cards
- muted uppercase labels
- 22 px KPI values
- active Dashboard nav: orange-soft background and orange accent
- compact solid status pills
- grey status tracks with solid fills

### Responsive

```scss
@media (max-width: 1199px) { KPI 4 + 3; compact sidebar or drawer; panels may stack; }
@media (max-width: 767px)  { drawer sidebar; KPI 2 columns; table horizontal scroll; }
@media (max-width: 479px)  { KPI 1 column if required; compact user area; }
```

Do not add Chart.js, Bootstrap card shadows, gradients, or unrelated icons.

---

## 11. Dashboard Action XML

Define one `ir.actions.client` with:

```text
name: TransitOps Dashboard
tag: transit_ops.dashboard
XML ID: action_transit_dashboard
```

Define `action_transit_analytics` as a stable native graph/pivot/list action using an existing model and measures. It is an emergency fallback, not the primary dashboard.

---

## 12. Hour Plan

### 00:00–00:15

Read the exact visual contract, inspect installed Odoo client-action syntax, freeze names.

### 00:15–01:30

Build groups, ACLs, core actions/views, root menu, and dashboard shell.

### 01:30–02:45

Build exact HTML structure and first SCSS pass: 190 px sidebar, 56 px topbar, filters, seven cards, table, bars.

### 02:45–04:00

Connect API, loading/error/empty states, local search, filters, and action navigation.

### 04:00–05:15

Pixel-match desktop colours/spacing and run role visibility checks.

### 05:15–06:15

Fix QA issues, responsive breakpoints, and asset errors. Freeze features.

### 06:15–08:00

Blocker fixes and demo support only.

---

## 13. Acceptance Checklist

- Four groups and ACL matrix work.
- Core menus/actions/views open without unknown fields.
- Dashboard mounts from `action_transit_dashboard`.
- Sidebar is 190 px on desktop and has eight labels in exact order.
- Dashboard active nav is orange.
- Topbar has Search, dynamic user, role pill, and initials avatar.
- Three filters exist in exact order.
- Seven KPI cards exist in one desktop row.
- Recent Trips has exact five columns.
- Vehicle Status has four bars in exact order and colours.
- All values come from backend.
- Search filters recent trips.
- Filters reload all data.
- 1360 x 900 closely matches the supplied wireframe.
- 1024 and 390 widths remain usable.
- No third-party chart library.
- No unowned file changed.

---

## 14. Claude / Antigravity Prompt

```text
You are Member 2 implementing only security, core XML views, menus, and the exact
wireframe-matched Owl dashboard for an Odoo addon named transit_ops.
Generate or edit only:
- transit_ops/security/security.xml
- transit_ops/security/ir.model.access.csv
- transit_ops/views/vehicle_views.xml
- transit_ops/views/driver_views.xml
- transit_ops/views/trip_views.xml
- transit_ops/views/dashboard_action.xml
- transit_ops/views/menu_views.xml
- transit_ops/static/src/components/dashboard/dashboard.js
- transit_ops/static/src/components/dashboard/dashboard.xml
- transit_ops/static/src/components/dashboard/dashboard.scss
Do not output or modify Python models, manifest, Member 3 views, data files, reports,
README, or docs. Use all names and the dashboard payload exactly. Reproduce the supplied
layout: 190 px light-grey sidebar, 56 px topbar, Search/user/role/avatar, three filters,
seven flat KPI cards, Recent Trips table, and Vehicle Status bars. Do not redesign,
hard-code KPI values, or add third-party chart libraries. Output each owned file separately.
```
