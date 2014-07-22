# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.report import report_sxw


class bom_structure(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(bom_structure, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_children': self.get_children,
        })

    def get_children(self, object, level=0):
        result = []

        def _get_rec(object, level):
            for l in object:
                res = {
                    'name': l.name,
                    'pname': l.product_id.name,
                    'pcode': l.product_id.default_code,
                    'pqty': l.product_qty,
                    'uname': l.product_uom.name,
                    'code': l.code,
                    'level': level,
                    'bnumber': l.bubble_number,
                }
                result.append(res)
                if l.child_complete_ids:
                    if level < 6:
                        level += 1
                    _get_rec(l.child_complete_ids, level)
                    if 0 < level < 6:
                        level -= 1
            return result

        children = _get_rec(object, level)

        return children

report_sxw.report_sxw('report.industrialdesign.bom.structure',
                      'mrp.bom',
                      'mrp_industrial_design_bom/report/bom_structure_industrial_design.rml',
                      parser=bom_structure,
                      header='internal')
