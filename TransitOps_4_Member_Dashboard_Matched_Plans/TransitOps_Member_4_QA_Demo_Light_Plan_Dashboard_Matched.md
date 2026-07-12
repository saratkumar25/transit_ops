# Member 4 — QA, Demo Data, Documentation, and Presentation

> **Branch:** `member4-qa-docs`  
> **Workload:** Light and isolated  
> **New outside member:** you do not modify production Python, XML views, security, static assets, imports, or manifest files.

---

## 1. Mission

Make the implementation easy to test, demonstrate, and submit:

- Stable demo data
- README and setup instructions
- Full regression checklist
- Dashboard visual-fidelity checklist
- Screenshots
- 5–6 minute demo script
- Submission checklist
- Clear bug reports routed to the correct owner

This role is intentionally lighter and has no risky release-code ownership.

---

## 2. Exclusive File Ownership

```text
transit_ops/data/demo_data.xml
README.md
docs/TEST_CHECKLIST.md
docs/DASHBOARD_VISUAL_QA.md
docs/DEMO_SCRIPT.md
docs/SUBMISSION_CHECKLIST.md
docs/screenshots/*
```

Never edit:

```text
transit_ops/__init__.py
transit_ops/__manifest__.py
transit_ops/models/*
transit_ops/security/*
transit_ops/views/*
transit_ops/static/*
transit_ops/data/sequence.xml
transit_ops/data/mail_template.xml
transit_ops/data/license_cron.xml
transit_ops/report/*
```

Even when the fix is obvious, report it to the owner.

---

## 3. Bug Routing

| Problem | Owner |
|---|---|
| Vehicle/Driver/Trip fields, validation, status, calculations | Member 1 |
| ACLs, menus, core views, dashboard HTML/JS/SCSS/visual mismatch | Member 2 |
| Maintenance, Fuel, Expense, dashboard numbers/API, install/manifest | Member 3 |
| Demo data, docs, screenshots, checklists | Member 4 |

Bug report template:

```text
Test ID:
Time:
Logged-in user and role:
Screen/URL:
Steps to reproduce:
Expected:
Actual:
Exact error or traceback:
Screenshot path:
Likely owner:
```

---

## 4. Demo Data Strategy

Do not attempt to create 53 vehicles just to copy the wireframe's sample number. The dashboard must use actual records; the reference values are visual examples.

### Keep free for the live demo

#### Vehicle `Van-05`

```text
registration_number: TS09VA0005
vehicle_type: van
region: Hyderabad
max_load_capacity: 500
odometer: 12000
status: available
```

#### Driver `Alex`

```text
licence category: LMV
licence expiry: safely more than one year in the future
safety score: 92
status: available
```

Do not link Van-05 or Alex to a pre-existing active trip.

### Populate the dashboard with other records

Vehicles:

1. `Truck-12`, Hyderabad, on_trip
2. `Mini-08`, Hyderabad, on_trip
3. `Bus-03`, Secunderabad, in_shop with an open maintenance record
4. `Sedan-07`, Hyderabad, retired
5. `Van-09`, Hyderabad, available
6. `Truck-15`, Warangal, available
7. `Van-11`, Secunderabad, available

Drivers:

1. `John`, valid HMV, on_trip
2. `Priya`, valid LMV/HMV as appropriate, on_trip
3. `Sam`, expired licence, available — validation case
4. `Jordan`, valid licence, suspended — validation case
5. `Meera`, valid, available

Trips:

- one dispatched trip using Truck-12 and John
- one dispatched trip using Mini-08 and Priya
- one completed historical trip
- one draft trip
- one cancelled historical trip only if stable

Finance:

- at least one fuel log
- at least one closed maintenance cost
- at least one toll expense
- revenue on completed trip

Keep statuses internally consistent. An on-trip vehicle must have an on-trip driver and dispatched trip. An in-shop vehicle must have open maintenance.

### Record loading

- Use stable XML IDs.
- Use `noupdate="1"` where appropriate.
- Use safe future/expired dates relative to the hackathon date.
- Load demo data only after all model fields and external IDs are frozen.
- If XML becomes a release blocker, document manual creation steps instead of editing production files.

---

## 5. Demo Users

Do not create password-bearing users in demo XML unless the team explicitly decides it is safe and compatible.

Document manual creation of:

```text
Raven K. -> Dispatcher
Fleet Demo -> Fleet Manager
Safety Demo -> Safety Officer
Finance Demo -> Financial Analyst
```

The dashboard screenshot should be taken while logged in as `Raven K.` so the topbar resembles the supplied wireframe. Use initials `RK` and one role only.

---

## 6. `docs/DASHBOARD_VISUAL_QA.md`

Create a checklist with columns:

```text
ID | Requirement | Viewport | Expected | Actual | Pass/Fail | Screenshot | Owner
```

### Desktop visual tests at approximately 1360 x 900

- V01 sidebar is about 190 px wide
- V02 topbar is about 56 px high
- V03 sidebar background is `#f1f3f5`
- V04 brand says TransitOps
- V05 nav order is Dashboard, Fleet, Drivers, Trips, Maintenance, Fuel & Expenses, Analytics, Settings
- V06 Dashboard active item uses pale orange and orange accent
- V07 Search appears at top-left of workspace
- V08 user name, blue role pill, and circular initials appear at top-right
- V09 FILTERS label appears
- V10 filters are Vehicle Type, Status, Region in that order
- V11 exactly seven KPI cards appear in one row
- V12 KPI cards are flat, bordered, and have 4 px left accents
- V13 labels and accent colours match the contract
- V14 RECENT TRIPS exists
- V15 table columns are TRIP, VEHICLE, DRIVER, STATUS, ETA
- V16 status pills use blue/green/grey/red mapping
- V17 VEHICLE STATUS exists
- V18 bars are Available green, On Trip blue, In Shop orange, Retired red
- V19 no heavy shadows, gradients, or third-party chart styling
- V20 the dashboard is visually close to the supplied Excalidraw

### Functional dashboard tests

- V21 all KPI values come from data and change after workflow actions
- V22 all three filters refresh KPIs, bars, and trips
- V23 Search filters the recent-trip rows
- V24 loading state appears without broken layout
- V25 error state has Retry
- V26 zero-data state renders safely
- V27 sidebar actions open correct Odoo actions
- V28 Settings is disabled/guarded for ordinary users

### Responsive tests

- V29 at 1024 px KPI cards wrap cleanly and panels remain usable
- V30 at 390 px sidebar becomes a drawer/compact control, cards remain readable, table scrolls

For every failure, take a screenshot and route to Member 2 unless the number itself is wrong, in which case isolate Member 3's API response.

---

## 7. `docs/TEST_CHECKLIST.md`

Use columns:

```text
ID | Test | Role | Steps | Expected | Actual | Pass/Fail | Bug Owner
```

Mandatory tests:

### Core

- T01 duplicate registration blocked
- T02 invalid capacity blocked
- T03 invalid safety score blocked
- T04 expired driver blocked
- T05 suspended/off-duty driver blocked
- T06 overweight cargo blocked
- T07 In Shop/Retired/On Trip vehicle blocked
- T08 duplicate active vehicle/driver blocked
- T09 valid dispatch changes vehicle/driver to On Trip
- T10 invalid final odometer blocked
- T11 completion restores statuses and updates odometer
- T12 fuel log created on completion
- T13 cancellation restores resources

### Maintenance and finance

- T14 start maintenance sets In Shop
- T15 on-trip/retired maintenance blocked
- T16 close maintenance restores Available
- T17 negative fuel/maintenance/expense blocked
- T18 costs and ROI update

### RBAC

- T19 Dispatcher can manage trip workflow but not edit fleet master
- T20 Fleet Manager can manage vehicles and maintenance
- T21 Safety Officer can update driver compliance
- T22 Financial Analyst can manage fuel/expense
- T23 unauthorized menus/actions are hidden or blocked

