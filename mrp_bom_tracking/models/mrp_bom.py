# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    code = fields.Char(tracking=True)
    product_id = fields.Many2one(tracking=True)
    product_tmpl_id = fields.Many2one(tracking=True)
    product_qty = fields.Float(tracking=True)
    picking_type_id = fields.Many2one(tracking=True)
    type = fields.Selection(tracking=True)
    ready_to_produce = fields.Selection(tracking=True)
    consumption = fields.Selection(tracking=True)
    produce_delay = fields.Integer(tracking=True)
    days_to_prepare_mo = fields.Integer(tracking=True)

    def write(self, values):
        template_env = self.env["ir.ui.view"]
        bom_line_ids = {}
        if "bom_line_ids" in values:
            for bom in self:
                del_lines = []
                for line in values["bom_line_ids"]:
                    if line[0] == 2:
                        del_lines.append(line[1])
                if del_lines:
                    message_body = template_env._render_template(
                        "mrp_bom_tracking.track_bom_template",
                        values={
                            "lines": self.env["mrp.bom.line"].browse(del_lines),
                            "mode": "Removed",
                        },
                    )
                    bom.message_post(
                        body=message_body, subtype_id=self.env.ref("mail.mt_note").id
                    )
                bom_line_ids[bom.id] = bom.bom_line_ids
        res = super().write(values)
        if "bom_line_ids" in values:
            for bom in self:
                new_lines = bom.bom_line_ids - bom_line_ids[bom.id]
                if new_lines:
                    message_body = template_env._render_template(
                        "mrp_bom_tracking.track_bom_template",
                        values={"lines": new_lines, "mode": "New"},
                    )
                    bom.message_post(
                        body=message_body, subtype_id=self.env.ref("mail.mt_note").id
                    )
        return res


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    def write(self, values):
        template_env = self.env["ir.ui.view"]
        if "product_id" in values:
            for bom_line in self:
                bom = bom_line.bom_id
                product_id = values.get("product_id")
                product = self.env["product.product"].browse(product_id)
                if product.exists():
                    message_body = template_env._render_template(
                        "mrp_bom_tracking.track_bom_template_2",
                        values={"lines": bom_line, "product_id": product},
                    )
                    bom.message_post(
                        body=message_body, subtype_id=self.env.ref("mail.mt_note").id
                    )
        elif "product_qty" in values or "product_uom_id" in values:
            for bom_line in self:
                bom = bom_line.bom_id
                product_qty = values.get("product_qty") or bom_line.product_qty
                product_uom_id = values.get("product_uom_id")
                product_uom = None
                if product_uom_id:
                    product_uom = self.env["uom.uom"].browse(product_uom_id)
                product_uom = product_uom or bom_line.product_uom_id
                message_body = template_env._render_template(
                    "mrp_bom_tracking.track_bom_line_template",
                    values={
                        "lines": bom_line,
                        "product_qty": product_qty,
                        "product_uom_id": product_uom,
                    },
                )
                bom.message_post(
                    body=message_body, subtype_id=self.env.ref("mail.mt_note").id
                )
        return super().write(values)
