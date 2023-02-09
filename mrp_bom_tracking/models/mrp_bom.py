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

    def write(self, values):
        bom_line_ids = {}
        if "bom_line_ids" in values:
            for bom in self:
                del_lines = []
                for line in values["bom_line_ids"]:
                    if line[0] == 2:
                        del_lines.append(line[1])
                if del_lines:
                    bom.message_post_with_view(
                        "mrp_bom_tracking.track_bom_template",
                        values={
                            "lines": self.env["mrp.bom.line"].browse(del_lines),
                            "mode": "Removed",
                        },
                        subtype_id=self.env.ref("mail.mt_note").id,
                    )
                bom_line_ids[bom.id] = bom.bom_line_ids
        res = super(MrpBom, self).write(values)
        if "bom_line_ids" in values:
            for bom in self:
                new_lines = bom.bom_line_ids - bom_line_ids[bom.id]
                if new_lines:
                    bom.message_post_with_view(
                        "mrp_bom_tracking.track_bom_template",
                        values={"lines": new_lines, "mode": "New"},
                        subtype_id=self.env.ref("mail.mt_note").id,
                    )
        return res


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    def write(self, values):
        if "product_id" in values:
            for bom in self.mapped("bom_id"):
                lines = self.filtered(lambda l: l.bom_id == bom)
                product_id = values.get("product_id")
                if product_id:
                    product_id = self.env["product.product"].browse(product_id)
                product_id = product_id or lines.product_id
                if lines:
                    bom.message_post_with_view(
                        "mrp_bom_tracking.track_bom_template_2",
                        values={"lines": lines, "product_id": product_id},
                        subtype_id=self.env.ref("mail.mt_note").id,
                    )
        elif "product_qty" in values or "product_uom_id" in values:
            for bom in self.mapped("bom_id"):
                lines = self.filtered(lambda l: l.bom_id == bom)
                if lines:
                    product_qty = values.get("product_qty") or lines.product_qty
                    product_uom_id = values.get("product_uom_id")
                    if product_uom_id:
                        product_uom_id = self.env["uom.uom"].browse(product_uom_id)
                    product_uom_id = product_uom_id or lines.product_uom_id
                    bom.message_post_with_view(
                        "mrp_bom_tracking.track_bom_line_template",
                        values={
                            "lines": lines,
                            "product_qty": product_qty,
                            "product_uom_id": product_uom_id,
                        },
                        subtype_id=self.env.ref("mail.mt_note").id,
                    )
        return super(MrpBomLine, self).write(values)
