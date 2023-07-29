from itertools import tee

from odoo import _, api, fields, models


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


class FinishedProductStructureWizard(models.TransientModel):
    _name = "finished.product.structure.wizard"

    finished_product_id = fields.Many2one(
        comodel_name="product.template",
        domain="[('finished_product', '=', True)]",
        required=True,
    )
    line_ids = fields.One2many(
        comodel_name="finished.product.structure.line", inverse_name="structure_id"
    )
    attribute_ids = fields.Many2many(
        comodel_name="product.attribute", compute="_compute_attribute_ids", store=True
    )
    need_confirmation = fields.Boolean()

    @api.onchange("finished_product_id")
    def _onchange_finished_product_id(self):
        """
        Update attribute and line attributes
        by onchange finished product
        """
        self.line_ids.write({"attribute_ids": [(6, 0, self.attribute_ids.ids)]})
        self.need_confirmation = bool(
            self.finished_product_id.semi_finished_mrp_bom_ids
        )

    @api.depends("finished_product_id")
    def _compute_attribute_ids(self):
        for rec in self:
            rec.attribute_ids = rec.finished_product_id.attribute_line_ids.mapped(
                "attribute_id"
            )

    def _prepare_new_product_templates(self):
        finished_product = self.finished_product_id
        for line in self.line_ids:
            new_product_name = "{} - {}".format(finished_product.name, line.stage_name)
            product_tmpl = line.product_tmpl_id.copy({"name": new_product_name})
            attr_lines = finished_product.attribute_line_ids.filtered(
                lambda pl: pl.attribute_id in line.attribute_ids
            )
            for attr_line in attr_lines:
                attr_line.copy({"product_tmpl_id": product_tmpl.id})
            line.product_tmpl_stage_id = product_tmpl

    def _tmp_product_struct_line(self):
        self.ensure_one()
        return self.env["finished.product.structure.line"].new(
            {
                "stage_name": "{} - Start".format(self.finished_product_id.name),
                "product_tmpl_id": self.finished_product_id,
                "product_tmpl_stage_id": self.finished_product_id,
            }
        )

    def _prepare_bom_by_products(self):
        lines = self._tmp_product_struct_line() | self.line_ids
        vals_list = []
        for bom, line in pairwise(lines):
            vals = {
                "product_tmpl_id": bom.product_tmpl_stage_id.id,
                "type": line.bom_type,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "component_template_id": line.product_tmpl_stage_id.id,
                            "match_on_attribute_ids": [(6, 0, line.attribute_ids.ids)],
                        },
                    )
                ],
            }
            if line.bom_type == "subcontract":
                vals.update(subcontractor_ids=[(6, 0, line.partner_ids.ids)])
            self.finished_product_id.write(
                {
                    "semi_finished_product_tmpl_ids": [
                        (
                            0,
                            0,
                            {
                                "semi_finished_product_tmpl_id": line.product_tmpl_stage_id.id,
                                "attribute_ids": [(6, 0, line.attribute_ids.ids)],
                                "bom_type": line.bom_type,
                                "partner_ids": [(6, 0, line.partner_ids.ids)],
                            },
                        )
                    ]
                }
            )
            vals_list.append(vals)
        return vals_list

    def remove_old_struct(self):
        boms = self.finished_product_id.semi_finished_mrp_bom_ids
        if boms:
            archive_bom_ids = (
                self.env["mrp.production"]
                .search(
                    [
                        ("bom_id", "in", boms.ids),
                        ("state", "not in", ["done", "cancel"]),
                    ]
                )
                .mapped("bom_id")
            )
            (boms - archive_bom_ids).unlink()
            archive_bom_ids.write({"active": False})
        lines = self.finished_product_id.semi_finished_product_tmpl_ids
        if lines:
            products = lines.mapped("semi_finished_product_tmpl_id")
            lines.unlink()
            products.unlink()

    def create_product_struct(self):
        if not self.line_ids:
            raise models.MissingError(
                _("At least one line needs to be added to structure.")
            )
        self.remove_old_struct()
        self._prepare_new_product_templates()
        vals_list = self._prepare_bom_by_products()
        bom_ids = self.env["mrp.bom"].create(vals_list)
        self.finished_product_id.semi_finished_mrp_bom_ids = bom_ids
        return {"type": "ir.actions.act_window_close"}
