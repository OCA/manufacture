# Copyright 2023 Komit - Cuong Nguyen Mtm
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    type = fields.Selection(
        selection_add=[("supplier", "Supplier")],
        ondelete={"supplier": "set default"},
        help="Supplier: For information only, this BOM is not meant to be used "
        "for manufacturing nor to trigger any purchase.",
    )