### Dashboard and installation

- T24 exact dashboard schema
- T25 KPI counts match records
- T26 filters and search work
- T27 clean install
- T28 upgrade
- T29 demo data loads
- T30 every menu/action opens without traceback

---

## 8. README

Required structure:

```text
# TransitOps
## Problem
## Solution
## Features
## Dashboard Design
## Tech Stack
## Folder Structure
## Prerequisites
## Installation
## Run and Upgrade Commands
## Demo Users and Roles
## Demo Data
## Demo Workflow
## Business Rules
## Screenshots
## Test Results
## Known Limitations
## Team Responsibilities
```

Ask Member 3 for the exact install/upgrade commands actually used. Do not invent commands.

In Dashboard Design, mention:

- wireframe-matched 190 px sidebar and 56 px topbar
- three filters
- seven KPIs
- Recent Trips
- Vehicle Status bars
- responsive layout

---

## 9. Screenshots

Capture and name consistently:

```text
01_dashboard_desktop.png
02_dashboard_filters.png
03_vehicle_registry.png
04_driver_compliance.png
05_trip_draft.png
06_trip_dispatched.png
07_trip_completed.png
08_validation_error.png
09_maintenance_in_shop.png
10_finance_analytics.png
11_role_access.png
12_dashboard_mobile.png
```

Do not crop out the dashboard sidebar/topbar in the primary screenshot.

---

## 10. Demo Script

### Speaking order

- Member 4: problem, objective, final value
- Member 2: dashboard and RBAC/UI
- Member 1: trip workflow and validation
- Member 3: maintenance, costs, dashboard refresh

### 5–6 minute timing

```text
0:00–0:25  Problem
0:25–1:10  Wireframe-matched dashboard
1:10–2:40  Van-05/Alex trip dispatch and completion
2:40–3:15  Validation failure
3:15–4:05  Maintenance workflow
4:05–4:40  Fuel, expenses, ROI
4:40–5:15  Dashboard refresh and filters
5:15–5:40  Architecture, tests, closing
```

Have a backup sequence ready if a live record is already in the wrong state.

---

## 11. Hour Plan

### 00:00–00:15

Create owned docs and read the frozen contract.

### 00:15–01:30

Draft demo XML, README, regression matrix, and visual QA checklist.

### 01:30–02:45

Finalize consistent records after owners confirm fields/XML IDs. Document users and setup.

### 02:45–04:00

Load demo data, run smoke tests, report bugs, take first screenshots.

### 04:00–05:15

Run all dashboard visual checks and RBAC tests.

### 05:15–06:15

Run full regression, update README, screenshots, and script.

### 06:15–07:30

Rerun failed tests after owner fixes; finish submission pack.

### 07:30–08:00

Rehearse twice and freeze documentation.

---

## 12. Acceptance Checklist

- Demo data is consistent and loads.
- Van-05 and Alex remain free for live demo.
- Dashboard has non-zero sample data.
- Raven K. user setup is documented.
- All 30 functional tests have results.
- All dashboard visual checks have results.
- Every failed test has a routed bug report.
- README uses real commands.
- Primary screenshot shows the full dashboard shell.
- Demo script fits 5–6 minutes.
- No production file was edited.

---

## 13. Claude / Antigravity Prompt

```text
You are Member 4 handling only demo data, QA documentation, screenshots planning,
README, and presentation for an Odoo addon named transit_ops.
Generate or edit only:
- transit_ops/data/demo_data.xml
- README.md
- docs/TEST_CHECKLIST.md
- docs/DASHBOARD_VISUAL_QA.md
- docs/DEMO_SCRIPT.md
- docs/SUBMISSION_CHECKLIST.md
Do not output or modify Python, imports, manifest, security, views, static assets,
sequence, operational data templates, or reports. Keep Van-05 and Alex available for
the live demo. Populate other consistent records for dashboard KPIs. Include the exact
wireframe visual checklist from this plan. Output each owned file separately.
```
