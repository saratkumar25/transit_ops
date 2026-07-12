# Member 1 — Core Backend
# Owned file: transit_ops/models/driver.py
# Do not edit outside this file's scope.

from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TransitDriver(models.Model):
    _name = "transit.driver"
    _description = "Transit Driver"
    _order = "name"

    name = fields.Char(required=True)
    license_number = fields.Char(required=True)
    license_category = fields.Selection(
        [
            ("lmv", "LMV"),
            ("hmv", "HMV"),
            ("commercial", "Commercial"),
            ("other", "Other"),
        ],
        required=True,
    )
    license_expiry_date = fields.Date(required=True)
    contact_number = fields.Char(required=True)
    safety_score = fields.Float(required=True, default=100.0)
    status = fields.Selection(
        [
            ("available", "Available"),
            ("on_trip", "On Trip"),
            ("off_duty", "Off Duty"),
            ("suspended", "Suspended"),
        ],
        default="available",
        index=True,
    )
    trip_ids = fields.One2many("transit.trip", "driver_id", string="Trips")
    license_state = fields.Selection(
        [
            ("valid", "Valid"),
            ("expiring", "Expiring"),
            ("expired", "Expired"),
        ],
        compute="_compute_license_state",
        store=True,
    )

    _license_number_uniq = models.Constraint(
        "UNIQUE(license_number)",
        "License number must be unique.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("license_number"):
                vals["license_number"] = vals["license_number"].strip().upper()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("license_number"):
            vals["license_number"] = vals["license_number"].strip().upper()
        return super().write(vals)

    @api.constrains("safety_score")
    def _check_safety_score(self):
        for rec in self:
            if rec.safety_score < 0 or rec.safety_score > 100:
                raise ValidationError("Safety score must be between 0 and 100.")

    @api.depends("license_expiry_date")
    def _compute_license_state(self):
        today = fields.Date.context_today(self)
        soon = today + timedelta(days=30)
        for rec in self:
            if not rec.license_expiry_date:
                rec.license_state = "valid"
            elif rec.license_expiry_date < today:
                rec.license_state = "expired"
            elif rec.license_expiry_date <= soon:
                rec.license_state = "expiring"
            else:
                rec.license_state = "valid"