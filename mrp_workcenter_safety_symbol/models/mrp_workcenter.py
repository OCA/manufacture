from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"

    safety_symbol_ids = fields.Many2many(
        comodel_name="iso7010.symbol",
        relation="mrp_workcenter_iso7010_symbol_rel",
        column1="workcenter_id",
        column2="symbol_id",
        string="Safety Symbols",
        help="Safety symbols relevant when operating this work center. "
        "Ensure corresponding data modules (e.g., base_iso7010_data_mandatory) "
        "are installed.",
    )
