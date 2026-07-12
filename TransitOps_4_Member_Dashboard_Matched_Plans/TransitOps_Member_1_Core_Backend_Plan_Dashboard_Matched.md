# Member 1 — Core Backend and Trip Rules

> **Branch:** `member1-core-backend`  
> **Workload:** High  
> **Do not edit any file outside the ownership list.**  
> The dashboard frontend is not your responsibility, but your data must satisfy the frozen dashboard contract.

---

## 1. Mission

Implement the domain core:

- Vehicle model and calculated economics
- Driver model and licence state
- Trip model and complete lifecycle
- Mandatory validation rules
- Automatic resource status transitions
- Trip sequence
- Stable interfaces used by Member 2, Member 3, and Member 4

---

## 2. Exclusive File Ownership

```text
transit_ops/models/vehicle.py
transit_ops/models/driver.py
transit_ops/models/trip.py
transit_ops/data/sequence.xml
```

Never edit:

```text
transit_ops/__init__.py
transit_ops/__manifest__.py
transit_ops/models/__init__.py
transit_ops/models/maintenance.py
transit_ops/models/fuel_log.py
transit_ops/models/expense.py
transit_ops/models/dashboard.py
transit_ops/security/*
transit_ops/views/*
transit_ops/static/*
transit_ops/data/demo_data.xml
README.md
docs/*
```

Member 3 owns all imports and manifest entries. Give Member 3 your filenames; do not add the imports yourself.

---

## 3. Frozen Names

```text
Models:
- transit.vehicle
- transit.driver
- transit.trip

Trip methods:
- action_dispatch
- action_complete
- action_cancel

Trip sequence XML ID:
- seq_transit_trip
```

Selections:

```text
Vehicle: available, on_trip, in_shop, retired
Driver: available, on_trip, off_duty, suspended
Trip: draft, dispatched, completed, cancelled
```

---

## 4. `vehicle.py`

### Model

```python
_name = "transit.vehicle"
_description = "Transit Vehicle"
_order = "registration_number"
```

### Fields

```text
name: Char, required
registration_number: Char, required, indexed
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
operational_cost: Monetary, computed
total_revenue: Monetary, computed
roi: Float, computed
```

### Required behavior

- Normalize `registration_number` with `strip().upper()` on create/write.
- Add a database uniqueness constraint.
- Reject capacity <= 0.
- Reject negative odometer or acquisition cost.
- Compute totals from related records.
- `operational_cost = total_fuel_cost + total_maintenance_cost` exactly, because this is the challenge formula.
- `roi = (total_revenue - operational_cost) / acquisition_cost * 100`.
- Return zero when acquisition cost is zero.
- Compute total revenue from completed trips only.
- Do not automatically change workflow status from ordinary manual field edits.

### Cross-model dependency

The One2many comodels are created by Member 3. Keep names exact and do not create substitute models.

---

## 5. `driver.py`

### Model

```python
_name = "transit.driver"
_description = "Transit Driver"
_order = "name"
```

### Fields

```text
name: Char, required
license_number: Char, required
license_category: Selection(lmv, hmv, commercial, other), required
license_expiry_date: Date, required
contact_number: Char, required
safety_score: Float, required, default 100
status: Selection(available, on_trip, off_duty, suspended), default available, indexed
trip_ids: One2many(transit.trip, driver_id)
license_state: Selection(valid, expiring, expired), computed
```

### Required behavior

- Normalize licence number with `strip().upper()`.
- Add uniqueness constraint.
- Safety score must be 0–100.
- `license_state`:
  - expired when expiry < today
  - expiring when expiry is today through today + 30 days
  - valid otherwise
- Do not automatically suspend an expired driver; dispatch validation blocks them.

---

## 6. `trip.py`

### Model

```python
_name = "transit.trip"
_description = "Transit Trip"
_order = "create_date desc, id desc"
```

### Fields

```text
name: Char, sequence-generated, readonly
source: Char, required
destination: Char, required
region: Char, indexed
vehicle_id: Many2one(transit.vehicle), required, ondelete restrict
driver_id: Many2one(transit.driver), required, ondelete restrict
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

### Creation rules

- Assign sequence when `name` is missing or `/`.
- Reject source == destination after trimming/case normalization.
- Reject cargo weight <= 0.
- Reject planned distance <= 0.
- Reject negative fuel/revenue/final odometer values.
- Use company currency by default.

### `action_dispatch`

For every record:

1. State must be `draft`.
2. Vehicle status must be `available`.
3. Driver status must be `available`.
4. Vehicle cannot be retired, in shop, or on another dispatched trip.
5. Driver cannot be suspended, off duty, expired, or on another dispatched trip.
6. Cargo must not exceed maximum capacity.
7. Search again for any other `dispatched` trip using the same vehicle or driver.
8. Save vehicle odometer to `start_odometer`.
9. Set `dispatch_date` to current datetime.
10. Set trip state to `dispatched`.
11. Set vehicle and driver status to `on_trip`.

Use clear `ValidationError` or `UserError` messages that Member 4 can demo.

### `action_complete`

1. State must be `dispatched`.
2. Require `final_odometer`.
3. Require final odometer >= start odometer.
4. Calculate actual distance.
5. If fuel cost is entered, fuel litres must be > 0.
6. If fuel litres are entered, create one `transit.fuel.log` with vehicle, trip, date, litres, cost, and final odometer.
7. Update vehicle odometer.
8. Set completion datetime and state `completed`.
9. Restore vehicle and driver to `available`, but do not overwrite a deliberately retired vehicle.

The `transit.fuel.log` model belongs to Member 3. Call it by exact name; do not implement it here.

### `action_cancel`

- Draft -> cancelled; no resource change.
- Dispatched -> cancelled and restore both resources to available.
- Completed -> block cancellation in MVP.
- Repeated cancellation must not corrupt statuses.

### ETA used by dashboard

Do not add a mandatory ETA field. Member 3 calculates a display string:

```text
Dispatched: ceil(planned_distance / 40 * 60) minutes
Completed: —
Draft: Awaiting vehicle
Cancelled: —
```

---

## 7. Sequence File

Create `seq_transit_trip` with a clear prefix such as `TR` and sufficient padding. Do not define demo records or menu/action XML here.

---

## 8. Handoffs

### By 01:15 to Member 2

Send:

- final field list
- exact selection keys
- button methods
- fields shown/hidden by state

### By 01:20 to Member 3

Send:

- model filenames for imports
- One2many comodel names
- exact fuel-log create values expected by `action_complete`
- fields dashboard backend can query

### By 02:45 to Member 4

Send:

- stable external sequence behavior
- valid/invalid demo record requirements
- recommended validation messages

Do not edit their files during handoff.

---

## 9. Hour Plan

### 00:00–00:15

Read the frozen contract, verify branch, and refuse any schema changes after the freeze.

### 00:15–01:30

Implement all fields, normalization, SQL constraints, computed fields, and the sequence.

### 01:30–02:45

Implement dispatch, complete, cancel, duplicate checks, odometer updates, and fuel-log call.

### 02:45–04:00

Integrate with Member 3's models and run the complete Van-05/Alex workflow.

### 04:00–05:15

Verify ROI/cost calculations, status restoration, and edge cases found by Member 4.

### 05:15–06:15

Fix only failed M1 tests. No new fields after 05:30.

### 06:15–08:00

Regression support and demo rehearsal; change code only for confirmed blockers.

---

## 10. Acceptance Tests

- Duplicate registration blocked.
- Duplicate licence blocked.
- Invalid capacity/odometer/safety score blocked.
- Expired/suspended/off-duty drivers blocked at dispatch.
- In Shop/Retired/On Trip vehicles blocked.
- Overweight cargo blocked.
- Duplicate active assignment blocked.
- Valid dispatch changes all three statuses correctly.
- Completion validates odometer and creates fuel log.
- Cancellation restores resources.
- Costs and ROI compute without division errors.
- Dashboard backend can query every required field without unknown-field errors.

---

## 11. Claude / Antigravity Prompt

```text
You are Member 1 implementing only the core backend of an Odoo addon named transit_ops.
Generate or edit only:
- transit_ops/models/vehicle.py
- transit_ops/models/driver.py
- transit_ops/models/trip.py
- transit_ops/data/sequence.xml
Do not output or modify imports, manifest, security, views, static assets, other models,
demo data, README, or docs. Use every field, selection key, method, model name, and XML ID
in this plan exactly. Keep all mandatory rules in Python, not only in XML. Output each owned
file separately with its exact path. Do not redesign the architecture.
```
