# TransitOps — 4-Member, 8-Hour Odoo Hackathon Master Plan

> **Dashboard-matched edition** — built from the supplied TransitOps challenge PDF and the attached Excalidraw dashboard wireframe.  
> **Team size:** 4 members  
> **Duration:** 8 hours  
> **New outside member:** Member 4 has a deliberately lighter, isolated workload.  
> **Addon name:** `transit_ops`  
> **Non-negotiable rule:** one production file has one owner; no two members edit the same file.

---

## 1. Final Objective

Build an installable Odoo addon that digitizes the transport workflow from vehicle and driver registration through dispatch, maintenance, fuel, expenses, and operational reporting.

The final product must contain:

- Odoo authentication and four RBAC groups
- Vehicle and driver CRUD
- Trip creation, dispatch, completion, and cancellation
- Capacity, licence, availability, and duplicate-assignment validation
- Automatic vehicle and driver status transitions
- Maintenance start/close automation
- Fuel and expense tracking
- A custom Owl dashboard that visually follows the supplied wireframe
- Search, filters, list/form/kanban views, and native CSV export
- A stable demo dataset, test checklist, screenshots, README, and presentation script

The required demonstration flow is:

1. Open the dashboard and show live KPIs.
2. Register or open `Van-05`, capacity `500 kg`, status `Available`.
3. Open driver `Alex` with a valid licence and status `Available`.
4. Create a trip with cargo weight `450 kg`.
5. Dispatch it after the system validates `450 <= 500`, licence validity, resource status, and duplicate assignment.
6. Show both the vehicle and driver automatically becoming `On Trip`.
7. Complete the trip with final odometer, fuel litres, and fuel cost.
8. Show both resources returning to `Available` and the fuel log being created.
9. Start an Oil Change maintenance record and show the vehicle becoming `In Shop` and disappearing from dispatch choices.
10. Return to the dashboard and show refreshed KPIs, recent trips, and vehicle-status bars.

---

## 2. Scope and Priority

### P0 — mandatory before Hour 6:15

- Module installs and upgrades without traceback
- Four roles and ACLs
- Vehicle, Driver, Trip, Maintenance, Fuel Log, and Expense models
- Mandatory business rules in Python
- Vehicle, Driver, Trip, Maintenance, Fuel, and Expense views
- Custom dashboard matching the provided layout
- Dashboard backend API and live filters
- Demo workflow and test data

### P1 — after the end-to-end flow works

- Core kanban, graph, and pivot views
- Better status decorations
- Local search inside the dashboard recent-trip table
- Analytics action and native CSV export
- Responsive refinements

### P2 — only after feature freeze tests pass

- Licence-expiry reminder
- PDF report
- Attachments/document management
- Dark mode

### Out of scope for this 8-hour build

- GPS tracking
- Route optimisation
- Maps or third-party APIs
- Mobile application
- Complex accounting integration
- AI recommendations
- Multi-company custom rules

---

## 3. Role Split

| Member | Role | Workload | Main result |
|---|---|---:|---|
| **Member 1** | Core Backend and Trip Rules | High | Vehicle, Driver, Trip models, calculations, validations, and lifecycle actions |
| **Member 2** | Security, Core Views, and Exact Dashboard Frontend | High | RBAC, menus, core XML views, and the wireframe-matched Owl dashboard |
| **Member 3** | Maintenance, Finance, Dashboard API, and Release Integration | High | Maintenance/Fuel/Expense backend and views, dashboard data API, manifest, installation, merges |
| **Member 4 — new member** | QA, Demo Data, Documentation, and Presentation | Light | Demo records, visual QA, regression checklist, README, screenshots, pitch, submission pack |

Member 4 does not edit Python, security, views, static assets, or the manifest. This keeps the new member useful without putting the release at risk.

---

## 4. Strict File Ownership — Zero Overlap

