# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _get_lot_number_propagation_bom_types(self):
        types = super()._get_lot_number_propagation_bom_types()
        return types + ["subcontract"]
