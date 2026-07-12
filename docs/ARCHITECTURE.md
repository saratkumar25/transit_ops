# TransitOps Architecture

TransitOps is an Odoo addon named `transit_ops`. It digitizes a transport operation workflow from fleet and driver registration through trip dispatch, maintenance, fuel, expenses, and dashboard reporting.

This document is the shared technical architecture for the team. The member-specific plans remain the source of detailed implementation tasks.

## System Overview

```text
Odoo Web Client
    |
    |-- Native list/form/kanban/search views
    |-- Custom Owl dashboard client action
    |
Odoo Addon: transit_ops
    |
    |-- Security and RBAC
    |-- Business models and workflow actions
    |-- Dashboard service API
    |-- Demo data and documentation
    |
PostgreSQL through Odoo ORM
```

## Main User Flows

1. A dispatcher creates a trip with a vehicle, driver, cargo weight, and planned distance.
2. Dispatch validates vehicle availability, driver availability, licence status, duplicate assignments, and cargo capacity.
3. Dispatch moves the trip to `dispatched` and sets both vehicle and driver to `on_trip`.
4. Completion records final odometer, fuel litres, and fuel cost.
5. Completion updates the vehicle odometer, creates a fuel log when fuel is entered, and returns resources to `available`.
6. Maintenance can move a vehicle to `in_shop`, removing it from dispatch choices.
7. The custom dashboard reads live KPIs, filters, recent trips, and vehicle status distribution from the backend service.

## Addon Structure

```text
transit_ops/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── vehicle.py
│   ├── driver.py
│   ├── trip.py
│   ├── maintenance.py
│   ├── fuel_log.py
│   ├── expense.py
│   └── dashboard.py
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── views/
│   ├── vehicle_views.xml
│   ├── driver_views.xml
│   ├── trip_views.xml
│   ├── dashboard_action.xml
│   ├── menu_views.xml
│   ├── maintenance_views.xml
│   ├── fuel_log_views.xml
│   └── expense_views.xml
├── static/src/components/dashboard/
│   ├── dashboard.js
│   ├── dashboard.xml
│   └── dashboard.scss
├── data/
│   ├── sequence.xml
│   └── demo_data.xml
└── report/

docs/
├── ARCHITECTURE.md
├── GITHUB_WORKFLOW.md
├── TEST_CHECKLIST.md
├── DASHBOARD_VISUAL_QA.md
├── DEMO_SCRIPT.md
├── SUBMISSION_CHECKLIST.md
└── screenshots/
```

## Domain Model

| Model | Purpose | Owner |
|---|---|---|
| `transit.vehicle` | Fleet registry, capacity, odometer, lifecycle status, costs, ROI | Member 1 |
| `transit.driver` | Driver registry, licence compliance, safety score, availability | Member 1 |
| `transit.trip` | Dispatch workflow, cargo validation, completion, fuel-log creation | Member 1 |
| `transit.maintenance` | Maintenance lifecycle and in-shop vehicle status | Member 3 |
| `transit.fuel.log` | Fuel consumption and fuel cost records | Member 3 |
| `transit.expense` | Toll, parking, permit, and other operating expenses | Member 3 |
| `transit.dashboard` | JSON-safe dashboard API service for the Owl dashboard | Member 3 |

## Workflow States

```text
Vehicle:      available -> on_trip -> available
Vehicle:      available -> in_shop -> available
Vehicle:      available -> retired

Driver:       available -> on_trip -> available
Driver:       available -> off_duty
Driver:       available -> suspended

Trip:         draft -> dispatched -> completed
Trip:         draft -> cancelled
Trip:         dispatched -> cancelled

Maintenance:  draft -> open -> closed
Maintenance:  draft -> cancelled
Maintenance:  open -> cancelled
```

Completed trips cannot be cancelled in the MVP. Closed maintenance records cannot be cancelled in the MVP.

## Business Rules

