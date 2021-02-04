# © 2016 Akretion (http://www.akretion.com)
# David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.base.models.ir_ui_view import transfer_node_to_modifiers


class SubstituteWorkcenter(models.TransientModel):
    _name = "substitute.workcenter"
    _description = "Replace Workcenters from Work Orders by another one"

    workcenter_id = fields.Many2one(
        comodel_name="mrp.workcenter", string="Workcenter", required=True
    )

    def substitute_workcenter(self):
        self.ensure_one()
        MrpProdWorkcLine_m = self.env["mrp.workorder"]
        active_ids = self.env.context.get("active_ids", [])
        vals = {"workcenter_id": self.workcenter_id.id}
        lines = MrpProdWorkcLine_m.browse(active_ids)
        lines.write(vals)
        return True

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if self.env.context.get("active_ids") and view_type == "form":
            parent = False
            for line in self.env["mrp.workorder"].browse(
                self.env.context["active_ids"]
            ):
                if line.state == "done":
                    raise UserError(
                        _("You can't change the workcenter of a done operation")
                    )
                elif not parent:
                    parent = line.workcenter_id.parent_level_1_id
                elif parent != line.workcenter_id.parent_level_1_id:
                    raise UserError(
                        _(
                            "You can only substitute workcenter that share the same "
                            "parent level 1"
                        )
                    )
            root = etree.fromstring(res["arch"])
            field = root.find(".//field[@name='workcenter_id']")
            field.set("domain", "[('parent_level_1_id', '=', %s)]" % parent.id)
            transfer_node_to_modifiers(root, field)
            res["arch"] = etree.tostring(root, pretty_print=True)
        return res
