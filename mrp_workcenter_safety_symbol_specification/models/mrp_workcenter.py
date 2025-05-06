from odoo import fields, models


class MrpWorkcenter(models.Model):
    """Inherit mrp.workcenter to add the One2many specification field."""

    _inherit = "mrp.workcenter"

    # The M2M field 'safety_symbol_ids' still exists from the dependency module,
    # but will be hidden by the view modification in this module.

    safety_specification_ids = fields.One2many(
        comodel_name="mrp.workcenter.safety.specification",
        inverse_name="workcenter_id",
        string="Safety Specifications",
        copy=True,
        help="Define safety symbols required for this work center and add "
        "specific instructions.",
    )