| Path | Owner |
|---|---|
| `transit_ops/__init__.py` | Member 3 |
| `transit_ops/__manifest__.py` | Member 3 |
| `transit_ops/models/__init__.py` | Member 3 |
| `transit_ops/models/vehicle.py` | Member 1 |
| `transit_ops/models/driver.py` | Member 1 |
| `transit_ops/models/trip.py` | Member 1 |
| `transit_ops/models/maintenance.py` | Member 3 |
| `transit_ops/models/fuel_log.py` | Member 3 |
| `transit_ops/models/expense.py` | Member 3 |
| `transit_ops/models/dashboard.py` | Member 3 |
| `transit_ops/security/security.xml` | Member 2 |
| `transit_ops/security/ir.model.access.csv` | Member 2 |
| `transit_ops/views/vehicle_views.xml` | Member 2 |
| `transit_ops/views/driver_views.xml` | Member 2 |
| `transit_ops/views/trip_views.xml` | Member 2 |
| `transit_ops/views/dashboard_action.xml` | Member 2 |
| `transit_ops/views/menu_views.xml` | Member 2 |
| `transit_ops/static/src/components/dashboard/dashboard.js` | Member 2 |
| `transit_ops/static/src/components/dashboard/dashboard.xml` | Member 2 |
| `transit_ops/static/src/components/dashboard/dashboard.scss` | Member 2 |
| `transit_ops/views/maintenance_views.xml` | Member 3 |
| `transit_ops/views/fuel_log_views.xml` | Member 3 |
| `transit_ops/views/expense_views.xml` | Member 3 |
| `transit_ops/data/sequence.xml` | Member 1 |
| `transit_ops/data/demo_data.xml` | Member 4 |
| `transit_ops/data/mail_template.xml` | Member 3, P2 only |
| `transit_ops/data/license_cron.xml` | Member 3, P2 only |
| `transit_ops/report/*` | Member 3, P2 only |
| `README.md` | Member 4 |
| `docs/TEST_CHECKLIST.md` | Member 4 |
| `docs/DASHBOARD_VISUAL_QA.md` | Member 4 |
| `docs/DEMO_SCRIPT.md` | Member 4 |
| `docs/SUBMISSION_CHECKLIST.md` | Member 4 |
| `docs/screenshots/*` | Member 4 |

### Enforcement rules

1. Claude or Antigravity receives only the member-specific plan.
2. An AI agent must output only owned paths.
3. Reading another member's file is allowed; editing it is not.
4. A bug is reported to the owner with reproduction steps and traceback.
5. Member 3 merges branches but never rewrites another owner's source file.
6. `models/__init__.py` belongs to Member 3 so Members 1 and 3 never collide on imports.
7. `__manifest__.py` belongs only to Member 3; Member 2 merely provides the final asset paths.
8. `menu_views.xml` belongs only to Member 2; Member 3 provides action XML IDs, not menu edits.
9. No schema, XML ID, method name, or selection key changes after the 15-minute freeze.

---

## 5. Final Addon Structure

```text
transit_ops/
├── __init__.py                                  # M3
├── __manifest__.py                              # M3
├── models/
│   ├── __init__.py                              # M3
│   ├── vehicle.py                               # M1
│   ├── driver.py                                # M1
│   ├── trip.py                                  # M1
│   ├── maintenance.py                           # M3
│   ├── fuel_log.py                              # M3
│   ├── expense.py                               # M3
│   └── dashboard.py                             # M3
├── security/
│   ├── security.xml                             # M2
│   └── ir.model.access.csv                      # M2
├── views/
│   ├── vehicle_views.xml                        # M2
│   ├── driver_views.xml                         # M2
│   ├── trip_views.xml                           # M2
│   ├── dashboard_action.xml                     # M2
│   ├── menu_views.xml                           # M2
│   ├── maintenance_views.xml                    # M3
│   ├── fuel_log_views.xml                       # M3
│   └── expense_views.xml                        # M3
├── static/src/components/dashboard/
│   ├── dashboard.js                             # M2
│   ├── dashboard.xml                            # M2
│   └── dashboard.scss                           # M2
├── data/
│   ├── sequence.xml                             # M1
│   ├── demo_data.xml                            # M4
│   ├── mail_template.xml                        # M3 optional
│   └── license_cron.xml                         # M3 optional
└── report/                                      # M3 optional

docs/
├── TEST_CHECKLIST.md                            # M4
├── DASHBOARD_VISUAL_QA.md                       # M4
├── DEMO_SCRIPT.md                               # M4
├── SUBMISSION_CHECKLIST.md                      # M4
└── screenshots/                                 # M4
```

