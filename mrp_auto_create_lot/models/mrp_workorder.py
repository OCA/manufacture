# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    @api.multi
    def record_production(self):
        if not self.final_lot_id and self.product_id.auto_create_lot:
            self.final_lot_id = self.env['stock.production.lot'].create({
                'product_id': self.product_id.id,
            })
        return super().record_production()
