# TransitOps - Smart Transport Operations Platform

TransitOps is an Odoo 19 based smart transport operations platform built for managing fleets, drivers, trips, maintenance, fuel, expenses, and live operational analytics from one role-aware dashboard.

The application is designed for transport teams that need a clean workflow from vehicle registration to dispatch, safety checks, finance tracking, and executive visibility. It combines Odoo's reliable backend, PostgreSQL storage, role-based access control, and a custom OWL dashboard UI tailored for transport operations.

## Key Features

- Custom TransitOps authentication page with role selection
- Role-based access control for operational teams
- Fleet and vehicle management
- Driver management with license and safety tracking
- Trip creation, dispatch, completion, and cancellation workflows
- Maintenance records with open/closed lifecycle
- Fuel log and expense tracking
- Live dashboard with KPIs, filters, recent trips, and vehicle status distribution
- Sample fleet data for demos and testing
- Odoo 19 compatible security, views, controllers, and constraints

## Roles

TransitOps includes four custom operational roles:

| Role | Main Responsibility | Access Focus |
| --- | --- | --- |
| Fleet Manager | Fleet readiness and maintenance | Vehicles, maintenance, fuel logs |
| Dispatcher | Trip operations | Dashboard, trips, fuel logs, expenses |
| Safety Officer | Driver and compliance tracking | Drivers and safety-related records |
| Financial Analyst | Cost and finance tracking | Fuel logs, expenses, analytics |

Odoo's built-in administrator account can be used for full access during development and demo:

```text
Login: admin
Password: admin
```

## Demo Accounts

All demo accounts use the classroom/demo password shared with the team.

| Role | Login |
| --- | --- |
| Dispatcher | dispatcher@transitops.local |
| Fleet Manager | fleet.manager@transitops.local |
| Safety Officer | safety.officer@transitops.local |
| Financial Analyst | finance.analyst@transitops.local |

## Dashboard

The custom dashboard opens after login and shows live data from Odoo models:

- Active vehicles
- Available vehicles
- Vehicles in maintenance
- Active trips
- Pending trips
- Drivers on duty
- Fleet utilization
- Recent trips
- Vehicle status breakdown
- Filters for vehicle type, status, and state/region

The dashboard is backed by the `transit.dashboard` service model and uses Odoo's ORM to fetch current data from PostgreSQL.

## Data Storage

TransitOps stores application data in PostgreSQL through Odoo models. The main business tables include:

```text
transit_vehicle
transit_driver
transit_trip
transit_maintenance
transit_fuel_log
transit_expense
```

Manual records created from the UI are stored in the local Odoo database. Source code and starter records are stored in this repository.

## Sample Data

The module includes starter data in:

```text
data/sample_data.xml
```

This provides vehicles, drivers, trips, maintenance, fuel, and expense records so the dashboard has meaningful values immediately after module update.

## Local Development

Open the project folder:

```bash
cd transit_ops
```

Update the Odoo module after code changes:

```bash
docker exec transitops-odoo odoo -d transitops -u transit_ops --db_host=transitops-db --db_user=odoo --db_password=odoo --without-demo=True --stop-after-init
```

Restart Odoo:

```bash
docker restart transitops-odoo
```

Open the app:

```bash
open http://localhost:8069
```

Useful debug command:

```bash
docker logs --tail 100 transitops-odoo
```

## Technology Stack

- Odoo 19
- Python models and controllers
- PostgreSQL database
- XML views and security rules
- OWL dashboard component
- SCSS dashboard styling
- Docker based local runtime

## Project Structure

```text
controllers/        Custom login and auth flow
models/             TransitOps business models and dashboard service
views/              Odoo XML views, menus, dashboard actions, login template
security/           Groups and access control rules
data/               Sequences and sample data
static/src/         OWL dashboard frontend assets
report/             Report assets and templates
```

## Purpose

TransitOps was built as a hackathon-ready transport operations platform. It demonstrates how Odoo can be extended into a focused business application with custom workflows, role-based dashboards, real database-backed records, and a polished first-screen experience.
