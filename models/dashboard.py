import math

from odoo import api, fields, models


class TransitDashboard(models.Model):
    _name = "transit.dashboard"
    _description = "TransitOps Dashboard Service"

    # ------------------------------------------------------------------
    # No user-facing fields — this model is an API-only service.
    # A single placeholder field keeps the ORM happy.
    # ------------------------------------------------------------------
    name = fields.Char(default="Dashboard Service")

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------
    _VEHICLE_STATUS_ORDER = [
        ("available", "Available"),
        ("on_trip", "On Trip"),
        ("in_shop", "In Shop"),
        ("retired", "Retired"),
    ]

    _TRIP_STATE_LABELS = {
        "dispatched": "On Trip",
        "completed": "Completed",
        "draft": "Draft",
        "cancelled": "Cancelled",
    }

    _VALID_VEHICLE_TYPES = {"van", "truck", "bus", "other"}
    _VALID_STATUSES = {"available", "on_trip", "in_shop", "retired"}

    _ROLE_PRECEDENCE = [
        ("transit_ops.group_transit_dispatcher", "Dispatcher"),
        ("transit_ops.group_transit_fleet_manager", "Fleet Manager"),
        ("transit_ops.group_transit_safety_officer", "Safety Officer"),
        ("transit_ops.group_transit_financial_analyst", "Financial Analyst"),
    ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @api.model
    def get_dashboard_data(self, filters=None):
        """Return the exact frozen dashboard payload.

        :param filters: dict with optional keys vehicle_type, status, region
        :returns: dict matching the frozen dashboard API contract
        """
        filters = self._sanitize_filters(filters)

        # Build vehicle domain from filters
        vehicle_domain = self._build_vehicle_domain(filters)

        # Fetch KPIs
        kpis = self._compute_kpis(vehicle_domain, filters)

        # Vehicle status distribution
        vehicle_status = self._compute_vehicle_status(vehicle_domain)

        # Recent trips
        recent_trips = self._compute_recent_trips(vehicle_domain, filters)

        # Filter options
        filter_options = self._compute_filter_options()

        # Applied filters echo
        applied_filters = {
            "vehicle_type": filters.get("vehicle_type") or False,
            "status": filters.get("status") or False,
            "region": filters.get("region") or False,
        }

        # Current user info
        current_user = self._compute_current_user()

        return {
            "schema_version": 1,
            "kpis": kpis,
            "vehicle_status": vehicle_status,
            "recent_trips": recent_trips,
            "filter_options": filter_options,
            "applied_filters": applied_filters,
            "current_user": current_user,
        }

    # ------------------------------------------------------------------
    # Private: Filter Sanitization
    # ------------------------------------------------------------------
    def _sanitize_filters(self, filters):
        """Validate and sanitize filter input. Ignore bad values."""
        if not filters or not isinstance(filters, dict):
            return {}

        clean = {}

        vt = filters.get("vehicle_type")
        if vt and vt in self._VALID_VEHICLE_TYPES:
            clean["vehicle_type"] = vt

        st = filters.get("status")
        if st and st in self._VALID_STATUSES:
            clean["status"] = st

        region = filters.get("region")
        if region and isinstance(region, str) and region.strip():
            clean["region"] = region.strip()

        return clean

    # ------------------------------------------------------------------
    # Private: Vehicle Domain
    # ------------------------------------------------------------------
    def _build_vehicle_domain(self, filters):
        """Build an ORM domain for transit.vehicle from sanitized filters."""
        domain = []
        if filters.get("vehicle_type"):
            domain.append(("vehicle_type", "=", filters["vehicle_type"]))
        if filters.get("status"):
            domain.append(("status", "=", filters["status"]))
        if filters.get("region"):
            domain.append(("region", "=", filters["region"]))
        return domain

    # ------------------------------------------------------------------
    # Private: KPIs
    # ------------------------------------------------------------------
    def _compute_kpis(self, vehicle_domain, filters):
        Vehicle = self.env["transit.vehicle"]
        Trip = self.env["transit.trip"]
        Driver = self.env["transit.driver"]

        # Vehicle KPIs (filtered)
        active_vehicles = Vehicle.search_count(
            vehicle_domain + [("status", "!=", "retired")]
        )
        available_vehicles = Vehicle.search_count(
            vehicle_domain + [("status", "=", "available")]
        )
        vehicles_in_maintenance = Vehicle.search_count(
            vehicle_domain + [("status", "=", "in_shop")]
        )
        on_trip_vehicles = Vehicle.search_count(
            vehicle_domain + [("status", "=", "on_trip")]
        )

        # Fleet utilization
        non_retired = Vehicle.search_count(
            vehicle_domain + [("status", "!=", "retired")]
        )
        if non_retired > 0:
            fleet_utilization = round(on_trip_vehicles / non_retired * 100, 1)
        else:
            fleet_utilization = 0.0

        # Trip KPIs — filter by vehicle set when vehicle filters are active
        trip_domain = self._build_trip_domain(vehicle_domain, filters)
        active_trips = Trip.search_count(
            trip_domain + [("state", "=", "dispatched")]
        )
        pending_trips = Trip.search_count(
            trip_domain + [("state", "=", "draft")]
        )

        # Drivers on duty — global count (drivers aren't filtered by vehicle)
        drivers_on_duty = Driver.search_count([("status", "=", "on_trip")])

        return {
            "active_vehicles": active_vehicles,
            "available_vehicles": available_vehicles,
            "vehicles_in_maintenance": vehicles_in_maintenance,
            "active_trips": active_trips,
            "pending_trips": pending_trips,
            "drivers_on_duty": drivers_on_duty,
            "fleet_utilization": fleet_utilization,
        }

    # ------------------------------------------------------------------
    # Private: Trip Domain from Vehicle Domain
    # ------------------------------------------------------------------
    def _build_trip_domain(self, vehicle_domain, filters):
        """Build trip domain.

        - vehicle_type / status filters: restrict trips to vehicles matching those filters.
        - region filter: match trip.region OR vehicle.region (OR logic).
        - When no filters active, return empty domain (all trips).
        """
        domain = []
        Vehicle = self.env["transit.vehicle"]

        has_vehicle_filter = filters.get("vehicle_type") or filters.get("status")
        has_region_filter = filters.get("region")

        if has_vehicle_filter and has_region_filter:
            # Vehicles matching type/status filter
            vehicle_ids = Vehicle.search(vehicle_domain).ids
            # Vehicles matching region filter
            region_vehicle_ids = Vehicle.search(
                [("region", "=", filters["region"])]
            ).ids
            # Combined: (vehicle in type/status set) AND (trip.region matches OR vehicle.region matches)
            if not vehicle_ids:
                # No matching vehicles → no trips
                return [("id", "=", 0)]
            domain = [
                "&",
                ("vehicle_id", "in", vehicle_ids),
                "|",
                ("region", "=", filters["region"]),
                ("vehicle_id", "in", region_vehicle_ids),
            ]
        elif has_vehicle_filter:
            vehicle_ids = Vehicle.search(vehicle_domain).ids
            if vehicle_ids:
                domain = [("vehicle_id", "in", vehicle_ids)]
            else:
                domain = [("id", "=", 0)]
        elif has_region_filter:
            # Region filter: trip.region matches OR vehicle is in a matching-region vehicle
            region_vehicle_ids = Vehicle.search(
                [("region", "=", filters["region"])]
            ).ids
            domain = [
                "|",
                ("region", "=", filters["region"]),
                ("vehicle_id", "in", region_vehicle_ids),
            ]

        return domain

    # ------------------------------------------------------------------
    # Private: Vehicle Status
    # ------------------------------------------------------------------
    def _compute_vehicle_status(self, vehicle_domain):
        """Return all four status entries with counts and percentages."""
        Vehicle = self.env["transit.vehicle"]
        total = Vehicle.search_count(vehicle_domain)

        result = []
        for key, label in self._VEHICLE_STATUS_ORDER:
            count = Vehicle.search_count(
                vehicle_domain + [("status", "=", key)]
            )
            percentage = round(count / total * 100, 1) if total > 0 else 0.0
            result.append({
                "key": key,
                "label": label,
                "count": count,
                "percentage": percentage,
            })
        return result

    # ------------------------------------------------------------------
    # Private: Recent Trips
    # ------------------------------------------------------------------
    def _compute_recent_trips(self, vehicle_domain, filters):
        """Return latest 6 trips with labels and ETA."""
        Trip = self.env["transit.trip"]
        trip_domain = self._build_trip_domain(vehicle_domain, filters)

        trips = Trip.search(
            trip_domain,
            order="dispatch_date desc, completion_date desc, create_date desc, id desc",
            limit=6,
        )

        result = []
        for trip in trips:
            result.append({
                "id": trip.id,
                "name": trip.name or "",
                "vehicle": trip.vehicle_id.name or "—",
                "driver": trip.driver_id.name or "—",
                "state": trip.state,
                "status_label": self._TRIP_STATE_LABELS.get(trip.state, trip.state),
                "eta": self._compute_eta(trip),
            })
        return result

    def _compute_eta(self, trip):
        """Compute ETA display string for a trip."""
        if trip.state == "dispatched":
            if not trip.planned_distance:
                return "—"
            total_minutes = math.ceil(trip.planned_distance / 40 * 60)
            if total_minutes < 60:
                return "%d min" % total_minutes
            hours = total_minutes // 60
            minutes = total_minutes % 60
            if minutes == 0:
                return "%dh" % hours
            return "%dh %dm" % (hours, minutes)
        elif trip.state in ("completed", "cancelled"):
            return "—"
        elif trip.state == "draft":
            return "Awaiting vehicle"
        return "—"

    # ------------------------------------------------------------------
    # Private: Filter Options
    # ------------------------------------------------------------------
    def _compute_filter_options(self):
        """Return available filter values from existing records."""
        Vehicle = self.env["transit.vehicle"]
        Trip = self.env["transit.trip"]

        # Vehicle types — from the selection field definition
        vehicle_type_labels = dict(
            Vehicle._fields["vehicle_type"].selection
        )
        # Always expose all supported vehicle types, even before demo data exists.
        vehicle_types = [
            {"value": value, "label": label}
            for value, label in Vehicle._fields["vehicle_type"].selection
        ]

        # Statuses — always show all four
        statuses = [
            {"value": key, "label": label}
            for key, label in self._VEHICLE_STATUS_ORDER
        ]

        # Regions — unique non-empty regions from vehicles and trips
        regions_set = set()
        vehicle_regions = Vehicle.search_read(
            [("region", "!=", False), ("region", "!=", "")],
            ["region"],
        )
        for vr in vehicle_regions:
            if vr["region"]:
                regions_set.add(vr["region"].strip())

        trip_regions = Trip.search_read(
            [("region", "!=", False), ("region", "!=", "")],
            ["region"],
        )
        for tr in trip_regions:
            if tr["region"]:
                regions_set.add(tr["region"].strip())

        if not regions_set:
            regions_set.update(["Karnataka", "Telangana", "Tamil Nadu", "Maharashtra", "Kerala"])

        regions = sorted([
            {"value": r, "label": r} for r in regions_set
        ], key=lambda x: x["label"])

        return {
            "vehicle_types": vehicle_types,
            "statuses": statuses,
            "regions": regions,
        }

    # ------------------------------------------------------------------
    # Private: Current User
    # ------------------------------------------------------------------
    def _compute_current_user(self):
        """Return user info with role based on group precedence."""
        user = self.env.user
        name = user.name or ""

        # Initials: first letters of first two words
        parts = name.split()
        if len(parts) >= 2:
            initials = (parts[0][0] + parts[1][0]).upper()
        elif len(parts) == 1 and parts[0]:
            initials = parts[0][0].upper()
        else:
            initials = ""

        # Role with precedence
        role = "User"
        for group_xmlid, role_label in self._ROLE_PRECEDENCE:
            try:
                if user.has_group(group_xmlid):
                    role = role_label
                    break
            except Exception:
                continue

        return {
            "name": name,
            "initials": initials,
            "role": role,
        }
