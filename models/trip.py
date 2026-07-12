# Member 1 — Core Backend
# Owned file: transit_ops/models/trip.py
# Do not edit outside this file's scope.

import math

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class TransitTrip(models.Model):
    _name = "transit.trip"
    _description = "Transit Trip"
    _order = "create_date desc, id desc"

    name = fields.Char(default="", copy=False)
    source = fields.Char(required=True)
    destination = fields.Char(required=True)
    region = fields.Char(index=True)
    vehicle_id = fields.Many2one("transit.vehicle", required=True, ondelete="restrict")
    driver_id = fields.Many2one("transit.driver", required=True, ondelete="restrict")
    cargo_weight = fields.Float(required=True)
    planned_distance = fields.Float(required=True)
    start_odometer = fields.Float(readonly=True)
    final_odometer = fields.Float()
    actual_distance = fields.Float(compute="_compute_actual_distance", store=True)
    fuel_consumed = fields.Float()
    fuel_cost = fields.Monetary(currency_field="currency_id")
    revenue = fields.Monetary(currency_field="currency_id")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("dispatched", "Dispatched"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        index=True,
    )
    dispatch_date = fields.Datetime()
    completion_date = fields.Datetime()
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("transit.trip") or "/"
        records = super().create(vals_list)
        records._check_source_destination()
        records._check_cargo_and_distance()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "source" in vals or "destination" in vals:
            self._check_source_destination()
        if "cargo_weight" in vals or "planned_distance" in vals:
            self._check_cargo_and_distance()
        return res

    def _check_source_destination(self):
        for rec in self:
            if (
                rec.source
                and rec.destination
                and rec.source.strip().lower() == rec.destination.strip().lower()
            ):
                raise ValidationError("Source and destination cannot be the same.")

    def _check_cargo_and_distance(self):
        for rec in self:
            if rec.cargo_weight <= 0:
                raise ValidationError("Cargo weight must be greater than zero.")
            if rec.planned_distance <= 0:
                raise ValidationError("Planned distance must be greater than zero.")

    @api.constrains("fuel_cost", "revenue", "final_odometer")
    def _check_non_negative(self):
        for rec in self:
            if rec.fuel_cost and rec.fuel_cost < 0:
                raise ValidationError("Fuel cost cannot be negative.")
            if rec.revenue and rec.revenue < 0:
                raise ValidationError("Revenue cannot be negative.")
            if rec.final_odometer and rec.final_odometer < 0:
                raise ValidationError("Final odometer cannot be negative.")

    @api.depends("start_odometer", "final_odometer")
    def _compute_actual_distance(self):
        for rec in self:
            if rec.final_odometer and rec.start_odometer is not None:
                rec.actual_distance = rec.final_odometer - rec.start_odometer
            else:
                rec.actual_distance = 0.0

    def action_dispatch(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only draft trips can be dispatched.")

            vehicle = rec.vehicle_id
            driver = rec.driver_id

            if vehicle.status == "retired":
                raise UserError("%s is retired and cannot be dispatched." % vehicle.name)
            if vehicle.status == "in_shop":
                raise UserError("%s is in shop and cannot be dispatched." % vehicle.name)
            if vehicle.status == "on_trip":
                raise UserError("%s is already on a trip." % vehicle.name)
            if vehicle.status != "available":
                raise UserError("%s is not available." % vehicle.name)

            if driver.status == "suspended":
                raise UserError("%s is suspended and cannot be dispatched." % driver.name)
            if driver.status == "off_duty":
                raise UserError("%s is off duty and cannot be dispatched." % driver.name)
            if driver.status == "on_trip":
                raise UserError("%s is already on a trip." % driver.name)
            if driver.status != "available":
                raise UserError("%s is not available." % driver.name)
            if driver.license_state == "expired":
                raise UserError("%s's license has expired." % driver.name)

            if rec.cargo_weight > vehicle.max_load_capacity:
                raise UserError(
                    "Cargo weight %.2f exceeds %s's capacity of %.2f."
                    % (rec.cargo_weight, vehicle.name, vehicle.max_load_capacity)
                )

            duplicate = self.search(
                [
                    ("id", "!=", rec.id),
                    ("state", "=", "dispatched"),
                    "|",
                    ("vehicle_id", "=", vehicle.id),
                    ("driver_id", "=", driver.id),
                ],
                limit=1,
            )
            if duplicate:
                raise UserError(
                    "%s or %s is already assigned to dispatched trip %s."
                    % (vehicle.name, driver.name, duplicate.name)
                )

            rec.write(
                {
                    "start_odometer": vehicle.odometer,
                    "dispatch_date": fields.Datetime.now(),
                    "state": "dispatched",
                }
            )
            vehicle.write({"status": "on_trip"})
            driver.write({"status": "on_trip"})

    def action_complete(self):
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Only dispatched trips can be completed.")
            if not rec.final_odometer:
                raise UserError("Final odometer is required to complete the trip.")
            if rec.final_odometer < rec.start_odometer:
                raise UserError("Final odometer cannot be less than the start odometer.")
            if rec.fuel_cost and not rec.fuel_consumed:
                raise UserError("Fuel litres must be entered when a fuel cost is provided.")

            rec.write(
                {
                    "completion_date": fields.Datetime.now(),
                    "state": "completed",
                }
            )

            # Handoff contract with Member 3 (transit.fuel.log):
            # vehicle_id, trip_id, date, fuel_litres, cost, odometer
            if rec.fuel_consumed:
                self.env["transit.fuel.log"].create(
                    {
                        "vehicle_id": rec.vehicle_id.id,
                        "trip_id": rec.id,
                        "date": fields.Date.context_today(rec),
                        "fuel_litres": rec.fuel_consumed,
                        "cost": rec.fuel_cost,
                        "odometer": rec.final_odometer,
                    }
                )

            rec.vehicle_id.write({"odometer": rec.final_odometer})
            if rec.vehicle_id.status != "retired":
                rec.vehicle_id.write({"status": "available"})
            rec.driver_id.write({"status": "available"})

    def action_cancel(self):
        for rec in self:
            if rec.state == "completed":
                raise UserError("Completed trips cannot be cancelled.")
            if rec.state == "cancelled":
                continue
            was_dispatched = rec.state == "dispatched"
            rec.write({"state": "cancelled"})
            if was_dispatched:
                rec.vehicle_id.write({"status": "available"})
                rec.driver_id.write({"status": "available"})

    def get_eta_display(self):
        """Used by Member 3's dashboard backend to render the ETA column."""
        self.ensure_one()
        if self.state == "dispatched":
            minutes = math.ceil(self.planned_distance / 40 * 60)
            return "%d minutes" % minutes
        if self.state == "completed":
            return "—"
        if self.state == "draft":
            return "Awaiting vehicle"
        return "—"