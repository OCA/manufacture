# Copyright 2024 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    subcontract_purchase_description = fields.Text(
        string="Description for Purchase Order Lines",
        translate=True,
        help="If there are several subcontract bills of material for the same product "
        "it is important to provide this description so that the subcontractor knows "
        "which bill of material to use.",
    )
