from odoo import _, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # main action to duplicate product with bom
    def action_duplicate_with_kit(self):
        new_records = self.env["product.template"]
        bom_obj = self.env["mrp.bom"]

        # check for multiple records (action might be initiated in tree view)
        for record in self:
            new_record = record.copy()
            new_records += new_record
            bom_line_vals = []
            for variant in record.product_variant_ids:
                bom_line_vals.append(
                    (
                        0,
                        0,
                        {
                            "product_id": variant.id,
                            "product_qty": 1,
                        },
                    )
                )

            # set kit and variants
            bom = bom_obj.create(
                {
                    "product_tmpl_id": new_record.id,
                    "type": "phantom",
                    "product_qty": 1,
                    "bom_line_ids": bom_line_vals,
                }
            )
            for bom_line in bom.bom_line_ids:
                attribute_value_ids = []
                for (
                    attribute_value
                ) in bom_line.product_id.product_template_attribute_value_ids:
                    temp_val = (
                        bom_line.possible_bom_product_template_attribute_value_ids
                    )
                    for possible_value in temp_val:
                        if attribute_value.name == possible_value.name:
                            attribute_value_ids.append(possible_value.id)
                bom_line.bom_product_template_attribute_value_ids = [
                    (6, 0, attribute_value_ids)
                ]
        name = _("Duplicate Products") if len(new_records) > 1 else (new_records.name)
        view_mode = "tree,form" if len(new_records) > 1 else "form"
        domain = [("id", "in", new_records.ids)] if len(new_records) > 1 else []
        res_id = False if len(new_records) > 1 else new_records.id
        if new_records.ids:
            return {
                "type": "ir.actions.act_window",
                "name": name,
                "view_mode": view_mode,
                "res_model": "product.template",
                "domain": domain,
                "res_id": res_id,
            }
