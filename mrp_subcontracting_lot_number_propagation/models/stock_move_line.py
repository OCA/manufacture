# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from lxml import etree

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.models.ir_ui_view import (
    transfer_modifiers_to_node,
    transfer_node_to_modifiers,
)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    is_lot_id_editable = fields.Boolean(
        string="Is lot editable?",
        compute="_compute_is_lot_id_editable",
        help="Technical field to define if the 'lot_id' field is editable.",
    )

    @api.depends("lot_id")
    def _compute_is_lot_id_editable(self):
        for line in self:
            line.is_lot_id_editable = True
            mos = line.move_id.move_orig_ids.production_id
            lot_prapagated = [
                mo.propagated_lot_producing == line.lot_id.name
                and mo.subcontracting_has_been_recorded
                and mo.is_lot_number_propagated
                for mo in mos
            ]
            if any(lot_prapagated):
                line.is_lot_id_editable = False

    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        # Override to make readonly the "lot_id" field if 'is_lot_editable' is false.
        # This is done this way as it's not possible to update easily existing 'attrs'
        # attributes on all views.
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if "is_lot_id_editable" in result["arch"]:
            result["arch"] = self._fields_view_get_adapt_lot_tags_attrs(result)
        return result

    def _fields_view_get_adapt_lot_tags_attrs(self, view):
        """Set as readonly 'lot_id' field if 'is_lot_editable' is false."""
        doc = etree.XML(view["arch"])
        tags = ("//field[@name='lot_id']",)
        lot_id_readonly_domain = [("is_lot_id_editable", "=", False)]
        for xpath_expr in tags:
            attrs_key = "readonly"
            nodes = doc.xpath(xpath_expr)
            for field in nodes:
                attrs = safe_eval(field.attrib.get("attrs", "{}"))
                if not attrs.get(attrs_key):
                    attrs[attrs_key] = lot_id_readonly_domain
                    continue
                readonly_domain = expression.OR(
                    [attrs[attrs_key], lot_id_readonly_domain]
                )
                attrs[attrs_key] = readonly_domain
                field.set("attrs", str(attrs))
                modifiers = {}
                transfer_node_to_modifiers(field, modifiers, self.env.context)
                transfer_modifiers_to_node(modifiers, field)
        return etree.tostring(doc, encoding="unicode")
