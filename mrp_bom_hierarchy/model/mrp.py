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

from odoo import fields, models


class Bom(models.Model):
    _inherit = "mrp.bom"

    def get_child_boms(self, cr, uid, ids, context=None):
        result = {}
        if not ids:
            return result
        for curr_id in ids:
            result[curr_id] = True
        # Now add the children
        cr.execute(
            """
        WITH RECURSIVE children AS (
        SELECT bom_id, id
        FROM mrp_bom
        WHERE bom_id IN %s
        UNION ALL
        SELECT a.bom_id, a.id
        FROM mrp_bom a
        JOIN children b ON(a.bom_id = b.id)
        )
        SELECT * FROM children order by bom_id
        """,
            (tuple(ids),),
        )
        res = cr.fetchall()
        for _x, y in res:
            result[y] = True
        return result

    def _get_boms_from_product(self, cr, uid, ids, context=None):
        result = {}
        bom_obj = self.pool.get("mrp.bom")
        for p in ids:
            product_bom_ids = bom_obj.search(cr, uid, [("product_id", "=", p)])
            bom_ids = bom_obj.get_child_boms(cr, uid, product_bom_ids, context=context)
            for bom_id in bom_ids:
                result[bom_id] = True
        return result

    def _is_bom(self, cr, uid, ids, name, arg, context=None):
        result = {}
        if context is None:
            context = {}
        for bom in self.browse(cr, uid, ids, context=context):
            result[bom.id] = False
            if bom.bom_lines:
                result[bom.id] = True
        return result

    def _bom_hierarchy_indent_calc(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        if not ids:
            return []
        res = []
        for bom in self.browse(cr, uid, ids, context=None):
            data = []
            b = bom
            while b:
                if b.name and b.bom_id:
                    data.insert(0, ">")
                else:
                    data.insert(0, "")

                b = b.bom_id
            data = "".join(data)
            res.append((bom.id, data))
        return dict(res)

    def _complete_bom_hierarchy_code_calc(
        self, cr, uid, ids, prop, unknow_none, unknow_dict
    ):
        if not ids:
            return []
        res = []
        for bom in self.browse(cr, uid, ids, context=None):
            data = []
            b = bom
            while b:
                if b.code:
                    data.insert(0, b.code)
                elif b.position:
                    data.insert(0, b.position)
                elif b.product_id.default_code:
                    data.insert(0, b.product_id.default_code)
                else:
                    data.insert(0, "")

                b = b.bom_id
            data = " / ".join(data)
            data = "[" + data + "] "

            res.append((bom.id, data))
        return dict(res)

    def _complete_bom_hierarchy_name_calc(
        self, cr, uid, ids, prop, unknow_none, unknow_dict
    ):
        if not ids:
            return []
        res = []
        for bom in self.browse(cr, uid, ids, context=None):
            data = []
            b = bom
            while b:
                if b.name:
                    data.insert(0, b.name)
                elif b.product_id.name:
                    data.insert(0, b.product_id.name)
                else:
                    data.insert(0, "")

                b = b.bom_id

            data = " / ".join(data)
            res.append((bom.id, data))
        return dict(res)

    def _is_parent(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        for bom in self.browse(cr, uid, ids, context=None):
            if not bom.bom_id:
                res[bom.id] = True
            else:
                res[bom.id] = False
        return res

    def _product_has_own_bom(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        for bom in self.browse(cr, uid, ids, context=None):
            bom_ids = self.pool.get("mrp.bom").search(
                cr,
                uid,
                [("product_id", "=", bom.product_id.id), ("bom_id", "=", False)],
                context=None,
            )
            if bom_ids:
                res[bom.id] = True
            else:
                res[bom.id] = False
        return res

    _columns = {
        "is_parent": fields.function(
            _is_parent,
            string="Is parent BOM",
            type="boolean",
            readonly=True,
            store=True,
        ),
        "has_child": fields.function(
            _is_bom, string="Has components", type="boolean", readonly=True
        ),
        "product_has_own_bom": fields.function(
            _product_has_own_bom,
            string="Product has own BOM",
            type="boolean",
            readonly=True,
        ),
        "bom_hierarchy_indent": fields.function(
            _bom_hierarchy_indent_calc,
            method=True,
            type="char",
            string="Level",
            size=32,
            readonly=True,
        ),
        "complete_bom_hierarchy_code": fields.function(
            _complete_bom_hierarchy_code_calc,
            method=True,
            type="char",
            string="Complete Reference",
            size=250,
            help="Describes the full path of this "
            "component within the BOM hierarchy using the BOM reference.",
            store={
                "mrp.bom": (get_child_boms, ["name", "code", "position", "bom_id"], 20),
                "product.product": (_get_boms_from_product, ["default_code"], 20),
            },
        ),
        "complete_bom_hierarchy_name": fields.function(
            _complete_bom_hierarchy_name_calc,
            method=True,
            type="char",
            string="Complete Name",
            size=250,
            help="Describes the full path of this "
            "component within the BOM hierarchy using the BOM name.",
            store={
                "mrp.bom": (get_child_boms, ["name", "bom_id"], 20),
                "product.product": (_get_boms_from_product, ["name"], 20),
            },
        ),
    }

    _order = "complete_bom_hierarchy_code"

    def action_openChildTreeView(self, cr, uid, ids, context=None):
        """
        :return dict: dictionary value for created view
        """
        if context is None:
            context = {}
        bom = self.browse(cr, uid, ids[0], context)
        child_bom_ids = self.pool.get("mrp.bom").search(
            cr, uid, [("bom_id", "=", bom.id)]
        )
        res = self.pool.get("ir.actions.act_window").for_xml_id(
            cr, uid, "mrp_bom_hierarchy", "action_mrp_bom_hierarchy_tree2", context
        )
        res["context"] = {
            "default_bom_id": bom.id,
        }
        res["domain"] = "[('id', 'in', [" + ",".join(map(str, child_bom_ids)) + "])]"
        res["nodestroy"] = False
        return res

    def action_openParentTreeView(self, cr, uid, ids, context=None):
        """
        :return dict: dictionary value for created view
        """
        if context is None:
            context = {}
        bom = self.browse(cr, uid, ids[0], context)
        res = self.pool.get("ir.actions.act_window").for_xml_id(
            cr, uid, "mrp_bom_hierarchy", "action_mrp_bom_hierarchy_tree2", context
        )
        if bom.bom_id:
            for parent_bom_id in self.pool.get("mrp.bom").search(
                cr, uid, [("id", "=", bom.bom_id.id)]
            ):
                res["domain"] = "[('id','='," + str(parent_bom_id) + ")]"
        res["nodestroy"] = False
        return res

    def action_openProductBOMTreeView(self, cr, uid, ids, context=None):
        """
        :return dict: dictionary value for created view
        """
        if context is None:
            context = {}
        bom = self.browse(cr, uid, ids[0], context)
        product_bom_ids = self.pool.get("mrp.bom").search(
            cr,
            uid,
            [("product_id", "=", bom.product_id.id), ("bom_id", "=", False)],
            context=context,
        )
        res = self.pool.get("ir.actions.act_window").for_xml_id(
            cr, uid, "mrp", "mrp_bom_form_action2", context
        )

        res["context"] = {
            "default_product_id": bom.product_id.id,
        }
        res["domain"] = "[('id', 'in', [" + ",".join(map(str, product_bom_ids)) + "])]"
        res["nodestroy"] = False
        return res
