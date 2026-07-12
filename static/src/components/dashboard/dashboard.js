/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";

export class TransitOpsDashboard extends Component {
    static template = "transit_ops.TransitOpsDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.requestSerial = 0;
        this.state = useState({
            loading: true,
            error: null,
            data: this.emptyData(),
            filters: {
                vehicle_type: false,
                status: false,
                region: false,
            },
            searchTerm: "",
            sidebarOpen: false,
        });

        this.navItems = [
            { label: "Dashboard", active: true, action: null },
            { label: "Fleet", action: "transit_ops.action_transit_vehicle" },
            { label: "Drivers", action: "transit_ops.action_transit_driver" },
            { label: "Trips", action: "transit_ops.action_transit_trip" },
            { label: "Maintenance", action: "transit_ops.action_transit_maintenance" },
            { label: "Fuel & Expenses", action: "transit_ops.action_transit_fuel_log" },
            { label: "Analytics", action: "transit_ops.action_transit_analytics" },
            { label: "Settings", preferences: true },
        ];

        onWillStart(() => this.reloadDashboard());
    }

    emptyData() {
        return {
            schema_version: 1,
            kpis: {
                active_vehicles: 0,
                available_vehicles: 0,
                vehicles_in_maintenance: 0,
                active_trips: 0,
                pending_trips: 0,
                drivers_on_duty: 0,
                fleet_utilization: 0,
            },
            vehicle_status: [
                { key: "available", label: "Available", count: 0, percentage: 0 },
                { key: "on_trip", label: "On Trip", count: 0, percentage: 0 },
                { key: "in_shop", label: "In Shop", count: 0, percentage: 0 },
                { key: "retired", label: "Retired", count: 0, percentage: 0 },
            ],
            recent_trips: [],
            filter_options: {
                vehicle_types: [],
                statuses: [],
                regions: [],
            },
            applied_filters: { vehicle_type: false, status: false, region: false },
            current_user: { name: "", initials: "", role: "" },
        };
    }

    async reloadDashboard() {
        const serial = ++this.requestSerial;
        this.state.loading = true;
        this.state.error = null;
        try {
            const filters = { ...this.state.filters };
            const data = await this.orm.call("transit.dashboard", "get_dashboard_data", [filters]);
            if (serial === this.requestSerial) {
                this.state.data = this.normalizeData(data);
            }
        } catch (error) {
            if (serial === this.requestSerial) {
                this.state.error = error.message || "Unable to load dashboard data.";
            }
        } finally {
            if (serial === this.requestSerial) {
                this.state.loading = false;
            }
        }
    }

    normalizeData(data = {}) {
        data = data || {};
        const defaults = this.emptyData();
        return {
            ...defaults,
            ...data,
            kpis: { ...defaults.kpis, ...(data.kpis || {}) },
            filter_options: { ...defaults.filter_options, ...(data.filter_options || {}) },
            applied_filters: { ...defaults.applied_filters, ...(data.applied_filters || {}) },
            current_user: { ...defaults.current_user, ...(data.current_user || {}) },
            vehicle_status: data.vehicle_status || defaults.vehicle_status,
            recent_trips: data.recent_trips || defaults.recent_trips,
        };
    }

    async onFilterChange(filterName, value) {
        this.state.filters[filterName] = value || false;
        await this.reloadDashboard();
    }

    onSearchInput(value) {
        this.state.searchTerm = value || "";
    }

    toggleSidebar() {
        this.state.sidebarOpen = !this.state.sidebarOpen;
    }

    closeSidebar() {
        this.state.sidebarOpen = false;
    }

    async navigate(item) {
        if (item.disabled) {
            return;
        }
        if (!item.action && !item.preferences) {
            await this.reloadDashboard();
            this.closeSidebar();
            return;
        }
        if (item.preferences) {
            const preferencesAction = await this.orm.call("res.users", "action_get", []);
            preferencesAction.res_id = user.userId;
            await this.action.doAction(preferencesAction);
            this.closeSidebar();
            return;
        }
        await this.action.doAction(item.action);
        this.closeSidebar();
    }

    get kpiCards() {
        const kpis = this.state.data.kpis || {};
        return [
            { label: "ACTIVE VEHICLES", value: this.formatNumber(kpis.active_vehicles) },
            { label: "AVAILABLE VEHICLES", value: this.formatNumber(kpis.available_vehicles) },
            { label: "VEHICLES IN MAINTENANCE", value: this.formatNumber(kpis.vehicles_in_maintenance) },
            { label: "ACTIVE TRIPS", value: this.formatNumber(kpis.active_trips) },
            { label: "PENDING TRIPS", value: this.formatNumber(kpis.pending_trips) },
            { label: "DRIVERS ON DUTY", value: this.formatNumber(kpis.drivers_on_duty) },
            { label: "FLEET UTILIZATION", value: `${this.formatNumber(kpis.fleet_utilization)}%` },
        ];
    }

    get filteredTrips() {
        const trips = this.state.data.recent_trips || [];
        const term = this.state.searchTerm.trim().toLowerCase();
        if (!term) {
            return trips;
        }
        return trips.filter((trip) => {
            return [trip.name, trip.vehicle, trip.driver]
                .filter(Boolean)
                .some((value) => String(value).toLowerCase().includes(term));
        });
    }

    get vehicleStatus() {
        const rows = this.state.data.vehicle_status || [];
        const byKey = Object.fromEntries(rows.map((row) => [row.key, row]));
        return ["available", "on_trip", "in_shop", "retired"].map((key) => {
            return byKey[key] || this.emptyData().vehicle_status.find((row) => row.key === key);
        });
    }

    statusClass(status) {
        const value = String(status || "").toLowerCase();
        if (["dispatched", "on_trip"].includes(value)) {
            return "is-blue";
        }
        if (value === "completed") {
            return "is-green";
        }
        if (value === "draft") {
            return "is-grey";
        }
        if (value === "cancelled") {
            return "is-red";
        }
        return "is-grey";
    }

    barWidth(row) {
        const percentage = Number((row && row.percentage) || 0);
        return `width: ${Math.max(0, Math.min(100, percentage))}%`;
    }

    formatNumber(value) {
        const number = Number(value || 0);
        return Number.isInteger(number) ? String(number) : number.toFixed(1);
    }
}

registry.category("actions").add("transit_ops.dashboard", TransitOpsDashboard);
