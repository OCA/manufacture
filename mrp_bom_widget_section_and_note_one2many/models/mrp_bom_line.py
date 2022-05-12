# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: BADEP
# @author: Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    # To handle bom_line section & note, we have to make these fiels not required
    product_id = fields.Many2one(required=False)
    product_qty = fields.Float(required=False)

    # New fields to handle section & note
    name = fields.Text(string="Description")

    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )
