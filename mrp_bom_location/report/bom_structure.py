# © 2017 Eficent Business and IT Consulting Services S.L.
#        (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class BomStructureReport(models.AbstractModel):
    _inherit = 'report.mrp.mrp_bom_structure_report'

    @staticmethod
    def _get_child_vals(record, level, qty, uom):
        child = {
            'pname': record.product_id.name_get()[0][1],
            'pcode': record.product_id.default_code,
            'puom': record.product_uom_id,
            'uname': record.product_uom_id.name,
            'level': level,
            'code': record.bom_id.code,
            'location_name': record.location_id.complete_name or '',
        }
        qty_per_bom = record.bom_id.product_qty
        if uom:
            if uom != record.bom_id.product_uom_id:
                qty = uom._compute_quantity(qty, record.bom_id.product_uom_id)
            child['pqty'] = (record.product_qty * qty) / qty_per_bom
        else:
            # for the first case, the ponderation is right
            child['pqty'] = (record.product_qty * qty)
        return child

    def get_children(self, records, level=0):
        result = []

        def _get_children_recursive(records, level, qty=1.0, uom=None):
            for l in records:
                child = self._get_child_vals(l, level, qty, uom)
                result.append(child)
                if l.child_line_ids:
                    if level < 6:
                        level += 1
                    _get_children_recursive(
                        l.child_line_ids,
                        level,
                        qty=child['pqty'],
                        uom=child['puom']
                    )
                    if level > 0 and level < 6:
                        level -= 1
            return result

        children = _get_children_recursive(records, level)

        return children

    @api.multi
    def get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'doc_model': 'mrp.bom',
            'docs': self.env['mrp.bom'].browse(docids),
            'get_children': self.get_children,
            'data': data,
        }
