# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from lxml import etree

from odoo import api, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.models.ir_ui_view import (
    transfer_modifiers_to_node,
    transfer_node_to_modifiers,
)


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def subcontracting_record_component(self):
        if self.is_lot_number_propagated and self.propagated_lot_producing:
            self._create_and_assign_propagated_lot_number()
        return super().subcontracting_record_component()

    def _views_to_adapt(self):
        names = super()._views_to_adapt()
        return names + ["mrp.production.subcontracting.form.view"]

    @api.depends(
        # New field dependencies to compute the propagated lot on the
        # "mrp_production_subcontracting_form_view" view.
        "move_raw_ids.move_line_ids.qty_done",
        "move_raw_ids.move_line_ids.lot_id",
    )
    def _compute_propagated_lot_producing(self):
        return super()._compute_propagated_lot_producing()

    def _fields_view_get_adapt_lot_tags_attrs(self, view):
        arch = super()._fields_view_get_adapt_lot_tags_attrs(view)
        # Remove 'required' on 'lot_producing_id' if it is automatically propagated.
        if view["name"] != "mrp.production.subcontracting.form.view":
            return arch
        doc = etree.XML(arch)
        tags = ("//field[@name='lot_producing_id']",)
        for xpath_expr in tags:
            attrs_key = "required"
            nodes = doc.xpath(xpath_expr)
            for field in nodes:
                attrs = safe_eval(field.attrib.get("attrs", "{}"))
                if not attrs[attrs_key]:
                    continue
                required_domain = expression.AND(
                    [attrs[attrs_key], [("is_lot_number_propagated", "=", False)]]
                )
                attrs[attrs_key] = required_domain
                field.set("attrs", str(attrs))
                modifiers = {}
                transfer_node_to_modifiers(field, modifiers, self.env.context)
                transfer_modifiers_to_node(modifiers, field)
        return etree.tostring(doc, encoding="unicode")