---

## 6. Frozen Technical Contract

### 6.1 Model names

```text
transit.vehicle
transit.driver
transit.trip
transit.maintenance
transit.fuel.log
transit.expense
transit.dashboard
```

### 6.2 Selection keys

```text
Vehicle status: available, on_trip, in_shop, retired
Driver status:  available, on_trip, off_duty, suspended
Trip state:     draft, dispatched, completed, cancelled
Maintenance:    draft, open, closed, cancelled
Vehicle type:   van, truck, bus, other
Licence type:   lmv, hmv, commercial, other
Expense type:   toll, parking, permit, other
```

### 6.3 Required methods

```text
transit.trip.action_dispatch
transit.trip.action_complete
transit.trip.action_cancel
transit.maintenance.action_start
transit.maintenance.action_close
transit.maintenance.action_cancel
transit.dashboard.get_dashboard_data
```

### 6.4 Shared XML IDs

```text
module_category_transit_ops
group_transit_fleet_manager
group_transit_dispatcher
group_transit_safety_officer
group_transit_financial_analyst

seq_transit_trip

action_transit_dashboard
action_transit_vehicle
action_transit_driver
action_transit_trip
action_transit_maintenance
action_transit_fuel_log
action_transit_expense
action_transit_analytics

menu_transit_ops_root
menu_transit_dashboard
menu_transit_fleet
menu_transit_drivers
menu_transit_trips
menu_transit_maintenance
menu_transit_finance
menu_transit_analytics
```

### 6.5 Shared field contract

#### `transit.vehicle`

```text
name: Char, required
registration_number: Char, required, unique, indexed, uppercase
vehicle_type: Selection(van, truck, bus, other), required
region: Char, indexed
max_load_capacity: Float, required
odometer: Float, required, default 0
acquisition_cost: Monetary, default 0
currency_id: Many2one(res.currency), required
status: Selection(available, on_trip, in_shop, retired), default available, indexed
trip_ids: One2many(transit.trip, vehicle_id)
maintenance_ids: One2many(transit.maintenance, vehicle_id)
fuel_log_ids: One2many(transit.fuel.log, vehicle_id)
expense_ids: One2many(transit.expense, vehicle_id)
total_fuel_cost: Monetary, computed
total_maintenance_cost: Monetary, computed
total_other_expense: Monetary, computed
operational_cost: Monetary, computed as fuel + maintenance
total_revenue: Monetary, computed from completed trips
roi: Float, computed percentage
```

#### `transit.driver`

```text
name: Char, required
license_number: Char, required, unique, uppercase
license_category: Selection(lmv, hmv, commercial, other), required
license_expiry_date: Date, required
contact_number: Char, required
safety_score: Float, required, default 100
status: Selection(available, on_trip, off_duty, suspended), default available, indexed
trip_ids: One2many(transit.trip, driver_id)
license_state: Selection(valid, expiring, expired), computed
```

#### `transit.trip`

```text
name: Char, sequence-generated, readonly
source: Char, required
destination: Char, required
region: Char, indexed
vehicle_id: Many2one(transit.vehicle), required
 driver_id: Many2one(transit.driver), required
cargo_weight: Float, required
planned_distance: Float, required
start_odometer: Float, readonly
final_odometer: Float
actual_distance: Float, computed
fuel_consumed: Float
fuel_cost: Monetary
revenue: Monetary
state: Selection(draft, dispatched, completed, cancelled), default draft, indexed
dispatch_date: Datetime, readonly
completion_date: Datetime, readonly
currency_id: Many2one(res.currency), required
```

