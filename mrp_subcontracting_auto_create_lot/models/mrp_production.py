# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    product_auto_create_lot = fields.Boolean(compute="_compute_product_auto_create_lot")

    def _compute_product_auto_create_lot(self):
        for production in self:
            product = production.product_id
            production.product_auto_create_lot = (
                product.auto_create_lot or product.categ_id.auto_create_lot
            )

    def subcontracting_record_component(self):
        self.ensure_one()
        if self._get_subcontract_move():
            self._set_auto_lot_producing()
        return super().subcontracting_record_component()
