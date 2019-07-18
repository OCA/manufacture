# -*- coding: utf-8 -*-
# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import _, api, models


class ChangeProductionQty(models.TransientModel):
    _inherit = 'change.production.qty'

    @api.multi
    def change_prod_qty(self):
        """
        Changes the Quantity of Product.
        """
        record_id = self.env.context.get('active_id', False)
        assert record_id, _('Active Id not found')
        prod_obj = self.env['mrp.production']
        bom_line_obj = self.env['mrp.bom.line']
        uom_obj = self.env['product.uom']
        res = super(ChangeProductionQty, self).change_prod_qty()
        for wiz_qty in self:
            prod = prod_obj.browse(record_id)
            for move in prod.move_lines:
                bom_point = prod.bom_id
                factor = uom_obj._compute_qty(prod.product_uom.id,
                                              prod.product_qty,
                                              bom_point.product_uom.id)
                product_details, workcenter_details = (
                    bom_point._bom_explode(prod.product_id,
                                           factor / bom_point.product_qty, []))
                for r in product_details:
                    bom_line = bom_line_obj.browse(r['bom_line'])
                    workorder = prod.workcenter_lines.filtered(
                        lambda x: (x.routing_wc_line == bom_line.operation))
                    if workorder:
                        move.work_order = workorder
        return res