`ETA` on the dashboard is display-only. For a dispatched trip, calculate a simple estimate from planned distance at `40 km/h`; for completed trips show `—`; for drafts show `Awaiting vehicle`. Do not add a new mandatory field solely for the wireframe.

#### `transit.maintenance`

```text
name: Char, required
vehicle_id: Many2one(transit.vehicle), required
maintenance_type: Selection(service, repair, inspection, other), required
start_date: Date, required, default today
end_date: Date
cost: Monetary, required, default 0
notes: Text
state: Selection(draft, open, closed, cancelled), default draft, indexed
currency_id: Many2one(res.currency), required
```

#### `transit.fuel.log`

```text
vehicle_id: Many2one(transit.vehicle), required
trip_id: Many2one(transit.trip)
date: Date, required, default today
liters: Float, required
cost: Monetary, required
odometer: Float
currency_id: Many2one(res.currency), required
```

#### `transit.expense`

```text
name: Char, required
vehicle_id: Many2one(transit.vehicle), required
trip_id: Many2one(transit.trip)
expense_type: Selection(toll, parking, permit, other), required
date: Date, required, default today
amount: Monetary, required
currency_id: Many2one(res.currency), required
```

---

## 7. Exact Dashboard Visual Contract

The supplied wireframe is the design source of truth. Do not redesign it into a generic Odoo dashboard.

### 7.1 Desktop canvas

Reference viewport: approximately `1360 x 900`.

```text
Left sidebar: 190 px
Top bar: 56 px
Main content horizontal padding: 20 px
Main content starts after the 190 px sidebar
Dashboard background: white
Style: flat ERP interface, 1 px borders, almost no shadows
```

### 7.2 Colour tokens

```scss
--to-white: #ffffff;
--to-page: #ffffff;
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
--to-grey-pill: #868e96;
```

Use a clean sans-serif stack such as `Arial, Helvetica, sans-serif`.

### 7.3 Left sidebar

Show the product name `TransitOps` at the top, then these items in this exact order:

1. Dashboard
2. Fleet
3. Drivers
4. Trips
5. Maintenance
6. Fuel & Expenses
7. Analytics
8. Settings

The active Dashboard item must have:

- pale orange background `#ffe8cc`
- orange border/accent `#f08c00`
- dark label text
- approximately 34 px height

Other entries remain flat on `#f1f3f5`. Settings may be disabled for non-admin users but must remain visible to preserve the supplied layout.

### 7.4 Top bar

Left side:

- Search input, approximately 260 x 28 px
- Placeholder: `Search...`
- Search filters only the Recent Trips rows client-side

Right side:

- current user display name
- blue role pill, for example `Dispatcher`
- circular avatar with initials

For the demo account, Member 4 should create/document a user named `Raven K.` in the Dispatcher group so the screen closely resembles the wireframe.

### 7.5 Filters row

Title: `FILTERS`

Controls, in this order:

1. `Vehicle Type: All`
2. `Status: All`
3. `Region: All`

The filters call the backend again and refresh KPI cards, vehicle-status bars, and recent trips. Use compact white controls with 1 px grey borders, not large Bootstrap cards.

### 7.6 KPI row

Exactly seven cards in one row at desktop width:

1. ACTIVE VEHICLES
2. AVAILABLE VEHICLES
3. VEHICLES IN MAINTENANCE
4. ACTIVE TRIPS
5. PENDING TRIPS
6. DRIVERS ON DUTY
7. FLEET UTILIZATION

Desktop card target:

```text
height: 80 px
width: about 149 px each
left accent: 4 px
border: 1 px solid #adb5bd
border radius: 0–2 px
shadow: none
label: small uppercase muted text
value: about 22 px dark text
```

Accent colours:

