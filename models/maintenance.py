
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class TransitMaintenance(models.Model):
    _name = "transit.maintenance"
    _description = "Transit Maintenance"
    _order = "start_date desc, id desc"

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
    maintenance_type = fields.Selection(
        [
            ("service", "Service"),
            ("repair", "Repair"),
            ("inspection", "Inspection"),
            ("other", "Other"),
        ],
        string="Type",
        required=True,
    )
    start_date = fields.Date(
        string="Start Date",
        required=True,
        default=fields.Date.context_today,
    )
    end_date = fields.Date(string="End Date")
    cost = fields.Monetary(
        string="Cost",
        required=True,
        default=0,
    )
    notes = fields.Text(string="Notes")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("open", "Open"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        string="State",
        default="draft",
        index=True,
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    # ------------------------------------------------------------------
    # SQL Constraints
    # ------------------------------------------------------------------
    _sql_constraints = [
        (
            "cost_non_negative",
            "CHECK(cost >= 0)",
            "Maintenance cost cannot be negative.",
        ),
    ]

    # ------------------------------------------------------------------
    # Python Constraints
    # ------------------------------------------------------------------
    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for rec in self:
            if rec.end_date and rec.start_date and rec.end_date < rec.start_date:
                raise ValidationError(
                    "End date cannot be earlier than start date."
                )

    @api.constrains("state", "vehicle_id")
    def _check_unique_open_maintenance(self):
        for rec in self:
            if rec.state == "open":
                existing = self.search([
                    ("vehicle_id", "=", rec.vehicle_id.id),
                    ("state", "=", "open"),
                    ("id", "!=", rec.id),
                ], limit=1)
                if existing:
                    raise ValidationError(
                        "Vehicle '%s' already has an open maintenance record (%s). "
                        "Close or cancel it before opening a new one."
                        % (rec.vehicle_id.name, existing.name)
                    )

    # ------------------------------------------------------------------
    # Workflow Actions
    # ------------------------------------------------------------------
    def action_start(self):
        """Draft → Open. Sets vehicle to in_shop."""
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Only draft maintenance records can be started."
                )
            vehicle = rec.vehicle_id
            if vehicle.status == "on_trip":
                raise UserError(
                    "Cannot start maintenance for vehicle '%s' — it is currently on a trip."
                    % vehicle.name
                )
            if vehicle.status == "retired":
                raise UserError(
                    "Cannot start maintenance for vehicle '%s' — it is retired."
                    % vehicle.name
                )
            # Check no other open maintenance for this vehicle
            existing = self.search([
                ("vehicle_id", "=", vehicle.id),
                ("state", "=", "open"),
                ("id", "!=", rec.id),
            ], limit=1)
            if existing:
                raise UserError(
                    "Vehicle '%s' already has an open maintenance record (%s)."
                    % (vehicle.name, existing.name)
                )
            rec.state = "open"
            vehicle.status = "in_shop"

    def action_close(self):
        """Open → Closed. Restores vehicle to available (unless retired)."""
        for rec in self:
            if rec.state != "open":
                raise UserError(
                    "Only open maintenance records can be closed."
                )
            if not rec.end_date:
                rec.end_date = fields.Date.today()
            rec.state = "closed"
            if rec.vehicle_id.status != "retired":
                rec.vehicle_id.status = "available"

    def action_cancel(self):
        """Draft/Open → Cancelled. Restores vehicle if was open."""
        for rec in self:
            if rec.state not in ("draft", "open"):
                raise UserError(
                    "Only draft or open maintenance records can be cancelled. "
                    "Closed records cannot be undone."
                )
            was_open = rec.state == "open"
            rec.state = "cancelled"
            if was_open and rec.vehicle_id.status != "retired":
                rec.vehicle_id.status = "available"