- Vehicle registration numbers and driver licence numbers are unique and normalized to uppercase.
- Capacity, distance, odometer, fuel, cost, expense, and revenue values cannot be invalid or negative.
- Safety score must stay between `0` and `100`.
- Retired, in-shop, or on-trip vehicles cannot be dispatched.
- Suspended, off-duty, on-trip, or licence-expired drivers cannot be dispatched.
- A vehicle or driver cannot be assigned to two dispatched trips.
- Cargo weight must be less than or equal to vehicle capacity.
- Dispatch and maintenance domains in XML are convenience only. Python must enforce every rule.

## Security Architecture

Use Odoo groups and ACLs. Do not create custom user or role models.

| Role | Main Permission |
|---|---|
| Fleet Manager | Manage vehicles and maintenance, read operations and finance |
| Dispatcher | Manage trip workflow, create/read fuel and expenses |
| Safety Officer | Read operations, update driver compliance |
| Financial Analyst | Manage fuel and expense records, read operational records |

Workflow buttons should be visible only to roles that can perform those actions, but server-side rules must still protect the methods.

## Dashboard Architecture

The dashboard is a custom Owl client action tagged:

```text
transit_ops.dashboard
```

Frontend responsibilities:

- Render the wireframe-matched layout.
- Keep the 190 px sidebar, 56 px topbar, filters, seven KPIs, recent trips, and vehicle status bars.
- Call `transit.dashboard.get_dashboard_data(filters)`.
- Do local search inside recent trips.
- Reload backend data when dashboard filters change.

Backend responsibilities:

- Return the exact frozen response shape.
- Validate filter values.
- Calculate KPIs from ORM records.
- Return latest six trips and vehicle status percentages.
- Return current user's name, initials, and role label.

The frontend must not hard-code KPI values. The backend must not edit dashboard markup or styles.

## Dashboard API Contract

```python
transit.dashboard.get_dashboard_data(filters=None)
```

Input:

```python
{
    "vehicle_type": False | "van" | "truck" | "bus" | "other",
    "status": False | "available" | "on_trip" | "in_shop" | "retired",
    "region": False | "Hyderabad",
}
```

Required top-level response keys:

```text
schema_version
kpis
vehicle_status
recent_trips
filter_options
applied_filters
current_user
```

KPI definitions:

```text
Active Vehicles = status != retired
Available Vehicles = status == available
Vehicles in Maintenance = status == in_shop
Active Trips = state == dispatched
Pending Trips = state == draft
Drivers On Duty = status == on_trip
Fleet Utilization = on_trip vehicles / non-retired vehicles * 100
```

## File Ownership

One production file has one owner. Reading another member's file is allowed; editing it is not.

| Area | Owner |
|---|---|
| Vehicle, Driver, Trip models and trip sequence | Member 1 |
| Security, core views, menus, dashboard JS/XML/SCSS | Member 2 |
| Manifest, imports, maintenance, fuel, expense, dashboard API, release integration | Member 3 |
| Demo data, README, QA docs, screenshots, presentation | Member 4 |

If a bug appears in another member's file, report it with steps, expected result, actual result, traceback, screenshot path, and likely owner.

## Integration Order

1. Member 3 creates the addon scaffold, imports, and manifest skeleton.
2. Member 1 adds Vehicle, Driver, Trip, and sequence.
3. Member 3 adds Maintenance, Fuel Log, Expense, and Dashboard API.
4. Member 2 adds security, menus, views, and dashboard frontend.
5. Member 4 adds demo data and test/docs assets after fields and XML IDs are stable.
6. Member 3 performs release integration, install, upgrade, and merge coordination.

## Acceptance Criteria

- Addon installs and upgrades without traceback.
- Demo data loads cleanly.
- Four roles and ACLs work as expected.
- Van-05 and Alex dispatch, complete, and return to available.
- Overweight cargo, expired driver, duplicate assignment, and in-shop vehicle validations are blocked.
- Maintenance start/close changes vehicle status correctly.
- Fuel log is created when a trip is completed with fuel values.
- Dashboard opens, matches the wireframe, and refreshes KPIs from backend data.
- Every menu and action opens without traceback.