```text
Active Vehicles: blue
Available Vehicles: green
Vehicles in Maintenance: orange
Active Trips: blue
Pending Trips: blue
Drivers On Duty: blue
Fleet Utilization: green
```

### 7.7 Main information area

Use a two-column desktop layout.

#### Left: RECENT TRIPS

Table columns in this exact order:

```text
TRIP | VEHICLE | DRIVER | STATUS | ETA
```

Display the latest four to six trips. Statuses are compact solid pills:

```text
On Trip / Dispatched: blue
Completed: green
Draft: grey
Cancelled: red or muted grey
```

Wireframe-style sample rows for visual testing:

```text
TR001 | VAN-05  | Alex  | On Trip    | 45 min
TR002 | TRK-12  | John  | Completed  | —
TR003 | MINI-08 | Priya | Dispatched | 1h 10m
TR006 | —       | —     | Draft      | Awaiting vehicle
```

The actual production rows must come from Odoo records.

#### Right: VEHICLE STATUS

Show four horizontal bars, in this order:

1. Available — green
2. On Trip — blue
3. In Shop — orange
4. Retired — red

Each item contains label, count, percentage, a light-grey track, and a solid fill. Do not use Chart.js or another chart library.

### 7.8 Responsive rules

```text
>= 1200 px: fixed 190 px sidebar, seven KPI cards in one row, table + status bars side by side
768–1199 px: compact/collapsible sidebar, KPI cards wrap 4 + 3, information panels stack if needed
< 768 px: sidebar becomes drawer, KPI cards use 2 columns then 1, table scrolls horizontally, topbar role/name may compact
```

The desktop layout is the judging priority. Responsive behavior must not destroy the desktop match.

### 7.9 Dashboard frontend boundaries

Member 2 owns only rendering, interaction, navigation, loading, and error states. Member 2 never hard-codes KPI numbers.

Member 3 owns all dashboard queries and the response schema. Member 3 never edits HTML, JavaScript, or SCSS.

Member 4 checks visual fidelity and reports mismatches; Member 4 never edits dashboard source.

---

## 8. Frozen Dashboard API Contract

