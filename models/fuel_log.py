from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TransitFuelLog(models.Model):
    _name = "transit.fuel.log"
    _description = "Transit Fuel Log"
    _order = "date desc, id desc"

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------
    vehicle_id = fields.Many2one(
        "transit.vehicle",
        string="Vehicle",
        required=True,
        ondelete="restrict",
    )
    trip_id = fields.Many2one(
        "transit.trip",
        string="Trip",
    )
    date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today,
    )
    liters = fields.Float(string="Liters", required=True)
    cost = fields.Monetary(string="Cost", required=True)
    odometer = fields.Float(string="Odometer")
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    # ------------------------------------------------------------------
    # SQL Constraints
    # ------------------------------------------------------------------
    _liters_positive = models.Constraint(
        "CHECK(liters > 0)",
        "Fuel quantity (liters) must be greater than zero.",
    )
    _cost_non_negative = models.Constraint(
        "CHECK(cost >= 0)",
        "Fuel cost cannot be negative.",
    )
    _odometer_non_negative = models.Constraint(
        "CHECK(odometer >= 0)",
        "Odometer reading cannot be negative.",
    )
    _unique_trip_fuel_log = models.Constraint(
        "UNIQUE(trip_id)",
        "A fuel log already exists for this trip.",
    )

    # ------------------------------------------------------------------
    # Python Constraints
    # ------------------------------------------------------------------
    @api.constrains("liters")
    def _check_liters(self):
        for rec in self:
            if rec.liters <= 0:
                raise ValidationError(
                    "Fuel quantity (liters) must be greater than zero."
                )

    @api.constrains("cost")
    def _check_cost(self):
        for rec in self:
            if rec.cost < 0:
                raise ValidationError("Fuel cost cannot be negative.")

    @api.constrains("odometer")
    def _check_odometer(self):
        for rec in self:
            if rec.odometer < 0:
                raise ValidationError("Odometer reading cannot be negative.")
