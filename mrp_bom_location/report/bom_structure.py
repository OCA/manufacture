# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
#        (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models


class BomStructureReport(models.AbstractModel):
    _inherit = 'report.mrp.report_mrpbomstructure'

    def get_children(self, record, level=0):
        result = []

        def _get_rec(record, level, qty=1.0, uom=False):
            for l in record:
                res = {}
                res['pname'] = l.product_id.name_get()[0][1]
                res['pcode'] = l.product_id.default_code
                qty_per_bom = l.bom_id.product_qty
                if uom:
                    if uom != l.bom_id.product_uom_id:
                        qty = uom._compute_quantity(
                            qty, l.bom_id.product_uom_id)
                    res['pqty'] = (l.product_qty * qty) / qty_per_bom
                else:
                    # for the first case, the ponderation is right
                    res['pqty'] = (l.product_qty * qty)
                res['puom'] = l.product_uom_id
                res['uname'] = l.product_uom_id.name
                res['level'] = level
                res['code'] = l.bom_id.code
                res['location_name'] = l.location_id.complete_name or ''
                result.append(res)
                if l.child_line_ids:
                    if level < 6:
                        level += 1
                    _get_rec(
                        l.child_line_ids, level,
                        qty=res['pqty'], uom=res['puom'])
                    if 0 < level < 6:
                        level -= 1
            return result

        children = _get_rec(record, level)

        return children
