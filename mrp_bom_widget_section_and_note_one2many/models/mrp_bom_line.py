# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: BADEP
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    # Returns mandatory for classic line thanks to _sql_constraints and view
    product_id = fields.Many2one(required=False)
    product_uom_id = fields.Many2one(required=False)

    # New fields to handle section & note
    name = fields.Text(string="Description")

    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )

    _sql_constraints = [
        (
            "bom_required_fields_product_qty",
            "CHECK(display_type IS NOT NULL OR"
            "(product_id IS NOT NULL AND product_qty IS NOT NULL))",
            "Missing required fields on bom line : product and quantity.",
        ),
        (
            "bom_required_field_uom",
            "CHECK(display_type IS NOT NULL OR" "(product_uom_id IS NOT NULL))",
            "Missing required field on bom line : uom.",
        ),
        (
            "non_bom_null_fields",
            "CHECK(display_type IS NULL OR" "(product_id IS NULL AND product_qty = 1))",
            "Forbidden values on note and section bom line",
        ),
    ]