`transit.dashboard.get_dashboard_data(filters=None)` returns this exact shape:

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
    "recent_trips": [
        {
            "id": 0,
            "name": "TR001",
            "vehicle": "VAN-05",
            "driver": "Alex",
            "state": "dispatched",
            "status_label": "On Trip",
            "eta": "45 min",
        }
    ],
    "filter_options": {
        "vehicle_types": [{"value": "van", "label": "Van"}],
        "statuses": [{"value": "available", "label": "Available"}],
        "regions": [{"value": "Hyderabad", "label": "Hyderabad"}],
    },
    "applied_filters": {
        "vehicle_type": False,
        "status": False,
        "region": False,
    },
    "current_user": {
        "name": "Raven K.",
        "initials": "RK",
        "role": "Dispatcher",
    },
}
```

Supported input:

```python
{
    "vehicle_type": False | "van" | "truck" | "bus" | "other",
    "status": False | "available" | "on_trip" | "in_shop" | "retired",
    "region": False | "Hyderabad",
}
```

### KPI definitions

```text
Active Vehicles = vehicles whose status is not retired
Available Vehicles = status available
Vehicles in Maintenance = status in_shop
Active Trips = state dispatched
Pending Trips = state draft
Drivers On Duty = status on_trip
Fleet Utilization = on_trip vehicles / non-retired vehicles * 100
```

Return `0.0` when the utilization denominator is zero.

---

## 9. Mandatory Business Rules

1. Vehicle registration is unique and normalized to uppercase.
2. Driver licence number is unique and normalized to uppercase.
3. Capacity must be greater than zero.
4. Odometer, cost, fuel, and expense values cannot be negative.
5. Safety score must be between 0 and 100.
6. Retired, In Shop, or On Trip vehicles cannot be dispatched.
7. Suspended, Off Duty, On Trip, or licence-expired drivers cannot be dispatched.
8. A vehicle or driver on another dispatched trip cannot be reused.
9. Cargo weight cannot exceed vehicle capacity.
10. Dispatch sets trip to `dispatched`, records the start odometer/date, and sets vehicle and driver to `on_trip`.
11. Completion requires final odometer >= start odometer, calculates distance, updates vehicle odometer, optionally creates a fuel log, and restores both resources to `available`.
12. Cancelling a dispatched trip restores both resources to `available`.
13. Starting maintenance is blocked for On Trip or Retired vehicles, opens the record, and sets the vehicle to `in_shop`.
14. Closing/cancelling open maintenance restores the vehicle to `available` unless retired.
15. Dispatch domains are convenience only; all rules must also exist in Python.
16. Ordinary users cannot manually bypass workflow states from forms.

---

## 10. RBAC Matrix

Create these groups:

```text
TransitOps / Fleet Manager
TransitOps / Dispatcher
TransitOps / Safety Officer
TransitOps / Financial Analyst
```

| Area | Fleet Manager | Dispatcher | Safety Officer | Financial Analyst |
|---|---:|---:|---:|---:|
| Dashboard | Read | Read | Read | Read |
| Vehicles | CRUD | Read | Read | Read |
| Drivers | Read | Read | Read/Write | Read |
| Trips | Read | CRUD + workflow | Read | Read |
| Maintenance | CRUD | Read | Read | Read |
| Fuel Logs | CRUD | Create/Read | Read | CRUD |
| Expenses | Read | Create/Read | Read | CRUD |
| Analytics | Read | Read | Compliance read | Full read |

Use Odoo `res.users` and `res.groups`; do not create custom user or role models.

---

## 11. Eight-Hour Parallel Schedule

### 00:00–00:15 — freeze and scaffold

**All:** confirm Odoo version, addon path, branch names, model names, fields, XML IDs, and dashboard schema.

**M3:** create the addon folders, empty owned files, root imports, and manifest skeleton.  
**M4:** create docs folders and empty checklist files.  
**Checkpoint:** everyone pulls the same scaffold. No contract changes after minute 15.

### 00:15–01:30 — parallel foundation

**M1**

- Vehicle, Driver, and Trip fields
- SQL/Python constraints
- Trip sequence
- Cost/revenue/ROI compute skeletons

**M2**

- Four groups and ACLs
- Vehicle/Driver/Trip list, form, and search views
- Root menus/actions
- Dashboard client-action shell and exact structural HTML

**M3**

- Maintenance, Fuel Log, Expense models
- Dashboard model and response skeleton
- Owned operational views
- Manifest data and asset ordering skeleton

**M4**

- Draft demo XML using frozen names
- Draft README and test matrix
- Prepare visual QA checklist from Section 7

**01:30 checkpoint:** Python compiles, XML parses, and every member shares only interface information.

### 01:30–02:45 — workflows and first install

**M1**

- Dispatch, complete, cancel
- Duplicate assignment protection
- Fuel-log creation call
- Status restoration and odometer rules

**M2**

- Domains, statusbars, buttons, decorations, group restrictions
- Dashboard sidebar, topbar, filters, KPI row, table, and status-bar markup
- Basic SCSS tokens and desktop grid

**M3**

- Maintenance actions and finance constraints
- Full dashboard queries and filter options
- First merge and module installation at about 02:25

**M4**

- Finish consistent demo data
- Finish installation steps after M3 confirms exact command
- Begin role/user setup instructions

**02:45 checkpoint:** module installs and basic records can be created.

### 02:45–04:00 — dashboard connection and MVP integration

**M1:** run full trip lifecycle and fix only M1 files.  
**M2:** connect Owl to `get_dashboard_data`, implement loading/error/empty states, search, and sidebar actions.  
**M3:** finish operational views, imports, manifest, and API response; run upgrades after merges.  
**M4:** load demo data, run smoke tests, capture first desktop dashboard screenshot, report defects.

**04:00 checkpoint:** required example workflow works once and the custom dashboard displays real data.

### 04:00–05:15 — exact dashboard pass and RBAC

**M1:** verify cost, revenue, ROI, completion, and maintenance interaction guardrails.  
**M2:** match colours, spacing, seven-card row, recent-trip table, status bars, active sidebar item, topbar user/role/avatar, and desktop responsiveness.  
**M3:** verify filtered KPI calculations, current-user payload, recent-trip ordering, role resolution, and query performance.  
**M4:** run the dashboard visual checklist at 1360 x 900 and RBAC tests for all four roles.

**05:15 checkpoint:** dashboard closely matches the supplied wireframe and all role menus open.

### 05:15–06:15 — regression and polish

**M1:** fix only failed core-rule tests.  
**M2:** fix only frontend/security/core-view failures.  
**M3:** fix only operations/API/install failures and verify a clean database install.  
**M4:** execute all mandatory tests, update pass/fail, screenshots, and demo script.

**06:15 feature freeze:** no new features.

### 06:15–07:00 — stabilization

- M4 reruns regression and visual QA.
- Owners fix only confirmed blockers.
- M3 tags a clean release after install and upgrade.
- M2 keeps a minimal native-action emergency fallback, but the custom dashboard remains the demo target.

### 07:00–07:30 — one bonus only

Priority:

1. graph/pivot analytics polish
2. licence reminder
3. PDF report
4. attachments

M4 receives no extra source-code work.

### 07:30–08:00 — submission freeze

- No source changes unless the module cannot start.
- Reset to known demo data.
- Rehearse twice.
- Verify repository, README, screenshots, test file, database, and ZIP.

---

## 12. Dependency and Handoff Matrix

| From | To | Handoff | Deadline |
|---|---|---|---|
| M1 | M2 | final vehicle/driver/trip field names and button methods | 01:15 |
| M3 | M2 | action XML IDs for maintenance/fuel/expense | 01:30 |
| M3 | M2 | dashboard API sample response | 02:30 |
| M2 | M3 | exact static asset paths for manifest | 02:30 |
| M1 + M3 | M4 | stable external IDs for demo records | 02:45 |
| M3 | M4 | exact install/upgrade command | 03:00 |
| M4 | Owners | structured bug reports and screenshots | continuously after 03:00 |

A handoff is information, not permission to edit the sender's files.

---

## 13. Git and AI Generation Protocol

### Branches

```text
main
develop
member1-core-backend
member2-ui-dashboard
member3-ops-integration
member4-qa-docs
```

### Merge order

1. M1 models
2. M3 models/imports/manifest/operational views
3. M2 security/views/static assets
4. M4 demo data/docs

### Commit prefixes

```text
[M1] trip dispatch and completion rules
[M2] wireframe dashboard layout and RBAC
[M3] dashboard API and maintenance workflow
[M4] dashboard visual QA and demo data
```

### Mandatory coding-agent header

```text
Generate or edit only the files listed under MY FILE OWNERSHIP.
Do not create, rename, format, or modify any other file.
Use the frozen model names, field names, selection keys, method names, XML IDs,
dashboard response schema, and visual requirements exactly as written.
Output every file separately with its exact relative path.
Do not redesign the dashboard and do not use placeholder code for P0 features.
Keep imports compatible with the installed Odoo version.
```

Never ask an AI agent to “generate the whole project.”

---

## 14. Mandatory Test Matrix

| ID | Test | Expected | Owner on failure |
|---|---|---|---|
| T01 | Duplicate registration | blocked | M1 |
| T02 | Capacity <= 0 | blocked | M1 |
| T03 | Safety score outside 0–100 | blocked | M1 |
| T04 | Overweight cargo | blocked | M1 |
| T05 | Expired/suspended/off-duty driver | blocked | M1 |
| T06 | In Shop/Retired/On Trip vehicle | blocked | M1 |
| T07 | Duplicate active vehicle/driver | blocked | M1 |
| T08 | Valid dispatch | trip + vehicle + driver become active/on-trip | M1 |
| T09 | Invalid final odometer | blocked | M1 |
| T10 | Valid completion | statuses restored and odometer updated | M1 |
| T11 | Completion with fuel | fuel log created | M1 first, M3 if target model fails |
| T12 | Cancel dispatched trip | resources restored | M1 |
| T13 | Start maintenance | vehicle becomes In Shop | M3 |
| T14 | Close maintenance | vehicle becomes Available | M3 |
| T15 | Negative maintenance/fuel/expense | blocked | M3 |
| T16 | Four ACL role checks | correct | M2 |
| T17 | Dashboard returns exact schema | correct | M3 |
| T18 | Seven KPI cards render from live values | correct | M2/M3 after isolation |
| T19 | Filters refresh all dashboard sections | correct | M2 frontend or M3 data |
| T20 | Recent Trips search works | correct | M2 |
| T21 | 1360 x 900 visual match | passes checklist | M2; M4 reports |
| T22 | Responsive 1024 and 390 widths | usable | M2 |
| T23 | Clean install | works | M3 |
| T24 | Upgrade | works | M3 |
| T25 | Demo data loads | works | M4, contract mismatch routed to owner |

---

## 15. Demo Data Strategy

Keep `Van-05` and `Alex` available for the live workflow. Populate the dashboard with other records:

- `Truck-12` + `John`: one dispatched trip
- `Mini-08` + `Priya`: one dispatched trip
- one completed historical trip
- one draft trip
- `Bus-03`: open maintenance and In Shop
- one retired vehicle
- at least two extra available vehicles
- one expired driver and one suspended driver for validation
- fuel, maintenance, and toll records for cost/analytics proof

The wireframe's sample values such as `53`, `42`, and `81%` are visual examples, not hard-coded production values.

---

## 16. Final Demo — 5 to 6 Minutes

1. **M4, 25 sec:** problem and objective.
2. **M2, 45 sec:** dashboard layout, filters, seven KPIs, recent trips, status bars, role-aware topbar.
3. **M1, 90 sec:** create 450 kg trip with Van-05/Alex, dispatch, status automation, complete with odometer/fuel.
4. **M1, 35 sec:** prove overweight or expired-driver validation.
5. **M3, 45 sec:** maintenance start/close and finance records.
6. **M2/M3, 30 sec:** return to dashboard and show live refresh.
7. **M4, 25 sec:** architecture, test status, and closing value.

---

## 17. Emergency Fallbacks

| Risk | Trigger | Action |
|---|---|---|
| Owl asset error | dashboard cannot mount by Hour 5:30 | M2 isolates frontend error; M3 fixes only manifest path/order |
| Custom dashboard still broken at 06:15 | release blocker | switch Dashboard menu to stable native analytics action; keep screenshot of last working custom build |
| XML parse error | upgrade fails | owner comments only the latest owned record, fixes, re-enables |
| Demo XML fails | external-ID/order issue | install without demo file and create records manually |
| Cross-model call fails | M1 completion cannot create fuel log | guard call, merge M3 model, retest interface |
| AI renamed contract | unknown field/method/XML ID | reject output and regenerate from frozen contract |
| Merge conflict | two edits in same file | restore designated owner's version |

The custom wireframe dashboard is the target; the native fallback is emergency-only.

---

## 18. Definition of Done

- Clean install and upgrade pass.
- Four roles exist and ACLs match the matrix.
- All mandatory workflows and validations pass.
- Custom dashboard uses the supplied layout: 190 px sidebar, 56 px topbar, three filters, seven KPI cards, Recent Trips table, Vehicle Status bars.
- Dashboard values are live and never hard-coded.
- Filters and search work.
- Demo data is consistent.
- README, test checklist, visual QA, screenshots, and demo script are complete.
- The team rehearses twice from a clean demo state.
