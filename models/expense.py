from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TransitExpense(models.Model):
    _name = "transit.expense"
    _description = "Transit Expense"
    _order = "date desc, id desc"

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------
    name = fields.Char(string="Description", required=True)
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
    expense_type = fields.Selection(
        [
            ("toll", "Toll"),
            ("parking", "Parking"),
            ("permit", "Permit"),
            ("other", "Other"),
        ],
        string="Expense Type",
        required=True,
    )
    date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today,
    )
    amount = fields.Monetary(string="Amount", required=True)
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    # ------------------------------------------------------------------
    # SQL Constraints
    # ------------------------------------------------------------------
    _amount_non_negative = models.Constraint(
        "CHECK(amount >= 0)",
        "Expense amount cannot be negative.",
    )

    # ------------------------------------------------------------------
    # Python Constraints
    # ------------------------------------------------------------------
    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount < 0:
                raise ValidationError("Expense amount cannot be negative.")

    # ------------------------------------------------------------------
    # Overrides — trim name
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name"):
                vals["name"] = vals["name"].strip()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("name"):
            vals["name"] = vals["name"].strip()
        return super().write(vals)
