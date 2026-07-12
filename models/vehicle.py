# Member 1 — Core Backend

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TransitVehicle(models.Model):
    _name = "transit.vehicle"
    _description = "Transit Vehicle"
    _order = "registration_number"

    name = fields.Char(required=True)
    registration_number = fields.Char(required=True, index=True)
    vehicle_type = fields.Selection(
        [
            ("van", "Van"),
            ("truck", "Truck"),
            ("bus", "Bus"),
            ("other", "Other"),
        ],
        required=True,
    )
    region = fields.Char(index=True)
    max_load_capacity = fields.Float(required=True)
    odometer = fields.Float(required=True, default=0.0)
    acquisition_cost = fields.Monetary(default=0.0, currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    status = fields.Selection(
        [
            ("available", "Available"),
            ("on_trip", "On Trip"),
            ("in_shop", "In Shop"),
            ("retired", "Retired"),
        ],
        default="available",
        index=True,
    )

    # Comodels below are owned by Member 3. Names are frozen — do not rename.
    trip_ids = fields.One2many("transit.trip", "vehicle_id", string="Trips")
    maintenance_ids = fields.One2many(
        "transit.maintenance", "vehicle_id", string="Maintenance Records"
    )
    fuel_log_ids = fields.One2many("transit.fuel.log", "vehicle_id", string="Fuel Logs")
    expense_ids = fields.One2many("transit.expense", "vehicle_id", string="Expenses")

    total_fuel_cost = fields.Monetary(
        compute="_compute_costs", currency_field="currency_id", store=True
    )
    total_maintenance_cost = fields.Monetary(
        compute="_compute_costs", currency_field="currency_id", store=True
    )
    total_other_expense = fields.Monetary(
        compute="_compute_costs", currency_field="currency_id", store=True
    )
    operational_cost = fields.Monetary(
        compute="_compute_costs", currency_field="currency_id", store=True
    )
    total_revenue = fields.Monetary(
        compute="_compute_costs", currency_field="currency_id", store=True
    )
    roi = fields.Float(compute="_compute_costs", store=True)

    _registration_number_uniq = models.Constraint(
        "UNIQUE(registration_number)",
        "Registration number must be unique.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("registration_number"):
                vals["registration_number"] = vals["registration_number"].strip().upper()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("registration_number"):
            vals["registration_number"] = vals["registration_number"].strip().upper()
        return super().write(vals)

    @api.constrains("max_load_capacity")
    def _check_capacity(self):
        for rec in self:
            if rec.max_load_capacity <= 0:
                raise ValidationError("Max load capacity must be greater than zero.")

    @api.constrains("odometer")
    def _check_odometer(self):
        for rec in self:
            if rec.odometer < 0:
                raise ValidationError("Odometer cannot be negative.")

    @api.constrains("acquisition_cost")
    def _check_acquisition_cost(self):
        for rec in self:
            if rec.acquisition_cost < 0:
                raise ValidationError("Acquisition cost cannot be negative.")

    # NOTE for Member 3 handoff: this compute expects the following field
    # names to exist on the related models:
    #   transit.fuel.log.cost
    #   transit.maintenance.cost
    #   transit.expense.amount
    #   transit.trip.revenue (already owned by M1)
    @api.depends(
        "fuel_log_ids.cost",
        "maintenance_ids.cost",
        "expense_ids.amount",
        "trip_ids.state",
        "trip_ids.revenue",
        "acquisition_cost",
    )
    def _compute_costs(self):
        for rec in self:
            total_fuel_cost = sum(rec.fuel_log_ids.mapped("cost"))
            total_maintenance_cost = sum(rec.maintenance_ids.mapped("cost"))
            total_other_expense = sum(rec.expense_ids.mapped("amount"))
            operational_cost = total_fuel_cost + total_maintenance_cost
            total_revenue = sum(
                rec.trip_ids.filtered(lambda t: t.state == "completed").mapped("revenue")
            )

            rec.total_fuel_cost = total_fuel_cost
            rec.total_maintenance_cost = total_maintenance_cost
            rec.total_other_expense = total_other_expense
            rec.operational_cost = operational_cost
            rec.total_revenue = total_revenue

            if rec.acquisition_cost:
                rec.roi = (total_revenue - operational_cost) / rec.acquisition_cost * 100.0
            else:
                rec.roi = 0.0