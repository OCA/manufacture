# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
#        (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv
from openerp.report import report_sxw


class bom_structure(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(bom_structure, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_children': self.get_children,
        })

    def get_children(self, object, level=0):
        result = []

        def _get_rec(object, level, qty=1.0):
            for l in object:
                res = {}
                res['pname'] = l.product_id.name_get()[0][1]
                res['pcode'] = l.product_id.default_code
                res['pqty'] = l.product_qty * qty
                res['uname'] = l.product_uom.name
                res['level'] = level
                res['code'] = l.bom_id.code
                res['location_name'] = l.location_id.complete_name or ''
                result.append(res)
                if l.child_line_ids:
                    if level<6:
                        level += 1
                    _get_rec(l.child_line_ids, level, qty=res['pqty'])
                    if level>0 and level<6:
                        level -= 1
            return result

        children = _get_rec(object,level)

        return children


class report_mrpbomstructure_location(osv.AbstractModel):
    _inherit = 'report.mrp.report_mrpbomstructure'
    _template = 'mrp.report_mrpbomstructure'
    _wrapped_report_class = bom_structure
