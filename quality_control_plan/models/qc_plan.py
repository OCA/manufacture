# Copyright 2019 Marcelo Frare (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# Copyright 2019 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QcPlan(models.Model):
    """
    Manages quality control plans
    """

    # model
    _name = "qc.plan"
    _description = "Quality Control Plan"

    _inherit = ["mail.thread"]

    # fields
    # alphanumeric identification code
    name = fields.Char("Name", required=True)
    # description of plan calculation
    description = fields.Char("Description")
    # free pass option
    free_pass = fields.Boolean("Free pass")
    # control levels of the plan
    plan_ids = fields.One2many("qc.level", "plan_id", "Plan")

    @api.onchange("free_pass")
    def on_change_free_pass(self):
        """
        Checks if there is only one free pass plan
        Sets the last changed to false if another one exists
        """

        if self.free_pass:
            free_p = self.env["qc.plan"].search([("free_pass", "=", True)])[0]
            if free_p:
                self.free_pass = False
                raise ValidationError(
                    _("A free pass plan already exists: %s.") % free_p.name
                )

    @api.model
    def create(self, vals):
        """
        Avoids multiple free pass plans
        """
        if vals["free_pass"]:
            if self.env["qc.plan"].search([("free_pass", "=", True)]):
                return False
        return super(QcPlan, self).create(vals)


class QcLevel(models.Model):
    """
    Manages the lelevs for a control plan
    """

    # model
    _name = "qc.level"
    _description = "Quality Control Plan Levels"

    # fields
    # plan reference
    plan_id = fields.Many2one("qc.plan", "Plan", required=True)
    # minimum ingoing quantity
    qty_received = fields.Float(
        "Quantity to inspect", help="Minimum received quantity reference"
    )
    # quantity value to check
    qty_checked = fields.Float(
        "Quantity checked",
        help="Quantity to check if the received goods is higher than the reference",
    )
    # chek value type: absolute or percent of ingoing quantity
    chk_type = fields.Selection(
        [
            ("absolute", "Absolute value"),
            ("percent", "Percent"),
        ],
        "Measure",
        default="absolute",
        help="Indicate how to use quantity checked value",
    )

    # defines record name to display in form view
    _rec_name = "id"
